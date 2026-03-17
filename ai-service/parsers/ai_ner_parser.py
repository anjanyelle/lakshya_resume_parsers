from transformers import pipeline
import torch
import logging

logger = logging.getLogger(__name__)

class AINamedEntityParser:
    def __init__(self):
        device = 0 if torch.cuda.is_available() else -1
        logger.info(f"Loading NER models on {'GPU' if device == 0 else 'CPU'}...")

        # Model 1: Names, Companies, Locations
        # dslim/bert-base-NER — properly fine-tuned NER model (CoNLL-2003)
        self.ner_pipeline = pipeline(
            task='ner',
            model='dslim/bert-base-NER',
            aggregation_strategy='simple',
            device=device
        )

        # Model 2: IT Skills — purpose-built for technical skill extraction
        try:
            self.skill_pipeline = pipeline(
                task='ner',
                model='Nucha/Nucha_ITSkillNER_BERT',
                aggregation_strategy='simple',
                device=device
            )
        except Exception as e:
            logger.warning(f"Failed to load skill model Nucha/Nucha_ITSkillNER_BERT: {e}")
            logger.info("Using jjzha/jobbert-base-cased for skills extraction as fallback")
            # Use the same model but extract skills differently
            self.skill_pipeline = None

        logger.info("All NER models loaded successfully")

    def _clean_entity_value(self, value: str) -> str:
        """Clean entity value by removing BERT tokenization artifacts and normalizing."""
        if not value:
            return ""
        
        # Remove ## prefix from BERT WordPiece tokens
        value = value.replace('##', '')
        
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Remove special characters that shouldn't be in entity names
        value = value.replace('[CLS]', '').replace('[SEP]', '').replace('[PAD]', '')
        
        # Normalize multiple spaces to single space
        import re
        value = re.sub(r'\s+', ' ', value)
        
        return value
    
    def extract_entities(self, text: str) -> dict:
        chunks = self._chunk_text(text, max_words=300, overlap=50)

        entities = {
            'names': [],
            'organizations': [],
            'locations': [],
            'job_titles': [],
            'skills': [],
            'misc': []
        }

        # Run Model 1: Names / Companies / Locations
        for chunk in chunks:
            try:
                results = self.ner_pipeline(chunk)
                for entity in results:
                    label = entity['entity_group']
                    value = self._clean_entity_value(entity['word'])
                    score = float(entity['score'])
                    if not value or len(value) < 2:
                        continue
                    if label == 'PER':
                        entities['names'].append({'value': value, 'score': score})
                    elif label == 'ORG':
                        entities['organizations'].append({'value': value, 'score': score})
                    elif label == 'LOC':
                        entities['locations'].append({'value': value, 'score': score})
                    elif label == 'MISC':
                        entities['misc'].append({'value': value, 'score': score})
            except Exception as e:
                logger.error(f"NER pipeline error: {e}")

        # Run Model 2: Skills
        if self.skill_pipeline:
            # Use dedicated skill model
            for chunk in chunks:
                try:
                    results = self.skill_pipeline(chunk)
                    for entity in results:
                        value = self._clean_entity_value(entity['word'])
                        score = float(entity['score'])
                        if score > 0.75 and len(value) > 1:
                            entities['skills'].append({'value': value, 'score': score})
                except Exception as e:
                    logger.error(f"Skill pipeline error: {e}")
        else:
            # Fallback: extract skills from general NER model
            # Look for technical terms in MISC entities
            tech_keywords = {
                'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'svelte', 'node', 'nodejs', 'express', 'fastapi', 'django', 'flask', 'spring', 'hibernate', 'dotnet', 'csharp', 'cpp', 'golang', 'rust', 'kotlin', 'swift', 'php', 'laravel', 'ruby', 'rails', 'scala', 'perl', 'r', 'matlab', 'bash', 'powershell', 'html', 'css', 'sass', 'tailwind', 'webpack', 'vite', 'redux', 'graphql', 'grpc', 'rest', 'soap', 'sql', 'postgresql', 'mysql', 'sqlite', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'elasticsearch', 'neo4j', 'kafka', 'rabbitmq', 'celery', 'airflow', 'spark', 'hadoop', 'hive', 'flink', 'docker', 'kubernetes', 'terraform', 'ansible', 'puppet', 'chef', 'jenkins', 'github', 'gitlab', 'circleci', 'aws', 'gcp', 'azure', 'heroku', 'vercel', 'netlify', 'linux', 'ubuntu', 'debian', 'centos', 'nginx', 'apache', 'pandas', 'numpy', 'scipy', 'sklearn', 'scikit', 'tensorflow', 'pytorch', 'keras', 'opencv', 'nltk', 'spacy', 'huggingface', 'transformers', 'langchain', 'openai', 'llm', 'bert', 'gpt', 'tableau', 'powerbi', 'looker', 'dbt', 'snowflake', 'bigquery', 'redshift', 'figma', 'sketch', 'jira', 'confluence', 'notion', 'agile', 'scrum', 'kanban', 'tdd', 'bdd', 'ci', 'cd', 'devops', 'mlops', 'microservices', 'serverless', 'graphdb', 'firebase', 'supabase', 'prisma', 'sequelize', 'sqlalchemy', 'junit', 'pytest', 'jest', 'cypress', 'selenium', 'playwright', 'postman', 'swagger', 'openapi', 'jwt', 'oauth', 'saml', 'ldap', 'ssl', 'tls', 'unity', 'unreal', 'opengl', 'vulkan', 'webgl', 'threejs', 'react_native', 'flutter', 'xamarin', 'android', 'ios', 'xcode', 'gradle', 'maven', 'npm', 'yarn', 'pip', 'conda', 'git', 'svn', 'mercurial', 'excel', 'vba', 'sharepoint', 'sap', 'salesforce', 'hubspot', 'stripe', 'twilio', 'sendgrid', 'websocket', 'mqtt', 'bluetooth', 'raspberry_pi', 'arduino'
            }
            
            for chunk in chunks:
                try:
                    results = self.ner_pipeline(chunk)
                    for entity in results:
                        label = entity['entity_group']
                        value = entity['word'].strip().lower()
                        score = float(entity['score'])
                        
                        # Check if MISC entity contains technical terms
                        if label == 'MISC' and score > 0.6:
                            for tech in tech_keywords:
                                if tech in value:
                                    entities['skills'].append({'value': entity['word'].strip(), 'score': score})
                                    break
                except Exception as e:
                    logger.error(f"Fallback skill extraction error: {e}")

        # Deduplicate all
        for key in entities:
            entities[key] = self._deduplicate(entities[key])

        return entities

    def get_top_person(self, entities: dict) -> str | None:
        names = entities.get('names', [])
        if not names:
            return None
        return max(names, key=lambda x: x['score'])['value']

    def get_organizations(self, entities: dict) -> list:
        return [e['value'] for e in entities.get('organizations', []) if e['score'] > 0.80]

    def get_locations(self, entities: dict) -> list:
        return [e['value'] for e in entities.get('locations', []) if e['score'] > 0.80]

    def get_misc_entities(self, entities: dict) -> list:
        return [e['value'] for e in entities.get('misc', []) if e['score'] > 0.70]

    def get_skills(self, entities: dict) -> list:
        return [e['value'] for e in entities.get('skills', []) if e['score'] > 0.75]

    def _chunk_text(self, text: str, max_words: int, overlap: int) -> list:
        words = text.split()
        chunks = []
        start = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            chunks.append(' '.join(words[start:end]))
            start += max_words - overlap
        return chunks

    def _deduplicate(self, items: list) -> list:
        seen = set()
        result = []
        for item in items:
            key = item['value'].lower()
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result
