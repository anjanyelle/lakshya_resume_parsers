"""
Rule-based personal information extractor for resume parsing.
Uses regex patterns and specialized libraries for accurate data extraction.
"""

import re
import logging
from typing import List, Dict, Optional, Union
from datetime import datetime
import phonenumbers
from phonenumbers import NumberParseException
import dateparser
from dateparser import DateDataParser

# Configure logging
logger = logging.getLogger(__name__)


class RuleBasedParser:
    """
    Comprehensive rule-based parser for extracting personal information from resume text.
    Supports emails, phone numbers, social profiles, websites, dates, and skills extraction.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize date parser with common configurations
        self.date_parser = DateDataParser(
            languages=['en'],
            settings={
                'PREFER_DATES_FROM': 'past',
                'DATE_ORDER': 'MDY',
                'RELATIVE_BASE': datetime.now()
            }
        )
        
        # Pre-compiled regex patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for better performance."""
        
        # Email pattern with internationalized domain support
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
            re.IGNORECASE
        )
        
        # LinkedIn URL pattern
        self.linkedin_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9-]+)',
            re.IGNORECASE
        )
        
        # GitHub URL pattern
        self.github_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9-]+)',
            re.IGNORECASE
        )
        
        # General website URL pattern
        self.website_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',
            re.IGNORECASE
        )
        
        # Years of experience pattern
        self.experience_pattern = re.compile(
            r'(\d+(?:\.\d+)?)(?:\+|\s*-\s*\d+)?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)?',
            re.IGNORECASE
        )
    
    def extract_email(self, text: str) -> Optional[str]:
        """
        Extract email address from text using regex pattern.
        
        Args:
            text: Input text to search for email
            
        Returns:
            First email found or None
        """
        try:
            matches = self.email_pattern.findall(text)
            if matches:
                email = matches[0].lower().strip()
                self.logger.debug(f"Found email: {email}")
                return email
            return None
        except Exception as e:
            self.logger.error(f"Error extracting email: {e}")
            return None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """
        Extract phone number using phonenumbers library for international detection.
        Supports US, UK, India, Australia formats.
        
        Args:
            text: Input text to search for phone numbers
            
        Returns:
            E.164 formatted phone number or None
        """
        try:
            # Common countries to try
            country_codes = ['US', 'GB', 'IN', 'AU']
            
            for country_code in country_codes:
                try:
                    # Find all phone numbers in the text
                    for match in phonenumbers.PhoneNumberMatcher(text, country_code):
                        phone_number = match.number
                        
                        # Format to E.164 format
                        formatted_number = phonenumbers.format_number(
                            phone_number, 
                            phonenumbers.PhoneNumberFormat.E164
                        )
                        
                        self.logger.debug(f"Found phone number: {formatted_number}")
                        return formatted_number
                        
                except Exception:
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting phone number: {e}")
            return None
    
    def extract_linkedin(self, text: str) -> Optional[str]:
        """
        Extract LinkedIn profile URL from text.
        
        Args:
            text: Input text to search for LinkedIn URL
            
        Returns:
            LinkedIn URL or None
        """
        try:
            match = self.linkedin_pattern.search(text)
            if match:
                linkedin_url = f"https://linkedin.com/in/{match.group(1)}"
                self.logger.debug(f"Found LinkedIn: {linkedin_url}")
                return linkedin_url
            return None
        except Exception as e:
            self.logger.error(f"Error extracting LinkedIn URL: {e}")
            return None
    
    def extract_github(self, text: str) -> Optional[str]:
        """
        Extract GitHub profile URL from text.
        
        Args:
            text: Input text to search for GitHub URL
            
        Returns:
            GitHub URL or None
        """
        try:
            match = self.github_pattern.search(text)
            if match:
                github_url = f"https://github.com/{match.group(1)}"
                self.logger.debug(f"Found GitHub: {github_url}")
                return github_url
            return None
        except Exception as e:
            self.logger.error(f"Error extracting GitHub URL: {e}")
            return None
    
    def extract_websites(self, text: str) -> List[str]:
        """
        Extract website URLs that are not LinkedIn or GitHub.
        
        Args:
            text: Input text to search for website URLs
            
        Returns:
            List of website URLs
        """
        try:
            websites = []
            
            # Find all URLs
            matches = self.website_pattern.findall(text)
            
            for match in matches:
                url = match.lower().strip()
                
                # Skip LinkedIn and GitHub URLs
                if 'linkedin.com' in url or 'github.com' in url:
                    continue
                
                # Add protocol if missing
                if not url.startswith('http'):
                    url = f"https://{url}"
                
                # Avoid duplicates
                if url not in websites:
                    websites.append(url)
            
            self.logger.debug(f"Found {len(websites)} websites")
            return websites
            
        except Exception as e:
            self.logger.error(f"Error extracting websites: {e}")
            return []
    
    def extract_dates(self, text: str) -> List[Dict[str, Union[str, datetime, None]]]:
        """
        Extract all date mentions using dateparser library.
        
        Args:
            text: Input text to search for dates
            
        Returns:
            List of dictionaries with raw text, parsed datetime, and type
        """
        try:
            dates = []
            
            # Common date patterns to search for
            date_patterns = [
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s*\d{4}\b',
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b',
                r'\b(?:Spring|Summer|Fall|Winter)\s+\d{4}\b',
                r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b'
            ]
            
            # Combine all patterns
            combined_pattern = '|'.join(f'({pattern})' for pattern in date_patterns)
            
            for match in re.finditer(combined_pattern, text, re.IGNORECASE):
                raw_date = match.group(0).strip()
                
                # Check for present/current indicators
                date_type = 'unknown'
                if any(word in raw_date.lower() for word in ['present', 'current', 'now']):
                    dates.append({
                        'raw': raw_date,
                        'parsed': None,
                        'type': 'end'
                    })
                    continue
                
                # Parse the date
                try:
                    parsed_date = dateparser.parse(raw_date)
                    if parsed_date:
                        dates.append({
                            'raw': raw_date,
                            'parsed': parsed_date,
                            'type': 'unknown'
                        })
                except Exception:
                    # If parsing fails, still include the raw date
                    dates.append({
                        'raw': raw_date,
                        'parsed': None,
                        'type': 'unknown'
                    })
            
            self.logger.debug(f"Found {len(dates)} dates")
            return dates
            
        except Exception as e:
            self.logger.error(f"Error extracting dates: {e}")
            return []
    
    def extract_years_of_experience(self, text: str) -> Optional[int]:
        """
        Extract years of experience from text.
        Looks for patterns like '5 years of experience', '3+ years', '2-4 years'.
        
        Args:
            text: Input text to search for experience mentions
            
        Returns:
            Maximum years mentioned or None
        """
        try:
            matches = self.experience_pattern.findall(text)
            
            max_years = None
            
            for match in matches:
                try:
                    years_str = match[0]  # Get the first group (the number)
                    years = float(years_str)
                    
                    # Handle ranges like "2-4 years" by taking the higher number
                    if '-' in match:
                        # This is a range, extract the higher number
                        range_match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', match)
                        if range_match:
                            years = max(float(range_match.group(1)), float(range_match.group(2)))
                    
                    # Update maximum years found
                    if max_years is None or years > max_years:
                        max_years = years
                        
                except ValueError:
                    continue
            
            result = int(max_years) if max_years is not None else None
            if result:
                self.logger.debug(f"Found years of experience: {result}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting years of experience: {e}")
            return None
    
    SKILL_TAXONOMY = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby', 'Kotlin', 'Swift',
        'React', 'React.js', 'Angular', 'Vue', 'Vue.js', 'Next.js', 'Nuxt.js', 'Svelte', 'Ember',
        'Node.js', 'Express', 'FastAPI', 'Django', 'Flask', 'Spring Boot', 'Laravel', 'NestJS',
        'HTML', 'HTML5', 'CSS', 'CSS3', 'Sass', 'SCSS', 'Tailwind CSS', 'Bootstrap', 'Material UI', 'Styled Components',
        'Redux', 'Redux Toolkit', 'Redux Thunk', 'Redux Saga', 'Zustand', 'MobX', 'React Query', 'Context API', 'Recoil',
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'SQLite', 'DynamoDB', 'Cassandra',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Ansible', 'CI/CD', 'Jenkins', 'GitHub Actions',
        'Git', 'GitHub', 'GitLab', 'Bitbucket', 'REST', 'RESTful', 'GraphQL', 'WebSocket', 'gRPC', 'Microservices',
        'Jest', 'Pytest', 'Cypress', 'Selenium', 'React Testing Library', 'Mocha', 'Chai', 'JUnit',
        'Webpack', 'Vite', 'Babel', 'ESLint', 'Prettier', 'npm', 'yarn', 'pnpm',
        'Linux', 'Bash', 'PowerShell', 'Figma', 'Storybook', 'Postman', 'Firebase', 'Supabase',
        'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Scikit-learn', 'NLP', 'Computer Vision',
        'Jira', 'Confluence', 'Agile', 'Scrum', 'Kanban', 'Recharts', 'D3.js', 'Chart.js',
        'Vercel', 'Netlify', 'Heroku', 'DigitalOcean', 'Nginx', 'Apache',
        # ─── Programming Languages ───
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'PHP', 'Ruby',
        'Kotlin', 'Swift', 'Scala', 'Perl', 'Haskell', 'Elixir', 'Erlang', 'Clojure', 'F#', 'R',
        'MATLAB', 'Julia', 'Lua', 'Dart', 'Groovy', 'Objective-C', 'Assembly', 'COBOL', 'Fortran',
        'Ada', 'Prolog', 'Lisp', 'Scheme', 'Racket', 'OCaml', 'Crystal', 'Nim', 'Zig', 'V',
        'Solidity', 'Vyper', 'Move', 'Cairo', 'Ink!', 'Cadence', 'Clarity', 'Michelson',
        'VHDL', 'Verilog', 'SystemVerilog', 'HDL', 'FPGA Programming', 'PLC Programming',
        'ActionScript', 'CoffeeScript', 'LiveScript', 'PureScript', 'ReasonML', 'Elm',
        'Tcl', 'AWK', 'Sed', 'D', 'Modula-2', 'Pascal', 'Delphi', 'Visual Basic', 'VBScript',
        'PowerShell', 'Bash', 'Zsh', 'Fish', 'Ksh', 'Csh', 'Batch Scripting',
        'HCL', 'Jsonnet', 'Dhall', 'Nix', 'Pkl',

        # ─── Frontend Frameworks & Libraries ───
        'React', 'React.js', 'Angular', 'Vue', 'Vue.js', 'Next.js', 'Nuxt.js', 'Svelte', 'SvelteKit',
        'Ember', 'Backbone.js', 'Mithril', 'Preact', 'Inferno', 'Solid.js', 'Qwik', 'Astro',
        'Remix', 'Gatsby', 'Gridsome', 'Eleventy', 'Hugo', 'Jekyll', 'Hexo', 'VuePress',
        'Alpine.js', 'Stimulus', 'Hotwire', 'HTMX', 'Lit', 'Stencil', 'Web Components',
        'Ionic', 'Capacitor', 'Cordova', 'PhoneGap', 'Electron', 'Tauri', 'NW.js',

        # ─── Backend Frameworks ───
        'Node.js', 'Express', 'Express.js', 'Fastify', 'Koa', 'Hapi', 'NestJS', 'AdonisJS',
        'FastAPI', 'Django', 'Flask', 'Pyramid', 'Tornado', 'Sanic', 'Starlette', 'Litestar',
        'Spring Boot', 'Spring MVC', 'Spring Cloud', 'Spring Security', 'Spring Data', 'Micronaut',
        'Quarkus', 'Vert.x', 'Dropwizard', 'Play Framework', 'Ktor',
        'Laravel', 'Symfony', 'CodeIgniter', 'Yii', 'CakePHP', 'Slim', 'Lumen', 'Phalcon',
        'Ruby on Rails', 'Sinatra', 'Hanami', 'Padrino',
        'ASP.NET', 'ASP.NET Core', 'Blazor', 'Minimal API', 'MAUI',
        'Gin', 'Echo', 'Fiber', 'Chi', 'Gorilla Mux', 'Buffalo',
        'Actix', 'Axum', 'Rocket', 'Warp', 'Tide',
        'Phoenix', 'Plug', 'Absinthe', 'Ash Framework',
        'Hono', 'Elysia', 'Bun', 'Deno',

        # ─── CSS & Styling ───
        'HTML', 'HTML5', 'CSS', 'CSS3', 'Sass', 'SCSS', 'Less', 'Stylus',
        'Tailwind CSS', 'Bootstrap', 'Material UI', 'MUI', 'Styled Components',
        'Chakra UI', 'Ant Design', 'Semantic UI', 'Bulma', 'Foundation', 'UIKit',
        'Radix UI', 'shadcn/ui', 'Headless UI', 'DaisyUI', 'Flowbite',
        'Emotion', 'CSS Modules', 'CSS-in-JS', 'Stitches', 'Vanilla Extract',
        'Mantine', 'NextUI', 'PrimeReact', 'PrimeNG', 'PrimeVue', 'Vuetify',
        'Quasar', 'Element UI', 'Element Plus', 'Naive UI', 'Arco Design',
        'TDesign', 'Windi CSS', 'UnoCSS', 'Open Props',
        'Web Animations API', 'GSAP', 'Framer Motion', 'Motion One', 'Anime.js', 'Three.js',
        'Lottie', 'Rive', 'Spline', 'Babylon.js', 'PlayCanvas',

        # ─── State Management ───
        'Redux', 'Redux Toolkit', 'Redux Thunk', 'Redux Saga', 'Redux Observable',
        'Zustand', 'MobX', 'Jotai', 'Recoil', 'Valtio', 'XState', 'Nanostores',
        'React Query', 'TanStack Query', 'SWR', 'Apollo Client', 'Relay',
        'Context API', 'NgRx', 'Akita', 'NGXS', 'Vuex', 'Pinia',
        'Legend State', 'Effector', 'Storeon', 'Nano Stores',

        # ─── Databases – Relational ───
        'SQL', 'MySQL', 'PostgreSQL', 'SQLite', 'MariaDB', 'Oracle Database',
        'Microsoft SQL Server', 'IBM DB2', 'Sybase', 'Teradata', 'Greenplum',
        'CockroachDB', 'YugabyteDB', 'TiDB', 'PlanetScale', 'Neon', 'Supabase',
        'Vercel Postgres', 'SingleStore', 'Citus', 'TimescaleDB',

        # ─── Databases – NoSQL ───
        'MongoDB', 'Redis', 'Elasticsearch', 'DynamoDB', 'Cassandra', 'HBase',
        'CouchDB', 'CouchBase', 'Firebase Firestore', 'Firebase Realtime Database',
        'Neo4j', 'ArangoDB', 'OrientDB', 'JanusGraph', 'Amazon Neptune',
        'InfluxDB', 'Prometheus', 'Victoria Metrics', 'QuestDB', 'Druid',
        'Riak', 'Aerospike', 'ScyllaDB', 'Apache Ignite',
        'Fauna', 'Upstash', 'PocketBase', 'RethinkDB', 'RavenDB',
        'Realm', 'ObjectBox', 'Ditto', 'WatermelonDB', 'LevelDB', 'RocksDB',

        # ─── Search & Vector Databases ───
        'Elasticsearch', 'OpenSearch', 'Solr', 'Algolia', 'Typesense', 'Meilisearch',
        'Pinecone', 'Weaviate', 'Qdrant', 'Milvus', 'Chroma', 'FAISS', 'Annoy',
        'pgvector', 'Redis Vector', 'Vespa', 'Marqo',

        # ─── ORMs & Query Builders ───
        'Hibernate', 'JPA', 'MyBatis', 'JOOQ', 'Flyway', 'Liquibase',
        'SQLAlchemy', 'Tortoise ORM', 'Peewee', 'PonyORM', 'Django ORM',
        'Prisma', 'Drizzle ORM', 'Knex.js', 'Objection.js', 'MikroORM', 'TypeORM', 'Sequelize',
        'Active Record', 'Ecto', 'Diesel', 'SeaORM', 'GORM', 'Ent',
        'Mongoose', 'Typegoose', 'Entity Framework', 'Dapper', 'NHibernate',

        # ─── Cloud Platforms ───
        'AWS', 'Azure', 'GCP', 'Google Cloud', 'Oracle Cloud', 'IBM Cloud',
        'Alibaba Cloud', 'Tencent Cloud', 'Huawei Cloud', 'DigitalOcean',
        'Linode', 'Vultr', 'Hetzner', 'OVH', 'Scaleway',
        'Cloudflare', 'Fastly', 'Akamai', 'Vercel', 'Netlify', 'Render',
        'Railway', 'Fly.io', 'Heroku', 'Back4App', 'Supabase', 'PlanetScale',
        'Neon', 'Turso', 'Upstash', 'Deno Deploy', 'Bun Deploy',

        # ─── AWS Services ───
        'AWS Lambda', 'AWS EC2', 'AWS S3', 'AWS RDS', 'AWS DynamoDB',
        'AWS CloudFormation', 'AWS CDK', 'AWS SAM', 'AWS ECS', 'AWS EKS',
        'AWS Fargate', 'AWS Batch', 'AWS SQS', 'AWS SNS', 'AWS EventBridge',
        'AWS API Gateway', 'AWS AppSync', 'AWS Cognito', 'AWS IAM', 'AWS KMS',
        'AWS Secrets Manager', 'AWS Parameter Store', 'AWS Systems Manager',
        'AWS CloudWatch', 'AWS X-Ray', 'AWS CloudTrail', 'AWS Config',
        'AWS Route53', 'AWS CloudFront', 'AWS WAF', 'AWS Shield',
        'AWS Elastic Beanstalk', 'AWS Lightsail', 'AWS Amplify',
        'AWS Glue', 'AWS Athena', 'AWS EMR', 'AWS Redshift', 'AWS Kinesis',
        'AWS Step Functions', 'AWS AppFlow', 'AWS DataSync', 'AWS Transfer Family',
        'AWS SageMaker', 'AWS Rekognition', 'AWS Comprehend', 'AWS Textract',
        'AWS Polly', 'AWS Transcribe', 'AWS Translate', 'AWS Lex',

        # ─── Azure Services ───
        'Azure Functions', 'Azure App Service', 'Azure Cosmos DB', 'Azure DevOps',
        'Azure Blob Storage', 'Azure SQL Database', 'Azure Service Bus',
        'Azure Event Hub', 'Azure Event Grid', 'Azure Logic Apps',
        'Azure API Management', 'Azure Active Directory', 'Azure AD B2C',
        'Azure Key Vault', 'Azure Monitor', 'Azure Application Insights',
        'Azure Kubernetes Service', 'Azure Container Instances', 'Azure Container Apps',
        'Azure Static Web Apps', 'Azure CDN', 'Azure Front Door',
        'Azure Machine Learning', 'Azure Cognitive Services', 'Azure OpenAI Service',
        'Azure Databricks', 'Azure Synapse Analytics', 'Azure Data Factory',
        'Azure Stream Analytics', 'Azure HDInsight',

        # ─── GCP Services ───
        'Google Cloud Functions', 'Google App Engine', 'Google Cloud Storage', 'BigQuery',
        'Google Cloud Run', 'Google Kubernetes Engine', 'Google Cloud SQL',
        'Google Cloud Spanner', 'Google Cloud Bigtable', 'Google Cloud Firestore',
        'Google Cloud Pub/Sub', 'Google Cloud Tasks', 'Google Cloud Scheduler',
        'Google Cloud IAM', 'Google Cloud KMS', 'Google Cloud Armor',
        'Google Cloud CDN', 'Google Cloud Load Balancing',
        'Vertex AI', 'Google Cloud Vision API', 'Google Natural Language API',
        'Google Cloud Speech-to-Text', 'Google Cloud Text-to-Speech',
        'Google Cloud Translation', 'Google Dialogflow', 'Google Cloud Dataflow',
        'Google Cloud Dataproc', 'Google Cloud Composer', 'Looker',

        # ─── DevOps & Infrastructure ───
        'Docker', 'Docker Compose', 'Docker Swarm', 'Podman', 'Buildah',
        'Kubernetes', 'Helm', 'Kustomize', 'Istio', 'Linkerd', 'Envoy',
        'ArgoCD', 'Flux', 'Spinnaker', 'Harness', 'Tekton',
        'Terraform', 'Pulumi', 'AWS CDK', 'Crossplane', 'OpenTofu',
        'Ansible', 'Chef', 'Puppet', 'SaltStack', 'CFEngine',
        'Vagrant', 'Packer', 'Consul', 'Vault', 'Nomad',
        'Jenkins', 'GitHub Actions', 'GitLab CI', 'CircleCI', 'Travis CI',
        'Bamboo', 'TeamCity', 'Azure Pipelines', 'Bitbucket Pipelines',
        'Drone CI', 'Buildkite', 'Concourse CI', 'Woodpecker CI',
        'Nginx', 'Apache', 'Caddy', 'HAProxy', 'Traefik', 'Kong',
        'CI/CD', 'GitOps', 'Infrastructure as Code', 'Site Reliability Engineering',
        'Platform Engineering', 'FinOps', 'CloudOps', 'AIOps',
        'Prometheus', 'Grafana', 'Alertmanager', 'Loki', 'Tempo', 'Jaeger',
        'Zipkin', 'OpenTelemetry', 'Datadog', 'New Relic', 'Dynatrace',
        'Splunk', 'Elastic Stack', 'ELK Stack', 'EFK Stack',
        'PagerDuty', 'Opsgenie', 'VictorOps', 'StatusPage',
        'Chaos Engineering', 'Chaos Monkey', 'LitmusChaos', 'Gremlin',

        # ─── Version Control & Collaboration ───
        'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Azure Repos', 'AWS CodeCommit',
        'Mercurial', 'SVN', 'Perforce', 'Plastic SCM', 'Fossil',
        'GitHub Copilot', 'GitLab Duo', 'Tabnine', 'Cursor', 'Codeium',
        'Code Review', 'Pull Requests', 'Merge Requests', 'Branch Strategy',
        'Git Flow', 'GitHub Flow', 'Trunk Based Development',

        # ─── API Development ───
        'REST', 'RESTful', 'GraphQL', 'WebSocket', 'gRPC', 'tRPC', 'JSON-RPC',
        'SOAP', 'OData', 'AsyncAPI', 'OpenAPI', 'Swagger', 'Postman', 'Insomnia',
        'API Gateway', 'API Design', 'API Documentation', 'API Testing',
        'API Security', 'OAuth', 'OAuth2', 'JWT', 'SAML', 'OIDC', 'LDAP',
        'API Versioning', 'Rate Limiting', 'Throttling', 'API Monetization',
        'Webhooks', 'Server-Sent Events', 'Long Polling', 'WebRTC',

        # ─── Messaging & Event Streaming ───
        'Kafka', 'Apache Kafka', 'RabbitMQ', 'ActiveMQ', 'NATS', 'NATS JetStream',
        'Redis Pub/Sub', 'Redis Streams', 'AWS SQS', 'AWS SNS', 'AWS Kinesis',
        'Azure Service Bus', 'Azure Event Hub', 'Google Cloud Pub/Sub',
        'Pulsar', 'ZeroMQ', 'MQTT', 'AMQP', 'Stomp',
        'Kafka Streams', 'KSQL', 'Flink', 'Spark Streaming',

        # ─── Testing ───
        'Jest', 'Vitest', 'Mocha', 'Chai', 'Jasmine', 'AVA', 'Tape',
        'Pytest', 'Unittest', 'Nose2', 'Hypothesis', 'Locust',
        'JUnit', 'TestNG', 'Mockito', 'PowerMock', 'AssertJ', 'Hamcrest',
        'NUnit', 'xUnit', 'MSTest', 'SpecFlow', 'FluentAssertions',
        'RSpec', 'Minitest', 'Capybara', 'FactoryBot',
        'Cypress', 'Playwright', 'Selenium', 'WebdriverIO', 'Puppeteer',
        'TestCafe', 'Nightwatch', 'Appium', 'Detox', 'Espresso', 'XCTest',
        'React Testing Library', 'Enzyme', 'Vue Test Utils', 'Angular Testing',
        'Storybook', 'Chromatic', 'Percy', 'BackstopJS', 'Loki',
        'k6', 'JMeter', 'Gatling', 'Artillery', 'Vegeta',
        'SonarQube', 'ESLint', 'Prettier', 'Checkstyle', 'PMD', 'SpotBugs',
        'Codecov', 'Coveralls', 'Istanbul', 'NYC',
        'Test-Driven Development', 'Behavior-Driven Development', 'Acceptance Test-Driven Development',
        'Mutation Testing', 'Property-Based Testing', 'Contract Testing', 'Pact',

        # ─── Build Tools & Package Managers ───
        'Webpack', 'Vite', 'Rollup', 'Parcel', 'esbuild', 'Turbopack', 'Rspack',
        'Babel', 'SWC', 'TypeScript Compiler', 'Flow',
        'npm', 'yarn', 'pnpm', 'Bun', 'Deno',
        'Maven', 'Gradle', 'Ant', 'SBT', 'Mill', 'Bazel',
        'Make', 'CMake', 'Meson', 'Ninja', 'Buck', 'Pants',
        'Cargo', 'Mix', 'Rebar3', 'Poetry', 'PDM', 'Hatch', 'uv',
        'pip', 'conda', 'pipenv', 'virtualenv',
        'NuGet', 'Paket', 'Composer', 'Bundler', 'CocoaPods', 'SPM',
        'Turborepo', 'Nx', 'Lerna', 'Rush', 'Moon',

        # ─── Security ───
        'Application Security', 'Web Application Security', 'API Security',
        'OAuth', 'OAuth2', 'JWT', 'SAML', 'OIDC', 'Kerberos', 'LDAP', 'Active Directory',
        'SSL', 'TLS', 'mTLS', 'PKI', 'Certificates', 'Let\'s Encrypt',
        'OWASP', 'Penetration Testing', 'Vulnerability Assessment', 'Security Auditing',
        'SAST', 'DAST', 'IAST', 'RASP', 'SCA',
        'Snyk', 'Checkmarx', 'Veracode', 'Fortify', 'SonarQube',
        'Nmap', 'Metasploit', 'Burp Suite', 'OWASP ZAP', 'Wireshark',
        'Nessus', 'Qualys', 'Rapid7', 'Tenable',
        'Zero Trust', 'Zero Trust Architecture', 'Privileged Access Management',
        'Identity and Access Management', 'IAM', 'PAM', 'SIEM', 'SOC',
        'Incident Response', 'Threat Modeling', 'Risk Assessment',
        'Cryptography', 'Encryption', 'Hashing', 'Digital Signatures',
        'Key Management', 'Hardware Security Module', 'HSM',
        'DevSecOps', 'Shift Left Security', 'Supply Chain Security',
        'SBOM', 'Compliance', 'GDPR', 'HIPAA', 'PCI DSS', 'SOC 2', 'ISO 27001',
        'Firewall', 'IDS', 'IPS', 'WAF', 'DDoS Protection',
        'Reverse Engineering', 'Malware Analysis', 'Forensics', 'OSINT',
        'Bug Bounty', 'Red Team', 'Blue Team', 'Purple Team', 'CTF',

        # ─── Machine Learning & AI ───
        'Machine Learning', 'Deep Learning', 'Neural Networks', 'AI', 'Artificial Intelligence',
        'TensorFlow', 'PyTorch', 'Keras', 'JAX', 'MXNet', 'Paddle Paddle',
        'Scikit-learn', 'XGBoost', 'LightGBM', 'CatBoost', 'H2O', 'AutoML',
        'NLP', 'Natural Language Processing', 'Computer Vision', 'Speech Recognition',
        'Object Detection', 'Image Segmentation', 'Image Classification',
        'YOLO', 'Detectron2', 'MMDetection', 'Torchvision',
        'Hugging Face', 'Transformers', 'BERT', 'GPT', 'T5', 'RoBERTa',
        'LLM', 'Large Language Models', 'Foundation Models', 'Multimodal AI',
        'LangChain', 'LlamaIndex', 'Semantic Kernel', 'AutoGen', 'CrewAI',
        'OpenAI API', 'Anthropic API', 'Gemini API', 'Cohere API', 'Mistral AI',
        'LLM Fine-Tuning', 'RLHF', 'LoRA', 'QLoRA', 'PEFT', 'DPO',
        'RAG', 'Retrieval-Augmented Generation', 'Agentic AI', 'AI Agents',
        'Prompt Engineering', 'Few-Shot Learning', 'Zero-Shot Learning',
        'Transfer Learning', 'Federated Learning', 'Continual Learning',
        'Reinforcement Learning', 'Q-Learning', 'PPO', 'SAC', 'DDPG',
        'Stable Baselines', 'OpenAI Gym', 'Ray RLlib',
        'Generative AI', 'Diffusion Models', 'GANs', 'VAEs',
        'Stable Diffusion', 'Midjourney API', 'DALL-E', 'ControlNet',
        'MLflow', 'Weights & Biases', 'DVC', 'ClearML', 'Comet ML',
        'Kubeflow', 'MLOps', 'LLMOps', 'Model Monitoring', 'Model Serving',
        'BentoML', 'Seldon', 'KServe', 'TorchServe', 'TFServing', 'Triton',
        'Feature Engineering', 'Feature Store', 'Feast', 'Tecton', 'Hopsworks',
        'Data Preprocessing', 'Data Augmentation', 'Imbalanced Learning',
        'Dimensionality Reduction', 'PCA', 't-SNE', 'UMAP',
        'Clustering', 'Classification', 'Regression', 'Anomaly Detection',
        'Time Series Analysis', 'Forecasting', 'Prophet', 'ARIMA',
        'Recommendation Systems', 'Collaborative Filtering', 'Matrix Factorization',
        'Graph Neural Networks', 'GNN', 'Knowledge Graphs',
        'Explainable AI', 'XAI', 'SHAP', 'LIME', 'Captum',
        'AI Ethics', 'Responsible AI', 'Fairness in AI', 'Bias Detection',
        'Synthetic Data', 'Data Labeling', 'Annotation', 'Label Studio', 'CVAT',
        'OpenCV', 'PIL', 'Pillow', 'scikit-image', 'Albumentations',
        'NLTK', 'spaCy', 'Gensim', 'FastText', 'Sentence Transformers',
        'Speech Recognition', 'Whisper', 'TTS', 'Text-to-Speech',
        'Audio Processing', 'Librosa', 'torchaudio', 'SoundFile',
        'Simulation', 'Digital Twin', 'Isaac Sim', 'Mujoco',

        # ─── Data Engineering & Analytics ───
        'Data Engineering', 'Data Pipelines', 'ETL', 'ELT', 'Data Warehousing',
        'Pandas', 'NumPy', 'Polars', 'Dask', 'Vaex', 'Modin',
        'Matplotlib', 'Seaborn', 'Plotly', 'Bokeh', 'Altair', 'Vega',
        'Tableau', 'Power BI', 'Looker', 'Metabase', 'Superset', 'Redash',
        'Apache Spark', 'Apache Flink', 'Apache Beam', 'Apache Storm',
        'Hadoop', 'HDFS', 'MapReduce', 'Hive', 'HBase', 'Pig', 'Sqoop',
        'Airflow', 'Prefect', 'Dagster', 'Mage', 'Kedro', 'Luigi',
        'dbt', 'Great Expectations', 'Soda', 'Monte Carlo', 'Atlan',
        'Redshift', 'Snowflake', 'BigQuery', 'Databricks', 'Synapse',
        'Delta Lake', 'Apache Iceberg', 'Apache Hudi', 'Apache Parquet',
        'Apache ORC', 'Apache Avro', 'Apache Arrow',
        'Kafka', 'Kinesis', 'Flink', 'Spark Streaming', 'Storm',
        'Data Governance', 'Data Catalog', 'Data Lineage', 'Data Quality',
        'DataOps', 'Analytics Engineering', 'Data Mesh', 'Data Lakehouse',
        'Excel', 'Google Sheets', 'Jupyter Notebook', 'JupyterLab', 'Zeppelin',
        'R Studio', 'KNIME', 'RapidMiner', 'SAS', 'SPSS', 'Stata',
        'Data Modeling', 'Star Schema', 'Snowflake Schema', 'Data Vault',
        'Business Intelligence', 'OLAP', 'OLTP', 'Data Lake', 'Data Lakehouse',

        # ─── Mobile Development ───
        'React Native', 'Flutter', 'Expo', 'NativeScript', 'Xamarin',
        'Android', 'iOS', 'Swift', 'SwiftUI', 'UIKit', 'Objective-C',
        'Kotlin', 'Jetpack Compose', 'Android SDK', 'Android NDK',
        'Cross-Platform Development', 'Hybrid App Development',
        'Mobile App Architecture', 'MVVM', 'MVI', 'MVP', 'MVC',
        'Core Data', 'Core Location', 'ARKit', 'RealityKit', 'SceneKit',
        'Metal', 'SpriteKit', 'GameplayKit', 'Core ML', 'Create ML',
        'Jetpack', 'Room', 'Hilt', 'WorkManager', 'Navigation Component',
        'Firebase', 'OneSignal', 'Braze', 'Amplitude', 'Mixpanel',
        'App Store', 'Google Play', 'TestFlight', 'Fastlane',
        'Mobile Security', 'Certificate Pinning', 'Obfuscation',
        'App Performance', 'ANR', 'Crash Reporting', 'App Analytics',
        'Push Notifications', 'Deep Linking', 'Universal Links',
        'Mobile Payments', 'Apple Pay', 'Google Pay', 'In-App Purchases',
        'Augmented Reality', 'ARCore', 'ARKit', 'Mixed Reality', 'VR Development',

        # ─── Game Development ───
        'Unity', 'Unreal Engine', 'Godot', 'CryEngine', 'GameMaker',
        'C# (Unity)', 'C++ (Unreal)', 'GDScript', 'Lua (Gaming)',
        'OpenGL', 'DirectX', 'Vulkan', 'Metal', 'WebGL', 'WebGPU',
        'Pygame', 'Arcade', 'Raylib', 'SDL', 'SFML', 'LÖVE',
        'Phaser', 'PixiJS', 'BabylonJS', 'PlayCanvas', 'Three.js',
        'Game Design', 'Level Design', 'Game Mechanics', 'Game Economy',
        'Game AI', 'Pathfinding', 'Behavior Trees', 'State Machines',
        'Physics Engines', 'Box2D', 'Bullet Physics', 'Havok', 'NVIDIA PhysX',
        'Animation', 'Rigging', 'Skinning', 'Shader Programming', 'HLSL', 'GLSL',
        'Multiplayer', 'Netcode', 'Game Server', 'ENet', 'Mirror', 'Photon',
        'Steam API', 'Epic Online Services', 'Xbox Live', 'PlayStation Network',
        'Localization', 'Monetization', 'In-App Purchases', 'Ads Integration',
        'Performance Optimization', 'Profiling', 'GPU Optimization',
        'VR Development', 'AR Development', 'XR Development',
        'Blender', 'Maya', '3ds Max', 'Cinema 4D', 'ZBrush', 'Substance Painter',

        # ─── Embedded & Systems ───
        'Embedded Systems', 'RTOS', 'FreeRTOS', 'Zephyr', 'VxWorks', 'QNX',
        'Arduino', 'Raspberry Pi', 'ESP32', 'STM32', 'PIC', 'AVR',
        'C (Embedded)', 'C++ (Embedded)', 'Rust (Embedded)', 'Assembly',
        'UART', 'SPI', 'I2C', 'CAN', 'Modbus', 'Profibus',
        'FPGA', 'VHDL', 'Verilog', 'Xilinx', 'Intel FPGA', 'Lattice',
        'Bare Metal Programming', 'Device Drivers', 'BSP', 'HAL',
        'IoT', 'Internet of Things', 'Edge Computing', 'Fog Computing',
        'MQTT', 'CoAP', 'Zigbee', 'Z-Wave', 'LoRa', 'LoRaWAN', 'Thread',
        'Matter', 'Bluetooth', 'BLE', 'WiFi', 'NFC', 'RFID',
        'Automotive', 'AUTOSAR', 'CAN Bus', 'LIN', 'FlexRay', 'Ethernet AVB',
        'ADAS', 'Functional Safety', 'ISO 26262', 'MISRA C',
        'Industrial IoT', 'SCADA', 'PLC', 'HMI', 'OPC UA',
        'Linux Kernel', 'Linux Device Drivers', 'Yocto', 'Buildroot',
        'Bootloader', 'U-Boot', 'GRUB', 'UEFI', 'BIOS',
        'Memory Management', 'DMA', 'Interrupt Handling', 'Real-Time Systems',

        # ─── Blockchain & Web3 ───
        'Blockchain', 'Web3', 'DeFi', 'NFT', 'DAO', 'DApp', 'Smart Contracts',
        'Solidity', 'Vyper', 'Move', 'Cairo', 'Ink!', 'Rust (Solana)',
        'Ethereum', 'Solana', 'Polygon', 'Avalanche', 'BNB Chain', 'Arbitrum',
        'Optimism', 'Base', 'zkSync', 'StarkNet', 'TON', 'Near', 'Cosmos',
        'Bitcoin', 'Lightning Network', 'Taproot', 'Script',
        'Hardhat', 'Foundry', 'Truffle', 'Brownie', 'Anchor', 'Scaffold-ETH',
        'OpenZeppelin', 'Chainlink', 'The Graph', 'IPFS', 'Arweave', 'Ceramic',
        'ethers.js', 'web3.js', 'viem', 'wagmi', 'RainbowKit', 'ConnectKit',
        'MetaMask', 'WalletConnect', 'Safe', 'Account Abstraction', 'ERC-4337',
        'ERC-20', 'ERC-721', 'ERC-1155', 'ERC-4626', 'EIP-1559',
        'AMM', 'Uniswap', 'Curve', 'Balancer', 'Aave', 'Compound', 'MakerDAO',
        'Layer 2', 'Rollups', 'Optimistic Rollups', 'ZK Rollups', 'State Channels',
        'Consensus Algorithms', 'PoW', 'PoS', 'DPoS', 'BFT', 'Tendermint',
        'Tokenomics', 'Staking', 'Yield Farming', 'Liquidity Mining',
        'Cryptography', 'ZK Proofs', 'zk-SNARKs', 'zk-STARKs', 'MPC', 'TSS',
        'Blockchain Analytics', 'On-Chain Analysis', 'MEV', 'Flash Loans',

        # ─── Architecture & Design Patterns ───
        'Microservices', 'Serverless', 'Event-Driven Architecture',
        'CQRS', 'Event Sourcing', 'Saga Pattern', 'Outbox Pattern',
        'Domain-Driven Design', 'DDD', 'Hexagonal Architecture', 'Clean Architecture',
        'Onion Architecture', 'SOLID Principles', 'Design Patterns', 'GoF Patterns',
        'Monolithic Architecture', 'SOA', 'Service Mesh', 'BFF Pattern',
        'API Gateway Pattern', 'Strangler Fig Pattern', 'Anti-Corruption Layer',
        'Reactive Systems', 'Actor Model', 'CSP', 'Reactive Streams',
        'Repository Pattern', 'Factory Pattern', 'Observer Pattern', 'Strategy Pattern',
        'MVC', 'MVVM', 'MVP', 'MVI', 'Flux', 'Redux Pattern',
        'Database Sharding', 'Read Replicas', 'CQRS', 'Polyglot Persistence',
        'Distributed Systems', 'CAP Theorem', 'Eventual Consistency',
        'Load Balancing', 'Circuit Breaker', 'Bulkhead', 'Retry Pattern',
        'Rate Limiting', 'Throttling', 'Backpressure',
        'High Availability', 'Fault Tolerance', 'Disaster Recovery',
        'Blue-Green Deployment', 'Canary Deployment', 'Feature Flags',
        'Twelve-Factor App', 'Cloud Native', 'Edge Computing',
        'Modular Monolith', 'Micro-Frontend', 'Module Federation',

        # ─── Software Development Methodologies ───
        'Agile', 'Scrum', 'Kanban', 'Lean', 'XP', 'SAFe', 'LeSS', 'Scrum@Scale',
        'Waterfall', 'Spiral', 'RAD', 'Prototyping', 'Incremental Development',
        'Test-Driven Development', 'Behavior-Driven Development', 'Domain-Driven Design',
        'Continuous Integration', 'Continuous Deployment', 'Continuous Delivery',
        'DevOps', 'DevSecOps', 'DataOps', 'MLOps', 'FinOps', 'GitOps',
        'Pair Programming', 'Mob Programming', 'Code Review', 'Refactoring',
        'Technical Debt Management', 'Legacy System Modernization',
        'Trunk Based Development', 'Feature Branch Workflow', 'Release Management',
        'Sprint Planning', 'Backlog Grooming', 'Retrospectives', 'Daily Standup',
        'Sprint Review', 'Velocity', 'Story Points', 'Burn Down Chart',
        'Velocity Chart', 'Cumulative Flow Diagram', 'Cycle Time', 'Lead Time',

        # ─── Project & Product Management ───
        'Product Management', 'Project Management', 'Program Management', 'Portfolio Management',
        'Product Strategy', 'Product Roadmap', 'Product Vision', 'Product Discovery',
        'Product-Led Growth', 'Growth Hacking', 'OKRs', 'KPIs', 'Metrics',
        'A/B Testing', 'Experimentation', 'Feature Prioritization', 'MVP',
        'Product Analytics', 'Cohort Analysis', 'Funnel Analysis', 'Retention',
        'User Research', 'User Interviews', 'Surveys', 'Usability Testing',
        'Competitive Analysis', 'Market Research', 'Go-to-Market Strategy',
        'Roadmapping', 'Story Mapping', 'Impact Mapping', 'Job-to-be-Done',
        'Stakeholder Management', 'Executive Communication', 'Product Metrics',
        'Jira', 'Confluence', 'Asana', 'Trello', 'Monday.com', 'Notion',
        'Linear', 'Height', 'Shortcut', 'ClickUp', 'Basecamp',
        'Figma', 'FigJam', 'Miro', 'Mural', 'Lucidchart', 'Whimsical',
        'PMP', 'PRINCE2', 'PMI', 'Six Sigma', 'ITIL', 'COBIT',
        'Risk Management', 'Change Management', 'Crisis Management',
        'Budget Management', 'Resource Planning', 'Capacity Planning',
        'Vendor Management', 'Contract Management', 'SLA Management',

        # ─── UI/UX Design ───
        'UI Design', 'UX Design', 'Product Design', 'Service Design', 'Design Thinking',
        'Interaction Design', 'Visual Design', 'Information Architecture', 'Content Design',
        'User Research', 'Usability Testing', 'A/B Testing', 'Eye Tracking',
        'Wireframing', 'Prototyping', 'Mockups', 'User Flows', 'Customer Journey Maps',
        'Figma', 'Sketch', 'Adobe XD', 'InVision', 'Zeplin', 'Marvel', 'Axure',
        'Framer', 'Webflow', 'Wix', 'Squarespace', 'Readymag',
        'Adobe Creative Suite', 'Photoshop', 'Illustrator', 'After Effects',
        'InDesign', 'Lightroom', 'Premiere Pro', 'Audition', 'Animate',
        'Affinity Designer', 'Affinity Photo', 'Affinity Publisher',
        'Canva', 'Penpot', 'Lunacy', 'Origami Studio',
        'Design Systems', 'Storybook', 'Chromatic', 'Zeroheight', 'Supernova',
        'Accessibility', 'WCAG', 'ADA Compliance', 'ARIA', 'Screen Readers',
        'Color Theory', 'Typography', 'Grid Systems', 'Responsive Design',
        'Mobile-First Design', 'Dark Mode', 'Micro-interactions',
        'Motion Design', 'Animation', 'Lottie', 'Rive', 'Principle',
        'Brand Design', 'Brand Identity', 'Logo Design', 'Graphic Design',
        'Icon Design', 'Illustration', 'Infographic Design', 'Data Visualization',
        '3D Design', 'Blender', 'Cinema 4D', 'KeyShot', 'Rhino', 'Fusion 360',
        'User Psychology', 'Cognitive Biases', 'Persuasion Design', 'Gamification',
        'Heuristic Evaluation', 'Contextual Inquiry', 'Card Sorting',
        'Tree Testing', 'First Click Testing', 'Preference Testing',

        # ─── Marketing & Growth ───
        'Digital Marketing', 'Content Marketing', 'Social Media Marketing', 'Email Marketing',
        'Influencer Marketing', 'Affiliate Marketing', 'Performance Marketing',
        'SEO', 'Technical SEO', 'On-Page SEO', 'Off-Page SEO', 'Local SEO',
        'SEM', 'PPC', 'Google Ads', 'Facebook Ads', 'Instagram Ads', 'LinkedIn Ads',
        'Twitter Ads', 'TikTok Ads', 'Pinterest Ads', 'Programmatic Advertising',
        'Google Analytics', 'Google Analytics 4', 'Google Tag Manager',
        'Google Search Console', 'Bing Webmaster Tools', 'Google Merchant Center',
        'HubSpot', 'Marketo', 'Pardot', 'Salesforce Marketing Cloud', 'Braze',
        'Mailchimp', 'Klaviyo', 'SendGrid', 'Iterable', 'Customer.io',
        'SEMrush', 'Ahrefs', 'Moz', 'Majestic', 'Screaming Frog',
        'Hotjar', 'FullStory', 'Heap', 'Amplitude', 'Mixpanel',
        'Segment', 'mParticle', 'Rudderstack', 'Snowplow',
        'Conversion Rate Optimization', 'CRO', 'Landing Page Optimization',
        'A/B Testing', 'Multivariate Testing', 'Optimizely', 'VWO', 'LaunchDarkly',
        'Growth Hacking', 'Viral Marketing', 'Referral Programs', 'Product-Led Growth',
        'Copywriting', 'Content Strategy', 'Content Creation', 'Blogging',
        'Video Marketing', 'Podcast Marketing', 'Webinar Marketing',
        'Social Media Management', 'Community Management', 'Community Building',
        'Brand Management', 'Brand Strategy', 'Corporate Communications',
        'Public Relations', 'Media Relations', 'Crisis Communications',
        'Event Marketing', 'Trade Show Marketing', 'Field Marketing',
        'Customer Acquisition', 'Customer Retention', 'Churn Reduction',
        'Lifecycle Marketing', 'CRM', 'Salesforce', 'HubSpot CRM', 'Pipedrive',

        # ─── Sales & Business Development ───
        'Sales', 'B2B Sales', 'B2C Sales', 'SaaS Sales', 'Enterprise Sales',
        'Inside Sales', 'Outside Sales', 'Field Sales', 'Channel Sales',
        'Business Development', 'Partnerships', 'Strategic Alliances',
        'Account Management', 'Key Account Management', 'Customer Success',
        'Sales Development', 'SDR', 'BDR', 'AE', 'Account Executive',
        'Lead Generation', 'Prospecting', 'Cold Calling', 'Cold Emailing',
        'Pipeline Management', 'Sales Forecasting', 'Revenue Operations',
        'Sales Enablement', 'Sales Training', 'Sales Coaching',
        'CRM', 'Salesforce', 'HubSpot', 'Pipedrive', 'ZoomInfo', 'Apollo',
        'Outreach', 'Salesloft', 'Gong', 'Chorus', 'Clari',
        'Contract Negotiation', 'Procurement', 'RFP', 'RFQ', 'SOW',
        'Revenue Recognition', 'Deal Structuring', 'Pricing Strategy',
        'Customer Onboarding', 'Upselling', 'Cross-Selling', 'Expansion Revenue',
        'NPS', 'CSAT', 'Customer Health Score', 'QBR',

        # ─── Finance & Accounting ───
        'Financial Analysis', 'Financial Modeling', 'Valuation', 'DCF Analysis',
        'Financial Reporting', 'Financial Planning', 'Budgeting', 'Forecasting',
        'Accounting', 'Bookkeeping', 'GAAP', 'IFRS', 'Audit', 'Tax',
        'Payroll', 'Accounts Payable', 'Accounts Receivable', 'General Ledger',
        'Cost Accounting', 'Management Accounting', 'Fund Accounting',
        'Investment Analysis', 'Portfolio Management', 'Risk Management',
        'Treasury Management', 'Cash Flow Management', 'Working Capital',
        'QuickBooks', 'Xero', 'NetSuite', 'SAP FI', 'Oracle Financials',
        'Excel', 'Google Sheets', 'Power BI', 'Tableau', 'Bloomberg', 'Refinitiv',
        'FP&A', 'CFO', 'Controllership', 'Internal Audit', 'External Audit',
        'IPO', 'M&A', 'Due Diligence', 'LBO', 'Private Equity', 'Venture Capital',
        'CFA', 'CPA', 'ACCA', 'CA', 'CMA', 'FRM',

        # ─── HR & People Operations ───
        'Human Resources', 'HR Management', 'People Operations', 'Talent Management',
        'Recruiting', 'Talent Acquisition', 'Sourcing', 'Employer Branding',
        'Onboarding', 'Offboarding', 'Employee Experience', 'Engagement',
        'Performance Management', 'Goal Setting', 'OKRs', 'Performance Reviews',
        'Learning & Development', 'Training', 'E-Learning', 'LMS',
        'Compensation & Benefits', 'Total Rewards', 'Equity', 'Stock Options',
        'HRIS', 'Workday', 'SAP HR', 'BambooHR', 'ADP', 'Paychex',
        'Greenhouse', 'Lever', 'Workable', 'SmartRecruiters', 'Jobvite',
        'LinkedIn Recruiter', 'Indeed', 'Glassdoor',
        'Diversity & Inclusion', 'DEI', 'DEIB', 'Culture Building',
        'Employee Relations', 'Labor Relations', 'Employment Law', 'HR Compliance',
        'Workforce Planning', 'Succession Planning', 'Organizational Design',
        'Change Management', 'Culture Transformation', 'Leadership Development',
        'Coaching', 'Mentoring', 'Team Building', 'Conflict Resolution',

        # ─── Leadership & Management ───
        'Leadership', 'Executive Leadership', 'Management', 'Team Management',
        'Engineering Management', 'Product Management', 'People Management',
        'Strategic Planning', 'Operational Excellence', 'Business Strategy',
        'Vision Setting', 'Mission Alignment', 'Culture Building',
        'Decision Making', 'Problem Solving', 'Critical Thinking', 'Systems Thinking',
        'Stakeholder Management', 'Executive Communication', 'Board Reporting',
        'Organizational Leadership', 'Cross-Functional Leadership', 'Influence',
        'Servant Leadership', 'Situational Leadership', 'Transformational Leadership',
        'Emotional Intelligence', 'EQ', 'Self-Awareness', 'Empathy',
        'Conflict Resolution', 'Negotiation', 'Facilitation', 'Mediation',
        'Coaching', 'Mentoring', 'Feedback', 'Performance Management',
        'Delegation', 'Prioritization', 'Time Management', 'Productivity',
        'Meeting Facilitation', 'Workshop Facilitation', 'Retrospectives',
        'Budget Management', 'P&L Management', 'Resource Allocation',

        # ─── Communication & Soft Skills ───
        'Communication', 'Public Speaking', 'Presentation Skills', 'Storytelling',
        'Technical Writing', 'Business Writing', 'Copywriting', 'Editing', 'Proofreading',
        'Documentation', 'API Documentation', 'User Guides', 'Release Notes',
        'Proposal Writing', 'Report Writing', 'Grant Writing', 'White Papers',
        'Active Listening', 'Feedback', 'Constructive Criticism', 'Assertiveness',
        'Interpersonal Skills', 'Relationship Building', 'Networking',
        'Cross-Cultural Communication', 'Remote Communication', 'Async Communication',
        'Slack', 'Microsoft Teams', 'Zoom', 'Google Meet', 'Loom',
        'Notion', 'Confluence', 'Coda', 'Obsidian', 'Roam Research',
        'Research Skills', 'Data Analysis', 'Problem Solving', 'Analytical Thinking',
        'Creativity', 'Innovation', 'Design Thinking', 'Systems Thinking',
        'Attention to Detail', 'Organization', 'Planning', 'Execution',
        'Adaptability', 'Resilience', 'Growth Mindset', 'Continuous Learning',
        'Collaboration', 'Teamwork', 'Team Player', 'Cross-Functional Collaboration',
        'Customer Focus', 'User Empathy', 'Customer Obsession',
        'Ownership', 'Accountability', 'Initiative', 'Proactiveness',
        'Curiosity', 'Intellectual Humility', 'Openness to Feedback',

        # ─── Education & Teaching ───
        'Teaching', 'Instruction', 'Curriculum Development', 'Course Design',
        'E-Learning Development', 'Instructional Design', 'LMS Administration',
        'Moodle', 'Canvas', 'Blackboard', 'Google Classroom', 'Kahoot', 'Quizlet',
        'Mentoring', 'Coaching', 'Tutoring', 'Academic Advising',
        'Classroom Management', 'Student Assessment', 'Grading',
        'STEM Education', 'Coding Education', 'Bootcamp Instruction',
        'Workshop Facilitation', 'Webinar Hosting', 'Online Teaching',
        'Bloom\'s Taxonomy', 'Constructivism', 'Flipped Classroom',

        # ─── Legal & Compliance ───
        'Contract Law', 'Corporate Law', 'Intellectual Property', 'Patent Law',
        'Trademark', 'Copyright', 'Trade Secret', 'Licensing',
        'Employment Law', 'Labor Law', 'GDPR', 'CCPA', 'HIPAA', 'PCI DSS',
        'SOC 2', 'ISO 27001', 'ISO 9001', 'ISO 14001', 'CMMI',
        'Regulatory Compliance', 'Risk & Compliance', 'GRC', 'AML', 'KYC',
        'Privacy Law', 'Data Protection', 'Data Governance',
        'Legal Research', 'Contract Drafting', 'Contract Negotiation',
        'Litigation Support', 'Legal Operations', 'CLM',

        # ─── Operations & Supply Chain ───
        'Operations Management', 'Supply Chain Management', 'Logistics',
        'Inventory Management', 'Demand Forecasting', 'Procurement',
        'Vendor Management', 'Supplier Relations', 'Sourcing', 'Category Management',
        'Warehouse Management', 'Distribution', 'Last-Mile Delivery',
        'ERP', 'SAP', 'Oracle ERP', 'NetSuite', 'Microsoft Dynamics',
        'Lean Manufacturing', 'Six Sigma', 'Kaizen', 'Kanban', '5S', 'TPM',
        'Quality Management', 'QA', 'QC', 'ISO 9001', 'FMEA', 'SPC',
        'Process Improvement', 'Business Process Management', 'BPM',
        'Robotic Process Automation', 'RPA', 'UiPath', 'Automation Anywhere', 'Blue Prism',

        # ─── Healthcare & Life Sciences ───
        'Healthcare IT', 'EHR', 'EMR', 'HL7', 'FHIR', 'DICOM',
        'Health Informatics', 'Clinical Data Management', 'Pharmacovigilance',
        'Clinical Trials', 'GCP', 'GLP', 'GMP', 'FDA Regulations', 'CE Marking',
        'Medical Devices', 'IVD', 'SaMD', 'ISO 13485', 'IEC 62304',
        'Genomics', 'Bioinformatics', 'NGS', 'CRISPR', 'Drug Discovery',
        'Pathology', 'Radiology', 'Telemedicine', 'Digital Health',
        'HIPAA', 'Healthcare Compliance', 'Patient Data Privacy',

        # ─── Science & Research ───
        'Research Design', 'Scientific Writing', 'Literature Review', 'Meta-Analysis',
        'Quantitative Research', 'Qualitative Research', 'Mixed Methods',
        'Statistical Analysis', 'Biostatistics', 'Econometrics', 'Psychometrics',
        'SPSS', 'SAS', 'R', 'Stata', 'MATLAB', 'Python (Research)',
        'Lab Techniques', 'PCR', 'ELISA', 'Western Blot', 'Cell Culture',
        'Flow Cytometry', 'Microscopy', 'Spectroscopy', 'Chromatography',
        'Physics', 'Chemistry', 'Biology', 'Neuroscience', 'Psychology',
        'Environmental Science', 'Climate Science', 'Geology', 'Astronomy',
        'Grant Writing', 'Ethics Approval', 'IRB', 'Peer Review',

        # ─── Customer Support ───
        'Customer Support', 'Technical Support', 'Customer Service',
        'Help Desk', 'ITSM', 'ServiceNow', 'Zendesk', 'Freshdesk',
        'Intercom', 'Drift', 'Front', 'Kustomer', 'Gladly',
        'JIRA Service Management', 'Confluence', 'Knowledge Base Management',
        'Ticketing Systems', 'SLA Management', 'Escalation Management',
        'Customer Onboarding', 'Customer Training', 'Customer Education',
        'Technical Account Management', 'Solutions Engineering',
        'Pre-Sales', 'Post-Sales', 'Professional Services',

        # ─── Languages ───
        'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
        'Dutch', 'Swedish', 'Norwegian', 'Danish', 'Finnish', 'Russian',
        'Polish', 'Czech', 'Hungarian', 'Romanian', 'Turkish', 'Greek',
        'Arabic', 'Hebrew', 'Farsi', 'Urdu', 'Hindi', 'Bengali', 'Tamil',
        'Telugu', 'Kannada', 'Marathi', 'Gujarati', 'Punjabi', 'Malayalam',
        'Chinese (Mandarin)', 'Chinese (Cantonese)', 'Japanese', 'Korean',
        'Vietnamese', 'Thai', 'Indonesian', 'Malay', 'Tagalog',
        'Swahili', 'Zulu', 'Afrikaans',
        'Translation', 'Localization', 'Interpretation',

        # ─── Miscellaneous Technical ───
        'Linux', 'Ubuntu', 'Debian', 'CentOS', 'RHEL', 'Fedora', 'Arch Linux',
        'macOS', 'Windows Server', 'Active Directory', 'Group Policy',
        'Networking', 'TCP/IP', 'DNS', 'DHCP', 'HTTP', 'HTTPS', 'FTP', 'SSH',
        'VPN', 'SD-WAN', 'BGP', 'OSPF', 'Cisco', 'Juniper', 'Palo Alto',
        'Network Security', 'Firewall Management', 'Zero Trust Network',
        'Virtual Machines', 'VMware', 'VirtualBox', 'Hyper-V', 'KVM',
        'Storage', 'SAN', 'NAS', 'NFS', 'iSCSI', 'Ceph', 'GlusterFS',
        'Backup & Recovery', 'BCP', 'DR', 'RTO', 'RPO',
        'Monitoring', 'Observability', 'Logging', 'Tracing', 'Metrics',
        'Performance Tuning', 'Query Optimization', 'Profiling', 'Benchmarking',
        'Technical Documentation', 'System Design', 'Technical Architecture',
        'Whiteboarding', 'System Design Interviews', 'Coding Interviews',

        # ─── Emerging Technologies ───
        'Quantum Computing', 'Quantum Algorithms', 'Qiskit', 'Cirq', 'Q#',
        'Edge AI', 'TinyML', 'ONNX', 'OpenVINO', 'TensorRT', 'NVIDIA Jetson',
        'Digital Twin', 'Simulation', 'Metaverse', 'Extended Reality', 'XR',
        'Virtual Reality', 'VR', 'Augmented Reality', 'AR', 'Mixed Reality', 'MR',
        'Spatial Computing', 'Apple Vision Pro', 'Meta Quest', 'HoloLens',
        '5G', '6G', 'Edge Computing', 'Fog Computing', 'MEC',
        'Autonomous Systems', 'Robotics', 'ROS', 'ROS2', 'SLAM', 'Autonomous Driving',
        'Drone Development', 'UAV', 'UAS', 'FPV',
        'Synthetic Biology', 'Biotech', 'Nanotech', 'Advanced Materials',
        'Space Tech', 'Satellite Systems', 'CubeSat', 'LoRa', 'SDR',
        'Neuromorphic Computing', 'Photonic Computing', 'DNA Computing',
    ]

    def extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from text using the built-in skill taxonomy.
        No external taxonomy list required.
        """
        return self.extract_skills_from_list(text, self.SKILL_TAXONOMY)

    def extract_skills_from_list(self, text: str, skill_taxonomy: List[str]) -> List[str]:
        """
        Extract skills from text using case-insensitive matching with known skills taxonomy.
        Handles compound skills like 'Node.js', 'React.js', 'C++', '.NET'.
        
        Args:
            text: Input text to search for skills
            skill_taxonomy: List of known skills to match against
            
        Returns:
            Sorted list of matched skills
        """
        try:
            found_skills = set()
            text_lower = text.lower()
            
            for skill in skill_taxonomy:
                if not skill or not skill.strip():
                    continue
                
                skill_lower = skill.lower().strip()
                
                # Handle compound skills with special characters
                # Escape special regex characters in skill names
                escaped_skill = re.escape(skill_lower)
                
                # Create pattern that matches whole words or compound skills
                pattern = r'\b' + escaped_skill + r'\b'
                
                # For compound skills with dots, also match without dots
                if '.' in skill_lower:
                    skill_without_dots = skill_lower.replace('.', '')
                    escaped_without_dots = re.escape(skill_without_dots)
                    pattern += r'|\b' + escaped_without_dots + r'\b'
                
                if re.search(pattern, text_lower):
                    found_skills.add(skill.strip())
            
            # Convert to sorted list
            result = sorted(list(found_skills))
            
            self.logger.debug(f"Found {len(result)} skills: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting skills: {e}")
            return []
    
    def extract_name(self, text: str) -> Optional[str]:
        """
        Extract candidate name from resume text.
        Looks for a proper name in the first few lines.
        
        Args:
            text: Input text to search for name
            
        Returns:
            First line that appears to be a name or None
        """
        for line in text.strip().splitlines()[:5]:
            line = line.strip()
            words = line.split()
            if 1 <= len(words) <= 5 and line.replace(' ', '').replace('-', '').replace("'", "").isalpha():
                return line
        return None
    
    def extract_all_contact_info(self, text: str) -> Dict[str, Union[str, List[str], None]]:
        """
        Extract all contact information in one call.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with all contact information
        """
        return {
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'linkedin': self.extract_linkedin(text),
            'github': self.extract_github(text),
            'websites': self.extract_websites(text)
        }
    
    def extract_all_temporal_info(self, text: str) -> Dict[str, Union[List, int, None]]:
        """
        Extract all temporal information in one call.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with dates and experience information
        """
        return {
            'dates': self.extract_dates(text),
            'years_of_experience': self.extract_years_of_experience(text)
        }


# Example usage and testing
if __name__ == "__main__":
    # Sample text for testing
    sample_text = """
    John Doe
    Email: john.doe@example.com
    Phone: +1-555-555-5555
    LinkedIn: https://www.linkedin.com/in/johndoe
    GitHub: https://github.com/johndoe
    Website: https://johndoe.com
    
    Experience:
    - Senior Software Engineer at Tech Corp (Jan 2020 - Present)
    - 5+ years of experience in software development
    - 2-3 years of experience with Python
    
    Skills: Python, JavaScript, Node.js, React.js, C++, .NET, SQL
    """
    
    parser = RuleBasedParser()
    
    # Test contact extraction
    contact_info = parser.extract_all_contact_info(sample_text)
    print("Contact Info:", contact_info)
    
    # Test temporal extraction
    temporal_info = parser.extract_all_temporal_info(sample_text)
    print("Temporal Info:", temporal_info)
    
    # Test skills extraction
    skills = ['Python', 'JavaScript', 'Node.js', 'React.js', 'C++', '.NET', 'SQL', 'Java']
    found_skills = parser.extract_skills_from_list(sample_text, skills)
    print("Found Skills:", found_skills)
