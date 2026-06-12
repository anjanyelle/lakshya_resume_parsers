#!/usr/bin/env python3
"""
Detailed NER Model Testing with Accuracy Metrics
Tests the model and compares against expected entities
"""

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import json
from pathlib import Path
from typing import List, Dict, Set
from colorama import init, Fore, Style

init(autoreset=True)

class DetailedNERTester:
    def __init__(self, model_path: str):
        """Initialize the NER model tester"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"🤖 LOADING TRAINED NER MODEL")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        self.model_path = Path(model_path)
        
        # Load label mappings
        label_map_path = self.model_path / "label_mappings.json"
        with open(label_map_path, 'r') as f:
            mappings = json.load(f)
            self.id2label = {int(k): v for k, v in mappings['id2label'].items()}
            self.label2id = mappings['label2id']
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
        self.model = AutoModelForTokenClassification.from_pretrained(str(self.model_path))
        
        # Set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        
        print(f"✅ Model loaded successfully")
        print(f"📊 Labels: {len(self.id2label)}")
        print(f"💻 Device: {self.device}")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract entities from text"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
            return_offsets_mapping=True
        )
        
        offset_mapping = inputs.pop("offset_mapping")[0]
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)[0]
        
        entities = []
        current_entity = None
        
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        
        for idx, (token, pred_id, offset) in enumerate(zip(tokens, predictions, offset_mapping)):
            if token in ['[CLS]', '[SEP]', '<s>', '</s>', '<pad>']:
                continue
            
            label = self.id2label[pred_id.item()]
            
            if label == 'O':
                if current_entity:
                    entities.append(current_entity)
                    current_entity = None
                continue
            
            if label.startswith('B-'):
                if current_entity:
                    entities.append(current_entity)
                
                entity_type = label[2:]
                start, end = offset
                current_entity = {
                    'type': entity_type,
                    'text': text[start:end],
                    'start': int(start),
                    'end': int(end),
                    'confidence': torch.softmax(outputs.logits[0][idx], dim=0)[pred_id].item()
                }
            
            elif label.startswith('I-') and current_entity:
                entity_type = label[2:]
                if entity_type == current_entity['type']:
                    start, end = offset
                    current_entity['end'] = int(end)
                    current_entity['text'] = text[current_entity['start']:current_entity['end']]
        
        if current_entity:
            entities.append(current_entity)
        
        return entities
    
    def compare_with_expected(self, extracted: List[Dict], expected: List[Dict]) -> Dict:
        """Compare extracted entities with expected entities"""
        
        # Convert to sets for comparison
        extracted_set = {(e['type'], e['text'].strip().lower()) for e in extracted}
        expected_set = {(e['type'], e['text'].strip().lower()) for e in expected}
        
        # Calculate metrics
        true_positives = extracted_set & expected_set
        false_positives = extracted_set - expected_set
        false_negatives = expected_set - extracted_set
        
        precision = len(true_positives) / len(extracted_set) if extracted_set else 0
        recall = len(true_positives) / len(expected_set) if expected_set else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'extracted_count': len(extracted_set),
            'expected_count': len(expected_set)
        }
    
    def display_comparison(self, text: str, extracted: List[Dict], expected: List[Dict], title: str):
        """Display detailed comparison"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"🧪 TEST: {title}")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}📝 TEXT:{Style.RESET_ALL}")
        print(f"{text}\n")
        
        metrics = self.compare_with_expected(extracted, expected)
        
        # Display metrics
        print(f"{Fore.YELLOW}📊 METRICS:{Style.RESET_ALL}")
        print(f"  Precision: {Fore.GREEN if metrics['precision'] > 0.8 else Fore.YELLOW if metrics['precision'] > 0.5 else Fore.RED}{metrics['precision']:.2%}{Style.RESET_ALL}")
        print(f"  Recall:    {Fore.GREEN if metrics['recall'] > 0.8 else Fore.YELLOW if metrics['recall'] > 0.5 else Fore.RED}{metrics['recall']:.2%}{Style.RESET_ALL}")
        print(f"  F1 Score:  {Fore.GREEN if metrics['f1'] > 0.8 else Fore.YELLOW if metrics['f1'] > 0.5 else Fore.RED}{metrics['f1']:.2%}{Style.RESET_ALL}")
        print(f"  Extracted: {metrics['extracted_count']} | Expected: {metrics['expected_count']}\n")
        
        # Display true positives
        if metrics['true_positives']:
            print(f"{Fore.GREEN}✅ CORRECT EXTRACTIONS ({len(metrics['true_positives'])}):{Style.RESET_ALL}")
            for entity_type, text in sorted(metrics['true_positives']):
                print(f"  • [{entity_type}] {text}")
            print()
        
        # Display false positives
        if metrics['false_positives']:
            print(f"{Fore.RED}❌ INCORRECT EXTRACTIONS ({len(metrics['false_positives'])}):{Style.RESET_ALL}")
            for entity_type, text in sorted(metrics['false_positives']):
                print(f"  • [{entity_type}] {text}")
            print()
        
        # Display false negatives
        if metrics['false_negatives']:
            print(f"{Fore.YELLOW}⚠️  MISSED ENTITIES ({len(metrics['false_negatives'])}):{Style.RESET_ALL}")
            for entity_type, text in sorted(metrics['false_negatives']):
                print(f"  • [{entity_type}] {text}")
            print()
        
        return metrics


