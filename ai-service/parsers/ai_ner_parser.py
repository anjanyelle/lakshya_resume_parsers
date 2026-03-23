from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch

class AINamedEntityParser:
    def __init__(self):
        MODEL_NAME = "jjzha/jobbert-base-cased"
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)
        device = 0 if torch.cuda.is_available() else -1
        self.ner_pipeline = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",
            device=device,
        )

    def extract_entities(self, text: str) -> dict:
        if not text or len(text.strip()) < 10:
            return {'names': [], 'companies': [], 'locations': [], 'skills': [], 'titles': []}

        max_length = 400
        words = text.split()
        chunks = [
            ' '.join(words[i:i + max_length])
            for i in range(0, len(words), max_length)
        ]

        all_entities = []
        for chunk in chunks:
            try:
                entities = self.ner_pipeline(chunk)
                all_entities.extend(entities)
            except Exception as e:
                print(f"NER chunk failed: {e}")
                continue

        result = {'names': [], 'companies': [], 'locations': [], 'skills': [], 'titles': []}

        for ent in all_entities:
            word = ent.get('word', '').strip()
            label = ent.get('entity_group', ent.get('entity', '')).upper()
            score = ent.get('score', 0)
            if score < 0.80 or not word or len(word) < 2:
                continue
            if 'PER' in label or 'NAME' in label:
                result['names'].append(word)
            elif 'ORG' in label or 'COMP' in label:
                result['companies'].append(word)
            elif 'LOC' in label or 'LOCATION' in label:
                result['locations'].append(word)
            elif 'SKILL' in label or 'TECH' in label:
                result['skills'].append(word)
            elif 'TITLE' in label or 'ROLE' in label:
                result['titles'].append(word)

        for key in result:
            result[key] = list(dict.fromkeys(result[key]))

        return result
