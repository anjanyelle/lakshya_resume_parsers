#!/usr/bin/env python3
"""
Test NER Model Performance with Real Resume Examples
Loads the trained model and tests entity extraction on sample resume text
"""

import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
import json
from pathlib import Path
from typing import List, Dict, Tuple
from colorama import init, Fore, Back, Style

# Initialize colorama for colored output
init(autoreset=True)

# Entity color mapping for visualization
ENTITY_COLORS = {
    'PERSON_NAME': Fore.CYAN + Style.BRIGHT,
    'COMPANY': Fore.GREEN + Style.BRIGHT,
    'CLIENT': Fore.MAGENTA + Style.BRIGHT,
    'ROLE': Fore.YELLOW + Style.BRIGHT,
    'LOCATION': Fore.BLUE + Style.BRIGHT,
    'DATE_START': Fore.RED,
    'DATE_END': Fore.RED,
    'DEGREE': Fore.LIGHTCYAN_EX,
    'FIELD': Fore.LIGHTGREEN_EX,
    'FEILD': Fore.LIGHTGREEN_EX,
    'INSTITUTION': Fore.LIGHTMAGENTA_EX,
    'EDU_YEAR_START': Fore.LIGHTRED_EX,
    'EDU_YEAR_END': Fore.LIGHTRED_EX,
    'GRADE': Fore.LIGHTYELLOW_EX,
}

class NERModelTester:
    def __init__(self, model_path: str):
        """Initialize the NER model tester"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"🤖 LOADING NER MODEL")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        self.model_path = Path(model_path)
        
        # Load label mappings
        label_map_path = self.model_path / "label_mappings.json"
        with open(label_map_path, 'r') as f:
            mappings = json.load(f)
            self.id2label = {int(k): v for k, v in mappings['id2label'].items()}
            self.label2id = mappings['label2id']
        
        print(f"📋 Loaded {len(self.id2label)} entity labels")
        
        # Load tokenizer and model
        print(f"🔤 Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
        
        print(f"🧠 Loading model...")
        self.model = AutoModelForTokenClassification.from_pretrained(str(self.model_path))
        
        # Set device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        
        print(f"✅ Model loaded on: {self.device}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract entities from text"""
        # Tokenize
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
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)[0]
        
        # Convert predictions to entities
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
            
            # Parse B-/I- prefix
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
    
    def visualize_entities(self, text: str, entities: List[Dict]):
        """Visualize extracted entities with colors"""
        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"📝 ORIGINAL TEXT")
        print(f"{'='*60}{Style.RESET_ALL}")
        print(f"{text}\n")
        
        print(f"{Fore.YELLOW}{'='*60}")
        print(f"🎯 EXTRACTED ENTITIES ({len(entities)} found)")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            entity_type = entity['type']
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        # Display grouped entities
        for entity_type in sorted(entities_by_type.keys()):
            color = ENTITY_COLORS.get(entity_type, Fore.WHITE)
            print(f"{color}▶ {entity_type}:{Style.RESET_ALL}")
            for entity in entities_by_type[entity_type]:
                conf_color = Fore.GREEN if entity['confidence'] > 0.9 else Fore.YELLOW if entity['confidence'] > 0.7 else Fore.RED
                print(f"  • {color}{entity['text']}{Style.RESET_ALL} {conf_color}({entity['confidence']:.2%}){Style.RESET_ALL}")
            print()
        
        # Visualize in context
        print(f"{Fore.YELLOW}{'='*60}")
        print(f"🌈 HIGHLIGHTED TEXT")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        # Sort entities by start position
        sorted_entities = sorted(entities, key=lambda x: x['start'])
        
        highlighted = ""
        last_end = 0
        
        for entity in sorted_entities:
            # Add text before entity
            highlighted += text[last_end:entity['start']]
            
            # Add colored entity
            color = ENTITY_COLORS.get(entity['type'], Fore.WHITE)
            highlighted += f"{color}{Back.BLACK}{entity['text']}{Style.RESET_ALL}"
            
            last_end = entity['end']
        
        # Add remaining text
        highlighted += text[last_end:]
        
        print(highlighted)
        print()
    
    def test_resume(self, resume_text: str, title: str = "Resume Test"):
        """Test model on a resume sample"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"🧪 TEST: {title}")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        entities = self.extract_entities(resume_text)
        self.visualize_entities(resume_text, entities)
        
        return entities


def main():
    """Main testing function"""
    
    # Model path - update this to your model location
    MODEL_PATH = "models/resume-ner-deberta"
    
    # Initialize tester
    tester = NERModelTester(MODEL_PATH)
    
    # Test samples
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"🚀 STARTING MODEL PERFORMANCE TESTS")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    # Sample 1: Work Experience
    sample1 = """
    John Smith worked as a Senior Software Engineer at Google from January 2020 to December 2022 in Mountain View, California. 
    He led development for the Search team and worked with clients like YouTube and Gmail.
    """
    tester.test_resume(sample1, "Sample 1: Work Experience")
    
    # Sample 2: Education
    sample2 = """
    Sarah Johnson completed her Master of Science in Computer Science from Stanford University 
    from September 2018 to June 2020 with a GPA of 3.9. She previously earned a Bachelor of Technology 
    in Information Technology from MIT from 2014 to 2018.
    """
    tester.test_resume(sample2, "Sample 2: Education")
    
    # Sample 3: Complex Resume Section
    sample3 = """
    Michael Chen, a Data Scientist at Amazon Web Services, worked on machine learning projects 
    from March 2021 to present in Seattle, Washington. He collaborated with the AWS AI team 
    and delivered solutions for enterprise clients including Microsoft and IBM. Prior to this, 
    he was a Research Analyst at Facebook from June 2019 to February 2021 in Menlo Park.
    """
    tester.test_resume(sample3, "Sample 3: Complex Work History")
    
    # Sample 4: Multiple Roles
    sample4 = """
    Emily Rodriguez served as Project Manager at Accenture from January 2020 to August 2022 in New York. 
    She managed consulting projects for Fortune 500 clients. Before that, she was a Business Analyst 
    at Deloitte from July 2017 to December 2019 in Chicago, working with retail and healthcare clients.
    """
    tester.test_resume(sample4, "Sample 4: Multiple Roles")
    
    # Sample 5: Education with Multiple Degrees
    sample5 = """
    David Kim holds a PhD in Artificial Intelligence from Carnegie Mellon University (2019-2023) 
    with a dissertation on deep learning. He completed his Master of Engineering in Computer Science 
    from UC Berkeley (2017-2019) with distinction, and Bachelor of Science in Mathematics from 
    UCLA (2013-2017) with honors.
    """
    tester.test_resume(sample5, "Sample 5: Multiple Degrees")
    
    # Summary
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"✅ ALL TESTS COMPLETED")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}💡 Tips for interpreting results:{Style.RESET_ALL}")
    print(f"  • Green confidence (>90%): High confidence predictions")
    print(f"  • Yellow confidence (70-90%): Medium confidence predictions")
    print(f"  • Red confidence (<70%): Low confidence predictions")
    print(f"\n{Fore.YELLOW}📊 Your model achieved F1: 66.92%{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}🎯 Target F1 was: 98.5-99%{Style.RESET_ALL}")
    print(f"\n{Fore.MAGENTA}💭 Note: Lower F1 suggests the model may need:{Style.RESET_ALL}")
    print(f"  • More diverse training data")
    print(f"  • Better data quality/labeling")
    print(f"  • Longer training or different hyperparameters")
    print()


if __name__ == "__main__":
    main()