def main():
    """Main testing function"""
    
    MODEL_PATH = "models/resume-ner-deberta"
    
    tester = DetailedNERTester(MODEL_PATH)
    
    print(f"{Fore.MAGENTA}{'='*70}")
    print(f"🚀 COMPREHENSIVE MODEL PERFORMANCE TEST")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    all_metrics = []
    
    # Test Case 1: Work Experience
    test1_text = """
    Sarah Johnson worked as a Senior Data Scientist at Microsoft from January 2020 to December 2022 
    in Seattle, Washington. She led the Azure ML team and worked with enterprise clients including 
    Amazon and Google.
    """
    
    test1_expected = [
        {'type': 'PERSON_NAME', 'text': 'Sarah Johnson'},
        {'type': 'ROLE', 'text': 'Senior Data Scientist'},
        {'type': 'COMPANY', 'text': 'Microsoft'},
        {'type': 'DATE_START', 'text': 'January 2020'},
        {'type': 'DATE_END', 'text': 'December 2022'},
        {'type': 'LOCATION', 'text': 'Seattle, Washington'},
        {'type': 'CLIENT', 'text': 'Amazon'},
        {'type': 'CLIENT', 'text': 'Google'},
    ]
    
    extracted1 = tester.extract_entities(test1_text)
    metrics1 = tester.display_comparison(test1_text, extracted1, test1_expected, "Work Experience")
    all_metrics.append(metrics1)
    
    # Test Case 2: Education
    test2_text = """
    Michael Chen completed his Master of Science in Computer Science from Stanford University 
    from September 2019 to June 2021 with a GPA of 3.95. He earned his Bachelor of Technology 
    in Information Technology from MIT from August 2015 to May 2019 with a grade of 3.8.
    """
    
    test2_expected = [
        {'type': 'PERSON_NAME', 'text': 'Michael Chen'},
        {'type': 'DEGREE', 'text': 'Master of Science'},
        {'type': 'FIELD', 'text': 'Computer Science'},
        {'type': 'INSTITUTION', 'text': 'Stanford University'},
        {'type': 'EDU_YEAR_START', 'text': 'September 2019'},
        {'type': 'EDU_YEAR_END', 'text': 'June 2021'},
        {'type': 'GRADE', 'text': '3.95'},
        {'type': 'DEGREE', 'text': 'Bachelor of Technology'},
        {'type': 'FIELD', 'text': 'Information Technology'},
        {'type': 'INSTITUTION', 'text': 'MIT'},
        {'type': 'EDU_YEAR_START', 'text': 'August 2015'},
        {'type': 'EDU_YEAR_END', 'text': 'May 2019'},
        {'type': 'GRADE', 'text': '3.8'},
    ]
    
    extracted2 = tester.extract_entities(test2_text)
    metrics2 = tester.display_comparison(test2_text, extracted2, test2_expected, "Education Background")
    all_metrics.append(metrics2)
    
    # Test Case 3: Multiple Roles
    test3_text = """
    David Kim served as a Product Manager at Google from March 2021 to present in Mountain View. 
    Previously, he was a Software Engineer at Facebook from June 2018 to February 2021 in Menlo Park, 
    working on the Instagram platform for clients worldwide.
    """
    
    test3_expected = [
        {'type': 'PERSON_NAME', 'text': 'David Kim'},
        {'type': 'ROLE', 'text': 'Product Manager'},
        {'type': 'COMPANY', 'text': 'Google'},
        {'type': 'DATE_START', 'text': 'March 2021'},
        {'type': 'LOCATION', 'text': 'Mountain View'},
        {'type': 'ROLE', 'text': 'Software Engineer'},
        {'type': 'COMPANY', 'text': 'Facebook'},
        {'type': 'DATE_START', 'text': 'June 2018'},
        {'type': 'DATE_END', 'text': 'February 2021'},
        {'type': 'LOCATION', 'text': 'Menlo Park'},
    ]
    
    extracted3 = tester.extract_entities(test3_text)
    metrics3 = tester.display_comparison(test3_text, extracted3, test3_expected, "Multiple Roles")
    all_metrics.append(metrics3)
    
    # Test Case 4: Consulting Experience
    test4_text = """
    Emily Rodriguez worked as a Management Consultant at McKinsey & Company from January 2019 
    to August 2022 in New York. She delivered strategic projects for Fortune 500 clients including 
    JPMorgan Chase and Goldman Sachs.
    """
    
    test4_expected = [
        {'type': 'PERSON_NAME', 'text': 'Emily Rodriguez'},
        {'type': 'ROLE', 'text': 'Management Consultant'},
        {'type': 'COMPANY', 'text': 'McKinsey & Company'},
        {'type': 'DATE_START', 'text': 'January 2019'},
        {'type': 'DATE_END', 'text': 'August 2022'},
        {'type': 'LOCATION', 'text': 'New York'},
        {'type': 'CLIENT', 'text': 'JPMorgan Chase'},
        {'type': 'CLIENT', 'text': 'Goldman Sachs'},
    ]
    
    extracted4 = tester.extract_entities(test4_text)
    metrics4 = tester.display_comparison(test4_text, extracted4, test4_expected, "Consulting Experience")
    all_metrics.append(metrics4)
    
    # Overall Summary
    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"📈 OVERALL PERFORMANCE SUMMARY")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    avg_precision = sum(m['precision'] for m in all_metrics) / len(all_metrics)
    avg_recall = sum(m['recall'] for m in all_metrics) / len(all_metrics)
    avg_f1 = sum(m['f1'] for m in all_metrics) / len(all_metrics)
    
    print(f"Tests Run: {len(all_metrics)}")
    print(f"Average Precision: {Fore.GREEN if avg_precision > 0.8 else Fore.YELLOW if avg_precision > 0.5 else Fore.RED}{avg_precision:.2%}{Style.RESET_ALL}")
    print(f"Average Recall:    {Fore.GREEN if avg_recall > 0.8 else Fore.YELLOW if avg_recall > 0.5 else Fore.RED}{avg_recall:.2%}{Style.RESET_ALL}")
    print(f"Average F1 Score:  {Fore.GREEN if avg_f1 > 0.8 else Fore.YELLOW if avg_f1 > 0.5 else Fore.RED}{avg_f1:.2%}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}📊 Model Training F1: 66.92%{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}🎯 Target F1: 98.5-99%{Style.RESET_ALL}\n")
    
    print(f"{Fore.MAGENTA}💡 RECOMMENDATIONS:{Style.RESET_ALL}")
    if avg_f1 < 0.7:
        print(f"  • Model performance is below expectations")
        print(f"  • Consider adding more diverse training examples")
        print(f"  • Review and improve label quality in training data")
        print(f"  • Try training for more epochs or adjusting hyperparameters")
    elif avg_f1 < 0.85:
        print(f"  • Model shows moderate performance")
        print(f"  • Fine-tune on domain-specific examples")
        print(f"  • Add more edge cases to training data")
    else:
        print(f"  • Model performing well!")
        print(f"  • Continue monitoring on production data")
    
    print(f"\n{Fore.GREEN}{'='*70}{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
