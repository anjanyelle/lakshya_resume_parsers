from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import spacy
    from spacy.matcher import PhraseMatcher
except Exception:  # noqa: BLE001
    spacy = None
    PhraseMatcher = None

from app.services.parser.work_experience_parser import JobEntry

logger = logging.getLogger(__name__)


def clean_text_for_skills(text: str) -> str:
    """Normalize text before skill extraction: collapse whitespace, normalize bullets to comma, newlines to comma (one continuous stream)."""
    if not text or not isinstance(text, str):
        return ""
    t = re.sub(r"\s+", " ", text.strip())
    t = re.sub(r"[•▪\-*]\s*", ",", t)
    t = t.replace("\n", ",").replace("\r", ",")
    t = re.sub(r",+", ",", t).strip(",").strip()
    return t


# Standalone noise words to drop when they appear as whole tokens (e.g. "Learn", "based", "models").
SKILL_NOISE_WORDS = frozenset({"learn", "based", "models"})


def clean_skill_text_for_section(text: str) -> str:
    """Enterprise-grade cleaning for the technical skills section only.
    Handles parentheses (GCP (Cloud storage, Bigquery) -> GCP, Cloud storage, Bigquery),
    removes trailing ), replaces & and / with comma, drops standalone noise words."""
    if not text or not isinstance(text, str):
        return ""
    t = text.replace("\u2022", ",").replace("•", ",").replace("▪", ",")
    t = re.sub(r"[\-*]\s+", ",", t)
    t = t.replace("\n", ",").replace("\r", ",")
    t = re.sub(r"\(", ",", t)
    t = re.sub(r"\)", "", t)
    t = re.sub(r"&", ",", t)
    t = re.sub(r"/", ",", t)
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r",+", ",", t).strip(" ,")
    # Standalone noise words (learn, based, models) are dropped in tokenize_skills_by_comma so "Scikit-Learn" stays
    return t


def tokenize_skills_by_comma(text: str) -> list[str]:
    """Split only by comma (no space/newline split). Use after clean_skill_text_for_section."""
    if not text or not isinstance(text, str):
        return []
    parts = [s.strip() for s in text.split(",") if s.strip()]
    return [p for p in parts if len(p) > 1 and p.lower() not in SKILL_NOISE_WORDS]


def strip_skill_token(token: str) -> str:
    """Remove leading/trailing brackets and parentheses from a single skill token."""
    if not token or not isinstance(token, str):
        return token
    return token.strip(" \t()[]\"'").strip()


# Only these explicit words set proficiency; no inference from verbs like "developed"/"built". no inference from verbs like "developed"/"built".
EXPLICIT_PROFICIENCY_KEYWORDS = {
    "expert": "expert",
    "mastery": "expert",
    "master": "expert",
    "advanced": "advanced",
    "proficient": "advanced",
    "intermediate": "intermediate",
    "beginner": "beginner",
    "familiar": "beginner",
    "knowledge": "intermediate",
    "exposure": "beginner",
    "basic": "beginner",
}

# Version pattern: 11g, 10g, 2014, 5.6, 10.x, 9.6
VERSION_PATTERN = re.compile(r"\b(\d+(?:\.\d+)?[a-zA-Z]*)\b")

RELATED_SKILLS = {
    # Frontend Frameworks
    "react": ["javascript", "html", "css", "jsx", "redux", "hooks"],
    "angular": ["javascript", "typescript", "html", "css", "rxjs"],
    "vue": ["javascript", "html", "css", "vuex"],
    "next.js": ["react", "javascript", "node.js", "ssr"],
    "svelte": ["javascript", "html", "css"],
    
    # Backend Frameworks
    "node.js": ["javascript", "express", "npm"],
    "express": ["node.js", "javascript"],
    "django": ["python", "orm", "mvc"],
    "flask": ["python", "web development"],
    "spring boot": ["java", "spring", "mvc"],
    "fastapi": ["python", "async", "rest api"],
    "nest.js": ["node.js", "typescript", "express"],
    
    # Programming Languages
    "typescript": ["javascript"],
    "javascript": ["html", "css"],
    "python": ["programming"],
    "java": ["programming", "oop"],
    "c#": ["programming", ".net", "oop"],
    "go": ["programming", "backend"],
    "rust": ["programming", "systems programming"],
    "kotlin": ["java", "android"],
    "swift": ["ios", "xcode"],
    
    # Cloud Platforms
    "aws": ["cloud", "devops", "ec2", "s3", "lambda"],
    "azure": ["cloud", "devops", "microsoft"],
    "gcp": ["cloud", "devops", "google cloud"],
    "heroku": ["cloud", "paas"],
    "digitalocean": ["cloud", "vps"],
    
    # Databases
    "mongodb": ["nosql", "database", "json"],
    "postgresql": ["sql", "database", "relational"],
    "mysql": ["sql", "database", "relational"],
    "redis": ["cache", "nosql", "in-memory"],
    "elasticsearch": ["search", "nosql", "indexing"],
    "dynamodb": ["nosql", "aws", "database"],
    "cassandra": ["nosql", "distributed database"],
    "oracle": ["sql", "database", "enterprise"],
    
    # DevOps & Tools
    "docker": ["containerization", "devops", "deployment"],
    "kubernetes": ["docker", "container orchestration", "devops"],
    "jenkins": ["ci/cd", "devops", "automation"],
    "gitlab ci": ["ci/cd", "devops", "git"],
    "github actions": ["ci/cd", "devops", "git"],
    "terraform": ["infrastructure as code", "devops", "cloud"],
    "ansible": ["configuration management", "devops", "automation"],
    
    # Version Control
    "git": ["version control", "github", "gitlab"],
    "github": ["git", "version control"],
    "gitlab": ["git", "version control", "ci/cd"],
    
    # Mobile Development
    "react native": ["react", "javascript", "mobile", "ios", "android"],
    "flutter": ["dart", "mobile", "cross-platform"],
    "android": ["java", "kotlin", "mobile"],
    "ios": ["swift", "objective-c", "xcode"],
    
    # Testing
    "jest": ["javascript", "testing", "unit testing"],
    "pytest": ["python", "testing", "unit testing"],
    "selenium": ["testing", "automation", "web testing"],
    "cypress": ["javascript", "testing", "e2e testing"],
    "junit": ["java", "testing", "unit testing"],
    
    # Data & ML
    "tensorflow": ["machine learning", "python", "deep learning"],
    "pytorch": ["machine learning", "python", "deep learning"],
    "scikit-learn": ["machine learning", "python", "data science"],
    "pandas": ["python", "data analysis", "data science"],
    "numpy": ["python", "numerical computing", "data science"],
    "spark": ["big data", "distributed computing", "data processing"],
    "hadoop": ["big data", "distributed computing", "mapreduce"],
    
    # Web Technologies
    "html": ["web development", "frontend"],
    "css": ["web development", "frontend", "styling"],
    "sass": ["css", "preprocessing", "styling"],
    "graphql": ["api", "query language", "rest"],
    "rest api": ["api", "web services", "http"],
    "websocket": ["real-time", "web communication"],
    
    # Message Queues
    "rabbitmq": ["message queue", "amqp", "messaging"],
    "kafka": ["message queue", "streaming", "distributed"],
    "redis": ["cache", "message queue", "pub/sub"],
    
    # Monitoring & Logging
    "prometheus": ["monitoring", "metrics", "devops"],
    "grafana": ["monitoring", "visualization", "dashboards"],
    "elk": ["elasticsearch", "logging", "kibana"],
    "datadog": ["monitoring", "apm", "logging"],
    "newrelic": ["monitoring", "apm", "performance"],
}



SOFT_SKILLS = {
    # Communication Skills
    "communication",
    "verbal communication",
    "written communication",
    "presentation",
    "public speaking",
    "articulation",
    "active listening",
    "interpersonal skills",
    "negotiation",
    "persuasion",
    "storytelling",
    "technical writing",
    "documentation",
    
    # Teamwork & Collaboration
    "teamwork",
    "collaboration",
    "cross-functional collaboration",
    "team player",
    "cooperation",
    "relationship building",
    "networking",
    "cultural awareness",
    "diversity and inclusion",
    "empathy",
    "conflict resolution",
    
    # Leadership & Management
    "leadership",
    "team leadership",
    "people management",
    "mentoring",
    "coaching",
    "delegation",
    "motivation",
    "influence",
    "decision making",
    "strategic thinking",
    "vision",
    "accountability",
    "ownership",
    "stakeholder management",
    "change management",
    "project leadership",
    
    # Problem Solving & Critical Thinking
    "problem solving",
    "problem-solving",
    "critical thinking",
    "analytical thinking",
    "analytical skills",
    "troubleshooting",
    "innovation",
    "creative thinking",
    "creativity",
    "research",
    "data-driven decision making",
    "root cause analysis",
    
    # Time & Project Management
    "time management",
    "project management",
    "organization",
    "organizational skills",
    "planning",
    "prioritization",
    "multitasking",
    "task management",
    "meeting deadlines",
    "efficiency",
    "productivity",
    "attention to detail",
    "detail-oriented",
    
    # Adaptability & Learning
    "adaptability",
    "flexibility",
    "resilience",
    "learning agility",
    "continuous learning",
    "self-learning",
    "growth mindset",
    "open-mindedness",
    "curiosity",
    "quick learner",
    "versatility",
    
    # Work Ethic & Professionalism
    "work ethic",
    "professionalism",
    "reliability",
    "dependability",
    "integrity",
    "honesty",
    "dedication",
    "commitment",
    "self-motivation",
    "initiative",
    "proactive",
    "self-starter",
    "driven",
    "passionate",
    "excellence",
    
    # Customer & Client Focus
    "customer service",
    "client management",
    "customer focus",
    "client relations",
    "user empathy",
    "customer satisfaction",
    
    # Business & Strategic Skills
    "business acumen",
    "strategic planning",
    "business strategy",
    "market analysis",
    "competitive analysis",
    "budgeting",
    "financial acumen",
    "roi optimization",
    "risk management",
    "vendor management",
    
    # Technical Soft Skills
    "technical leadership",
    "code review",
    "pair programming",
    "agile methodology",
    "scrum",
    "kanban",
    "sprint planning",
    "retrospectives",
    "requirement gathering",
    "system design",
    "architecture design",
    
    # Additional Qualities
    "patience",
    "positivity",
    "enthusiasm",
    "confidence",
    "humility",
    "emotional intelligence",
    "stress management",
    "work-life balance",
}


SKILL_ALIASES: dict[str, str] = {
    # React variations
    "reactjs": "react",
    "react.js": "react",
    "react js": "react",
    "react-js": "react",
    
    # Node.js variations
    "nodejs": "node.js",
    "node js": "node.js",
    "node-js": "node.js",
    "node": "node.js",
    
    # TypeScript variations
    "ts": "typescript",
    "type script": "typescript",
    
    # JavaScript variations
    "js": "javascript",
    "java script": "javascript",
    "ecmascript": "javascript",
    "es6": "javascript",
    "es2015": "javascript",
    
    # Python variations
    "py": "python",
    "python3": "python",
    "python2": "python",
    
    # Angular variations
    "angularjs": "angular",
    "angular.js": "angular",
    "angular js": "angular",
    
    # Vue variations
    "vuejs": "vue",
    "vue.js": "vue",
    "vue js": "vue",
    
    # Next.js variations
    "nextjs": "next.js",
    "next js": "next.js",
    
    # Express variations
    "expressjs": "express",
    "express.js": "express",
    "express js": "express",
    
    # MongoDB variations
    "mongo": "mongodb",
    "mongo db": "mongodb",
    
    # PostgreSQL variations
    "postgres": "postgresql",
    "psql": "postgresql",
    "postgre": "postgresql",
    
    # MySQL variations
    "my sql": "mysql",
    "my-sql": "mysql",
    
    # AWS variations
    "amazon web services": "aws",
    "amazon aws": "aws",
    
    # Azure variations
    "microsoft azure": "azure",
    "ms azure": "azure",
    
    # GCP variations
    "google cloud platform": "gcp",
    "google cloud": "gcp",
    
    # Docker variations
    "docker container": "docker",
    "docker-compose": "docker",
    
    # Kubernetes variations
    "k8s": "kubernetes",
    "k8": "kubernetes",
    "kube": "kubernetes",
    
    # Git variations
    "version control": "git",
    "git scm": "git",
    
    # GitHub variations
    "github.com": "github",
    "gh": "github",
    
    # GitLab variations
    "gitlab.com": "gitlab",
    "git lab": "gitlab",
    
    # CI/CD variations
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "cicd": "ci/cd",
    
    # REST API variations
    "rest": "rest api",
    "restful": "rest api",
    "restful api": "rest api",
    "rest-api": "rest api",
    
    # GraphQL variations
    "graph ql": "graphql",
    "graphql api": "graphql",
    
    # HTML variations
    "html5": "html",
    "html 5": "html",
    
    # CSS variations
    "css3": "css",
    "css 3": "css",
    "cascading style sheets": "css",
    
    # SASS variations
    "scss": "sass",
    "sass/scss": "sass",
    
    # Redux variations
    "redux.js": "redux",
    "reduxjs": "redux",
    
    # TensorFlow variations
    "tf": "tensorflow",
    "tensor flow": "tensorflow",
    
    # PyTorch variations
    "torch": "pytorch",
    "py torch": "pytorch",
    
    # Machine Learning variations
    "ml": "machine learning",
    "machine-learning": "machine learning",
    
    # Deep Learning variations
    "dl": "deep learning",
    "deep-learning": "deep learning",
    
    # Artificial Intelligence variations
    "ai": "artificial intelligence",
    "a.i.": "artificial intelligence",
    
    # Natural Language Processing variations
    "nlp": "natural language processing",
    "natural language": "natural language processing",
    
    # Computer Vision variations
    "cv": "computer vision",
    
    # Data Science variations
    "ds": "data science",
    "data-science": "data science",
    
    # SQL variations
    "structured query language": "sql",
    "sequel": "sql",
    
    # NoSQL variations
    "nosql": "nosql",
    "no-sql": "nosql",
    "non-sql": "nosql",
    
    # Java variations
    "java se": "java",
    "java ee": "java",
    "j2ee": "java",
    
    # C# variations
    "c sharp": "c#",
    "csharp": "c#",
    "c-sharp": "c#",
    
    # C++ variations
    "c plus plus": "c++",
    "cplusplus": "c++",
    "cpp": "c++",
    
    # Objective-C variations
    "objective c": "objective-c",
    "obj-c": "objective-c",
    "objc": "objective-c",
    
    # React Native variations
    "react-native": "react native",
    "reactnative": "react native",
    "rn": "react native",
    
    # iOS variations
    "ios development": "ios",
    "iphone": "ios",
    
    # Android variations
    "android development": "android",
    "android studio": "android",
    
    # Spring Boot variations
    "springboot": "spring boot",
    "spring-boot": "spring boot",
    
    # Django variations
    "django rest framework": "django",
    "drf": "django",
    
    # Flask variations
    "flask-rest": "flask",
    "flask api": "flask",
    
    # FastAPI variations
    "fast api": "fastapi",
    "fast-api": "fastapi",
    
    # Testing variations
    "unit testing": "testing",
    "integration testing": "testing",
    "e2e testing": "testing",
    "test automation": "testing",
    
    # Agile variations
    "agile development": "agile",
    "agile methodology": "agile",
    "agile scrum": "agile",
    
    # Scrum variations
    "scrum master": "scrum",
    "scrum methodology": "scrum",
    
    # DevOps variations
    "dev ops": "devops",
    "dev-ops": "devops",
    
    # UI/UX variations
    "ui": "ui/ux",
    "ux": "ui/ux",
    "user interface": "ui/ux",
    "user experience": "ui/ux",
    
    # Microservices variations
    "micro services": "microservices",
    "micro-services": "microservices",
    "microservice architecture": "microservices",
}



FALLBACK_SKIP_VERBS = {
    # Development & Creation
    "developed",
    "developing",
    "develop",
    "built",
    "building",
    "build",
    "implemented",
    "implementing",
    "implement",
    "designed",
    "designing",
    "design",
    "created",
    "creating",
    "create",
    "engineered",
    "engineering",
    "engineer",
    "programmed",
    "programming",
    "program",
    "coded",
    "coding",
    "code",
    "wrote",
    "writing",
    "write",
    "constructed",
    "constructing",
    "construct",
    
    # Management & Leadership
    "led",
    "leading",
    "lead",
    "managed",
    "managing",
    "manage",
    "coordinated",
    "coordinating",
    "coordinate",
    "oversaw",
    "overseeing",
    "oversee",
    "supervised",
    "supervising",
    "supervise",
    "directed",
    "directing",
    "direct",
    "organized",
    "organizing",
    "organize",
    "facilitated",
    "facilitating",
    "facilitate",
    
    # Optimization & Improvement
    "optimized",
    "optimizing",
    "optimize",
    "improved",
    "improving",
    "improve",
    "enhanced",
    "enhancing",
    "enhance",
    "refined",
    "refining",
    "refine",
    "streamlined",
    "streamlining",
    "streamline",
    "upgraded",
    "upgrading",
    "upgrade",
    "modernized",
    "modernizing",
    "modernize",
    
    # Deployment & Operations
    "deployed",
    "deploying",
    "deploy",
    "launched",
    "launching",
    "launch",
    "released",
    "releasing",
    "release",
    "delivered",
    "delivering",
    "deliver",
    "shipped",
    "shipping",
    "ship",
    "migrated",
    "migrating",
    "migrate",
    "integrated",
    "integrating",
    "integrate",
    
    # Configuration & Setup
    "configured",
    "configuring",
    "configure",
    "setup",
    "setting up",
    "set up",
    "installed",
    "installing",
    "install",
    "established",
    "establishing",
    "establish",
    "initialized",
    "initializing",
    "initialize",
    
    # Maintenance & Support
    "maintained",
    "maintaining",
    "maintain",
    "supported",
    "supporting",
    "support",
    "debugged",
    "debugging",
    "debug",
    "troubleshot",
    "troubleshooting",
    "troubleshoot",
    "fixed",
    "fixing",
    "fix",
    "resolved",
    "resolving",
    "resolve",
    "patched",
    "patching",
    "patch",
    
    # Analysis & Research
    "analyzed",
    "analyzing",
    "analyze",
    "evaluated",
    "evaluating",
    "evaluate",
    "assessed",
    "assessing",
    "assess",
    "investigated",
    "investigating",
    "investigate",
    "researched",
    "researching",
    "research",
    "studied",
    "studying",
    "study",
    "reviewed",
    "reviewing",
    "review",
    
    # Collaboration & Communication
    "collaborated",
    "collaborating",
    "collaborate",
    "worked",
    "working",
    "work",
    "partnered",
    "partnering",
    "partner",
    "communicated",
    "communicating",
    "communicate",
    "presented",
    "presenting",
    "present",
    "demonstrated",
    "demonstrating",
    "demonstrate",
    
    # Documentation & Planning
    "documented",
    "documenting",
    "document",
    "planned",
    "planning",
    "plan",
    "architected",
    "architecting",
    "architect",
    "drafted",
    "drafting",
    "draft",
    "outlined",
    "outlining",
    "outline",
    "specified",
    "specifying",
    "specify",
    
    # Testing & Quality Assurance
    "tested",
    "testing",
    "test",
    "validated",
    "validating",
    "validate",
    "verified",
    "verifying",
    "verify",
    "ensured",
    "ensuring",
    "ensure",
    "monitored",
    "monitoring",
    "monitor",
    
    # Training & Mentoring
    "trained",
    "training",
    "train",
    "mentored",
    "mentoring",
    "mentor",
    "coached",
    "coaching",
    "coach",
    "taught",
    "teaching",
    "teach",
    "educated",
    "educating",
    "educate",
    "onboarded",
    "onboarding",
    "onboard",
    
    # Automation & Scripting
    "automated",
    "automating",
    "automate",
    "scripted",
    "scripting",
    "script",
    "orchestrated",
    "orchestrating",
    "orchestrate",
    
    # Scaling & Performance
    "scaled",
    "scaling",
    "scale",
    "accelerated",
    "accelerating",
    "accelerate",
    "boosted",
    "boosting",
    "boost",
    
    # Data Operations
    "processed",
    "processing",
    "process",
    "transformed",
    "transforming",
    "transform",
    "extracted",
    "extracting",
    "extract",
    "loaded",
    "loading",
    "load",
    "queried",
    "querying",
    "query",
    
    # Security
    "secured",
    "securing",
    "secure",
    "protected",
    "protecting",
    "protect",
    "hardened",
    "hardening",
    "harden",
    
    # General Actions
    "utilized",
    "utilizing",
    "utilize",
    "used",
    "using",
    "use",
    "applied",
    "applying",
    "apply",
    "executed",
    "executing",
    "execute",
    "performed",
    "performing",
    "perform",
    "completed",
    "completing",
    "complete",
    "achieved",
    "achieving",
    "achieve",
    "accomplished",
    "accomplishing",
    "accomplish",
}


# Industry-standard fixed categories. Never allow dynamic/LLM-invented categories.
MASTER_SKILL_CATEGORIES = frozenset({
    "Programming Languages",
    "Databases",
    "Cloud Platforms",
    "Cloud Services",
    "Data Warehousing",
    "Big Data Technologies",
    "ETL & Data Integration",
    "Data Governance",
    "Machine Learning",
    "Visualization Tools",
    "DevOps & Containers",
    "Methodologies",
    "Project Tools",
    "Soft Skills",
    "AWS Compute",
    "AWS Serverless",
    "GCP Data Warehouse",
    "Cloud Data Warehouse",
    "Cloud Data Platform",
    "AWS Data Warehouse",
    "ML Frameworks",
    "LLM Models",
    "Cloud Storage",
    "Cloud ML",
})

# Map legacy or variant category names to master taxonomy (no random categories).
CATEGORY_MAP = {
    "programming languages": "Programming Languages",
    "databases": "Databases",
    "cloud platforms": "Cloud Platforms",
    "cloud services": "Cloud Services",
    "data warehousing": "Data Warehousing",
    "big data technologies": "Big Data Technologies",
    "big data": "Big Data Technologies",
    "etl & data integration": "ETL & Data Integration",
    "etl": "ETL & Data Integration",
    "data governance": "Data Governance",
    "machine learning": "Machine Learning",
    "data & ml": "Machine Learning",
    "visualization tools": "Visualization Tools",
    "devops & containers": "DevOps & Containers",
    "devops": "DevOps & Containers",
    "methodologies": "Methodologies",
    "project tools": "Project Tools",
    "soft skills": "Soft Skills",
    "frameworks": "Programming Languages",
    "tools": "DevOps & Containers",
    "web technologies": "Programming Languages",
    "mobile development": "Programming Languages",
    "testing": "Project Tools",
    "message queues": "Big Data Technologies",
    "monitoring & logging": "DevOps & Containers",
    "architecture": "Methodologies",
    "backend": "Programming Languages",
    "security": "Project Tools",
    "emerging tech": "Project Tools",
    "aws compute": "AWS Compute",
    "aws serverless": "AWS Serverless",
    "gcp data warehouse": "GCP Data Warehouse",
    "cloud data warehouse": "Cloud Data Warehouse",
    "cloud data platform": "Cloud Data Platform",
    "aws data warehouse": "AWS Data Warehouse",
    "ml frameworks": "ML Frameworks",
    "llm models": "LLM Models",
    "cloud storage": "Cloud Storage",
    "cloud ml": "Cloud ML",
}

# Finer category mapping: normalized skill -> specific category (overrides taxonomy when present).
FINE_CATEGORY_MAP = {
    "ec2": "AWS Compute",
    "lambda": "AWS Serverless",
    "bigquery": "GCP Data Warehouse",
    "snowflake": "Cloud Data Warehouse",
    "databricks": "Cloud Data Platform",
    "redshift": "AWS Data Warehouse",
    "pytorch": "ML Frameworks",
    "tensorflow": "ML Frameworks",
    "bert": "LLM Models",
    "gpt": "LLM Models",
    "t5": "LLM Models",
    "aws": "Cloud Platforms",
    "s3": "Cloud Storage",
    "vertex ai": "Cloud ML",
    "docker": "DevOps & Containers",
    "kubernetes": "DevOps & Containers",
}

# --- 4-Layer quality filter: atomic validation, sentence fragment rejection, canonical map, category sanitization ---

# Skills must not start with these (sentence fragments / conjunctions).
REJECT_STARTS_WITH = (
    "and ", "then ", "leveraging ", "processing ", "transforming ", "utilizing ",
    "constructed ", "loading ", "driving ", "building ", "designing ", "developing ",
    "or ", "with ", "for ", "from ", "using ", "via ", "including ", "such as ",
)
# Reject if skill string contains these verbs (sentence fragment).
REJECT_VERBS = (
    "leveraging", "transforming", "loading", "processing", "utilizing", "constructed",
    "driving", "building", "designing", "developing", "proficient", "across", "modern",
    "tools", "scalable", "then loading", "and data",
)
MAX_WORDS_ATOMIC = 4   # Valid skill: at most 4 words.
MAX_WORDS_REJECT = 6   # Reject as sentence fragment if more than 6 words.

# Punctuation that indicates sentence fragment (not a single skill token).
PUNCTUATION_REJECT = re.compile(r"[.,;:]")
# Broken token: truncated parenthetical e.g. "Google Kubernetes Engine (GKE"
BROKEN_PAREN_REJECT = re.compile(r"\([^)]*$")

# Canonical normalization: variant -> single canonical normalized_name (no duplicates).
CANONICAL_SKILL_MAP = {
    "amazon redshift": "redshift",
    "aws redshift": "redshift",
    "google bigquery": "bigquery",
    "bigquery": "bigquery",
    "aws s3": "s3",
    "amazon s3": "s3",
    "s3 glacier": "s3",
    "amazon s3 glacier": "s3",
    "gcp pub/sub": "pubsub",
    "pub/sub": "pubsub",
    "azure event hubs": "event hubs",
    "google kubernetes engine": "kubernetes",
    "gke": "kubernetes",
    "amazon ec2": "ec2",
    "aws ec2": "ec2",
    "aws lambda": "lambda",
    "amazon web services": "aws",
    "microsoft azure": "azure",
    "google cloud platform": "gcp",
    "amazon forecast": "aws",
    "amazon timestream": "aws",
    "amazon cloudwatch": "aws",
    "cloudwatch": "aws",
}

# Tech pattern: PascalCase word, or 2–5 char uppercase acronym, or known tech suffix.
_TECH_ACRONYM_RE = re.compile(r"^[A-Z]{2,5}$")
_KNOWN_ACRONYMS_LOWER = frozenset({"aws", "gcp", "sql", "api", "sdk", "ml", "ai", "etl", "gke", "k8s", "ec2", "nlp", "cicd", "ssr", "orm", "mvc", "rest", "grpc", "tls", "ssl", "csv", "json", "xml", "html", "css", "rds", "iam", "vpc", "vllm", "llm", "rag", "onnx", "cuda"})
_TECH_KEYWORDS = frozenset({"db", "sql", "cloud", "lake", "spark", "data", "api", "sdk", "ml", "ai", "etl", "s3", "ec2", "gke", "k8s", "llm", "rag", "vector", "embedding", "vllm", "tensor", "bert", "gpt", "transformer"})

# Generic/umbrella terms — never store as skills (not atomic technologies).
REJECT_GENERIC_SKILLS = frozenset({"cloud", "backend", "security", "frontend", "web development"})


def is_sentence_fragment(text: str) -> bool:
    """Reject if looks like a sentence fragment, not an atomic skill."""
    if not text or not isinstance(text, str):
        return True
    s = text.strip()
    if not s:
        return True
    words = s.split()
    if len(words) > MAX_WORDS_REJECT:
        return True
    lower = s.lower()
    for verb in REJECT_VERBS:
        if verb in lower:
            return True
    if PUNCTUATION_REJECT.search(s):
        return True
    if BROKEN_PAREN_REJECT.search(s) or s.rstrip().endswith("("):
        return True
    for bad in REJECT_STARTS_WITH:
        if lower.startswith(bad.strip()) or lower.startswith(bad):
            return True
    return False


def is_atomic_skill(text: str, known_normalized: set[str] | None = None) -> bool:
    """Skill is valid only if: in dictionary, or matches tech pattern; and <= 4 words; and not fragment."""
    if not text or not isinstance(text, str):
        return False
    s = text.strip()
    if not s:
        return False
    words = s.split()
    if len(words) > MAX_WORDS_ATOMIC:
        return False
    lower = s.lower()
    for bad in REJECT_STARTS_WITH:
        if lower.startswith(bad.strip()) or lower.startswith(bad):
            return False
    known_normalized = known_normalized or set()
    norm = normalize_skill_name(s)
    if norm in known_normalized:
        return True
    # Title Case (e.g. Snowflake, BigQuery, Flet, Solidity, Ray, Python)
    if len(s) >= 2 and s[0].isupper() and len(words) == 1:
        return True
    # CamelCase or mixed case (e.g. vLLM, jQuery, iPhone)
    if len(s) >= 3 and any(c.isupper() for c in s[1:]):
        # Basic check to ensure it's a technical-looking token
        if re.match(r"^[A-Za-z0-9-]+$", s):
            return True
    # Uppercase acronym 2–5 chars
    if _TECH_ACRONYM_RE.match(s):
        return True
    # Known acronym in lowercase (e.g. gke, aws)
    if norm in _KNOWN_ACRONYMS_LOWER:
        return True
    # Contains known tech keyword
    for kw in _TECH_KEYWORDS:
        if kw in norm:
            return True
    return False


def normalize_to_canonical(skill_name: str) -> str:
    """Map variant to canonical normalized name; return normalized string either way."""
    norm = normalize_skill_name(skill_name)
    return CANONICAL_SKILL_MAP.get(norm, norm)


def is_broken_or_fragment(skill_name: str) -> bool:
    """True if skill should be rejected (sentence fragment or broken token)."""
    return is_sentence_fragment(skill_name)


def is_generic_skill(normalized_name: str) -> bool:
    """True if skill is a generic/umbrella term that must not be stored. Only REJECT_GENERIC_SKILLS (cloud, backend, security, frontend, web development) are treated as generic."""
    if not normalized_name:
        return True
    return normalize_skill_name(normalized_name) in REJECT_GENERIC_SKILLS


def sanitize_category(category: str | None) -> str | None:
    """Reject corrupted category (e.g. comma-separated tech list); return clean or None."""
    if not category or not isinstance(category, str):
        return None
    s = category.strip()
    if not s:
        return None
    # Corrupted: contains comma or multiple words that look like tech names (e.g. "Wrangler, Amazon Forecast")
    if "," in s:
        return None
    if len(s.split()) > 4:
        return None
    # Must be one of allowed
    return map_category_to_master(s)


def normalize_skill_name(skill: str) -> str:
    """Normalize for deduplication: lowercase, strip, single spaces."""
    return " ".join((skill or "").strip().lower().split())


def map_category_to_master(category: str | None) -> str | None:
    """Map any category to master taxonomy; return None if unknown."""
    if not category:
        return None
    key = category.strip().lower()
    return CATEGORY_MAP.get(key) or (category if category in MASTER_SKILL_CATEGORIES else "Project Tools")


@dataclass(frozen=True)
class SkillMatch:
    name: str
    normalized_name: str
    category: str | None
    confidence: float
    years_experience: int | None
    proficiency: str | None
    source: str | None = None
    version: list[str] | None = None


def _build_known_skills_set(
    normalized_map: dict,
    synonym_map: dict,
) -> set[str]:
    """Build set of all known skill names (canonical + synonyms) for lookup."""
    known: set[str] = set(normalized_map.keys()) | set(synonym_map.keys()) | set(synonym_map.values())
    known.update(RELATED_SKILLS.keys())
    for vals in RELATED_SKILLS.values():
        known.update(vals)
    known.update(SKILL_ALIASES.values())
    known.update(s.lower().replace("-", " ").replace("_", " ") for s in SOFT_SKILLS)
    return known


class SkillExtractor:
    def __init__(self, taxonomy_path: str | None = None, use_spacy: bool = True) -> None:
        self.taxonomy = self._load_taxonomy(taxonomy_path)
        self.normalized_map = {
            item["normalized_name"]: item for item in self.taxonomy
        }
        self.synonym_map = self._build_synonym_map(self.taxonomy)
        self._known_skills = _build_known_skills_set(self.normalized_map, self.synonym_map)
        self.use_spacy = use_spacy and spacy is not None
        self._nlp = None
        self._matcher = None
        if self.use_spacy:
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except Exception:  # noqa: BLE001
                self._nlp = spacy.blank("xx")
            self._matcher = PhraseMatcher(self._nlp.vocab, attr="LOWER")
            patterns = [self._nlp.make_doc(item["name"]) for item in self.taxonomy]
            patterns += [self._nlp.make_doc(syn) for syn in self.synonym_map.keys()]
            self._matcher.add("SKILL", patterns)

    def get_known_normalized_skills(self) -> set[str]:
        """Return set of known normalized skill names for atomic validation."""
        return set(self._known_skills)

    def get_canonical_normalized_names(self) -> set[str]:
        """Return set of canonical skill names from master taxonomy (for strict dictionary validation)."""
        return set(self.normalized_map.keys())

    def extract_from_skills_section(self, text: str) -> list[SkillMatch]:
        """Extract skills from the technical skills section only.
        Uses enterprise-grade cleaning (parentheses -> comma, no space-split), then phrase match + comma-only token match."""
        source = "technical_skills_section"
        cleaned = clean_skill_text_for_section(text or "")
        if not cleaned:
            return []
        # Phrase-based taxonomy match (e.g. "Amazon Redshift" in block)
        phrase_matches = self._extract_skills(cleaned, base_confidence=0.85, source=source)
        # Comma-only tokenization: no space/newline split to avoid "main tracking", "based and ML", "Spanner)"
        tokens = tokenize_skills_by_comma(cleaned)
        freeform_matches: list[SkillMatch] = []
        for token in tokens:
            token = strip_skill_token(token)
            if not token or len(token) < 2:
                continue
            base_name, versions = self._extract_versions_from_token(token)
            canonicalize_input = (base_name if base_name else token).strip()
            for name, normalized, category_hint in self._expand_and_canonicalize(canonicalize_input or token):
                vers = versions if versions else None
                final_cat = map_category_to_master(category_hint) if category_hint else None
                if normalized in self.normalized_map:
                    item = self.normalized_map[normalized]
                    freeform_matches.append(
                        SkillMatch(
                            name=item["name"],
                            normalized_name=item["normalized_name"],
                            category=item.get("category") or final_cat,
                            confidence=0.7,
                            years_experience=None,
                            proficiency=None,
                            source=source,
                            version=vers,
                        )
                    )
                elif category_hint == "Soft Skills":
                    freeform_matches.append(
                        SkillMatch(
                            name=name,
                            normalized_name=normalized,
                            category=category_hint,
                            confidence=0.5,
                            years_experience=None,
                            proficiency=None,
                            source=source,
                            version=vers,
                        )
                    )
                elif is_atomic_skill(name, self.get_known_normalized_skills()):
                    freeform_matches.append(
                        SkillMatch(
                            name=name,
                            normalized_name=normalized,
                            category=final_cat or "Technical Skills",
                            confidence=0.65,
                            years_experience=None,
                            proficiency=None,
                            source=source,
                            version=vers,
                        )
                    )
        return self.normalize_skills(phrase_matches + freeform_matches)

    def extract_from_work_history(self, jobs: Iterable[JobEntry]) -> list[SkillMatch]:
        source = "experience"
        matches: list[SkillMatch] = []
        for job in jobs:
            matches.extend(self._extract_skills(clean_text_for_skills(job.description or ""), base_confidence=0.6, source=source))
        return matches

    def normalize_skills(self, matches: Iterable[SkillMatch]) -> list[SkillMatch]:
        merged: dict[str, SkillMatch] = {}
        for match in matches:
            key = match.normalized_name
            existing = merged.get(key)
            if not existing:
                merged[key] = match
                continue
            # Keep higher confidence; merge version lists (dedupe, preserve order)
            keep = match if match.confidence > existing.confidence else existing
            other = existing if keep is match else match
            versions = list(keep.version) if keep.version else []
            if other.version:
                for v in other.version:
                    if v not in versions:
                        versions.append(v)
            merged[key] = SkillMatch(
                name=keep.name,
                normalized_name=keep.normalized_name,
                category=keep.category,
                confidence=keep.confidence,
                years_experience=keep.years_experience,
                proficiency=keep.proficiency,
                source=keep.source,
                version=versions if versions else None,
            )
        return list(merged.values())

    def categorize_skills(self, matches: Iterable[SkillMatch]) -> list[SkillMatch]:
        categorized = []
        for match in matches:
            # Prefer finer category (e.g. EC2 -> AWS Compute) over taxonomy
            fine = FINE_CATEGORY_MAP.get(match.normalized_name)
            if fine:
                category = fine
            else:
                taxonomy = self.normalized_map.get(match.normalized_name)
                raw_category = taxonomy.get("category") if taxonomy else match.category
                category = map_category_to_master(raw_category) or map_category_to_master(match.category)
            categorized.append(
                SkillMatch(
                    name=match.name,
                    normalized_name=match.normalized_name,
                    category=category,
                    confidence=match.confidence,
                    years_experience=match.years_experience,
                    proficiency=match.proficiency,
                    source=match.source,
                    version=match.version,
                )
            )
        return categorized

    def infer_proficiency(self, text: str, skill: str) -> str | None:
        """Return proficiency only when resume explicitly states it next to the skill (Advanced/Expert/etc)."""
        # Look for patterns like "Skill (Advanced)" or "Skill: Advanced"
        pattern = rf"{re.escape(skill)}\s*\(?(Advanced|Intermediate|Beginner|Expert|Expertise)\)?"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).lower()
            return EXPLICIT_PROFICIENCY_KEYWORDS.get(val, val)
        return None

    def calculate_skill_years(
        self, jobs: Iterable[JobEntry], skill: str
    ) -> int | None:
        months = 0
        for job in jobs:
            if skill.lower() in job.description.lower():
                if job.duration_months:
                    months += job.duration_months
        return int(months / 12) if months else None

    def infer_related_skills(self, matches: Iterable[SkillMatch]) -> list[SkillMatch]:
        related: list[SkillMatch] = []
        present = {match.normalized_name for match in matches}
        for match in matches:
            for rel in RELATED_SKILLS.get(match.normalized_name, []):
                if rel in present:
                    continue
                taxonomy = self.normalized_map.get(rel)
                if taxonomy:
                    related.append(
                        SkillMatch(
                            name=taxonomy["name"],
                            normalized_name=taxonomy["normalized_name"],
                            category=taxonomy.get("category"),
                            confidence=0.4,
                            years_experience=None,
                            proficiency=None,
                        )
                    )
        return related

    def extract_all(
        self,
        skills_section: str,
        jobs: Iterable[JobEntry],
        *,
        skills_section_confidence: float | None = None,
        raw_text: str | None = None,
        section_only: bool = True,
    ) -> list[SkillMatch]:
        """Extract skills. Always supplements with raw_text when provided so sparse/misdetected sections don't lose skills."""
        section_text = clean_skill_text_for_section(skills_section or "")
        if skills_section_confidence is not None and skills_section_confidence < 0.6:
            section_text = ""
        raw_text_cleaned = clean_text_for_skills(raw_text or "") if raw_text else ""

        section_matches = self.extract_from_skills_section(section_text) if section_text else []
        history_matches = [] if section_only else self.extract_from_work_history(jobs)
        # Always use raw_text as supplementary source so we don't lose skills when section is small or misdetected
        fallback_matches = self.extract_from_raw_text(raw_text_cleaned) if raw_text_cleaned else []

        all_matches = self.normalize_skills(section_matches + history_matches + fallback_matches)

        # Do not guess years of experience; only explicit mention or timeline would set it (handled elsewhere).
        enriched = []
        for match in all_matches:
            proficiency = self.infer_proficiency(section_text or (raw_text_cleaned or ""), match.normalized_name)
            enriched.append(
                SkillMatch(
                    name=match.name,
                    normalized_name=match.normalized_name,
                    category=match.category,
                    confidence=match.confidence,
                    years_experience=None,
                    proficiency=proficiency,
                    source=match.source,
                    version=match.version,
                )
            )
        enriched = self.categorize_skills(enriched)
        # No enrichment: do not inject related skills; only return extracted skills.
        # enriched.extend(self.infer_related_skills(enriched))
        return self.normalize_skills(enriched)

    def extract_from_raw_text(self, text: str) -> list[SkillMatch]:
        if not text:
            return []
        text = clean_text_for_skills(text)
        if not text:
            return []
        matches: list[SkillMatch] = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            lines = [s.strip() for s in text.split(",") if s.strip()]
        for line in lines:
            if len(line) > 200:
                continue
            lowered = line.lower()
            if ":" in line:
                if any(re.search(rf"\b{re.escape(v)}\b", lowered) for v in FALLBACK_SKIP_VERBS):
                    continue
                label, _, values = line.partition(":")
                label_lower = label.lower()
                if not any(
                    k in label_lower
                    for k in ("skill", "tools", "technology", "technologies", "tech stack", "expertise", "competencies")
                ):
                    continue
                tokens = self._split_skills(values)
            else:
                delim_count = sum(int(d in line) for d in (",", "|", "•", "-", ";"))
                if delim_count < 2:
                    # Try token-line extraction for space-separated skills (no verb skip)
                    token_hits = self._extract_from_token_line(line)
                    if token_hits:
                        tokens = token_hits
                    else:
                        continue
                else:
                    if any(re.search(rf"\b{re.escape(v)}\b", lowered) for v in FALLBACK_SKIP_VERBS):
                        continue
                    tokens = self._split_skills(line)

            raw_text_source = "raw_text"
            for token in tokens:
                for name, canonical, category in self._expand_and_canonicalize(token):
                    base = 0.55 if canonical in self.normalized_map else 0.45
                    matches.append(
                        SkillMatch(
                            name=name,
                            normalized_name=canonical,
                            category=category,
                            confidence=base,
                            years_experience=None,
                            proficiency=None,
                            source=raw_text_source,
                        )
                    )

        return matches

    def _expand_and_canonicalize(self, token: str) -> list[tuple[str, str, str | None]]:
        """Expand compound skills, then canonicalize. Keep original if no parts in taxonomy."""
        expanded = self._expand_compound_skill(token)
        any_in_taxonomy = any(
            self._canonicalize_token(p)[1] in self.normalized_map for p in expanded
        )
        if any_in_taxonomy:
            return [self._canonicalize_token(part) for part in expanded]
        return [self._canonicalize_token(token)]

    def _canonicalize_token(self, token: str) -> tuple[str, str, str | None]:
        name = re.sub(r"\s+", " ", (token or "").strip())
        lowered = name.lower()
        lowered = lowered.replace("(", " ").replace(")", " ")
        lowered = re.sub(r"\s+", " ", lowered).strip()
        alias_key = lowered.replace(".", "").replace(" ", "").replace("-", "")
        canonical = SKILL_ALIASES.get(lowered) or SKILL_ALIASES.get(alias_key) or lowered
        canonical = self.synonym_map.get(canonical, canonical)
        canonical = canonical.replace(" ", " ").strip()
        if canonical in self.normalized_map:
            taxonomy = self.normalized_map[canonical]
            return taxonomy["name"], taxonomy["normalized_name"], taxonomy.get("category")

        if lowered in SOFT_SKILLS or alias_key in {s.replace(" ", "").replace("-", "") for s in SOFT_SKILLS}:
            return name, lowered.replace("-", " "), "Soft Skills"

        return name, canonical, None

    def _extract_skills(
        self, text: str, base_confidence: float, source: str | None = None
    ) -> list[SkillMatch]:
        matches: list[SkillMatch] = []
        lowered = text.lower()
        seen_normalized: set[str] = set()

        def _contains_term(term: str) -> bool:
            """Match skill with word boundaries so 'React' does not match 'ReactNative', 'SQL' not in 'NoSQL'."""
            if not term:
                return False
            term_lower = term.lower().strip()
            pattern = r"\b" + re.escape(term_lower) + r"\b"
            return bool(re.search(pattern, lowered, re.IGNORECASE))

        for canonical, item in self.normalized_map.items():
            if _contains_term(canonical) and item["normalized_name"] not in seen_normalized:
                seen_normalized.add(item["normalized_name"])
                matches.append(
                    SkillMatch(
                        name=item["name"],
                        normalized_name=item["normalized_name"],
                        category=item.get("category"),
                        confidence=base_confidence,
                        years_experience=None,
                        proficiency=None,
                        source=source,
                    )
                )

        for synonym, canonical in self.synonym_map.items():
            if _contains_term(synonym):
                item = self.normalized_map[canonical]
                if item["normalized_name"] not in seen_normalized:
                    seen_normalized.add(item["normalized_name"])
                    matches.append(
                        SkillMatch(
                            name=item["name"],
                            normalized_name=item["normalized_name"],
                            category=item.get("category"),
                            confidence=base_confidence - 0.1,
                            years_experience=None,
                            proficiency=None,
                            source=source,
                        )
                    )

        if self.use_spacy and self._nlp and self._matcher:
            doc = self._nlp(text)
            for _, start, end in self._matcher(doc):
                span = doc[start:end].text.lower()
                canonical = self.synonym_map.get(span, span)
                item = self.normalized_map.get(canonical)
                if not item or item["normalized_name"] in seen_normalized:
                    continue
                seen_normalized.add(item["normalized_name"])
                matches.append(
                    SkillMatch(
                        name=item["name"],
                        normalized_name=item["normalized_name"],
                        category=item.get("category"),
                        confidence=base_confidence,
                        years_experience=None,
                        proficiency=None,
                        source=source,
                    )
                )

        return matches

    def _extract_freeform_skills(
        self, text: str, base_confidence: float, source: str | None = None
    ) -> list[SkillMatch]:
        matches: list[SkillMatch] = []
        if not text:
            return matches
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            if ":" in line:
                label, _, values = line.partition(":")
                category = label.strip().title()
                # If label looks too long, it's not a category label
                if len(category.split()) > 4:
                    category = None
                    tokens = self._split_skills(line)
                else:
                    tokens = self._split_skills(values)
            else:
                category = None
                tokens = self._split_skills(line)
            
            for token in tokens:
                base_name, versions = self._extract_versions_from_token(token)
                canonicalize_input = (base_name if base_name else token).strip()
                for name, normalized, category_hint in self._expand_and_canonicalize(canonicalize_input or token):
                    vers = versions if versions else None
                    # Normalize category
                    final_cat = category_hint or category
                    if final_cat:
                        final_cat = map_category_to_master(final_cat)

                    if normalized in self.normalized_map:
                        item = self.normalized_map[normalized]
                        matches.append(
                            SkillMatch(
                                name=item["name"],
                                normalized_name=item["normalized_name"],
                                category=item.get("category") or final_cat,
                                confidence=base_confidence,
                                years_experience=None,
                                proficiency=None,
                                source=source,
                                version=vers,
                            )
                        )
                    elif category_hint == "Soft Skills":
                        matches.append(
                            SkillMatch(
                                name=name,
                                normalized_name=normalized,
                                category=category_hint,
                                confidence=base_confidence - 0.2,
                                years_experience=None,
                                proficiency=None,
                                source=source,
                                version=vers,
                            )
                        )
                    elif is_atomic_skill(name, self.get_known_normalized_skills()):
                        # Check internal compound expansion again (just in case)
                        matches.append(
                            SkillMatch(
                                name=name,
                                normalized_name=normalized,
                                category=final_cat or "Technical Skills",
                                confidence=base_confidence - 0.1,
                                years_experience=None,
                                proficiency=None,
                                source=source,
                                version=vers,
                            )
                        )
        return matches

    @staticmethod
    def _expand_compound_skill(skill: str) -> list[str]:
        """Expand compound skills: React/Redux -> [React, Redux]; AWS (EC2, S3) -> [AWS, EC2, S3]."""
        skills = [skill]

        if "/" in skill and len(skill) < 40:
            parts = [p.strip() for p in skill.split("/")]
            if all(len(p) >= 2 for p in parts):
                skills = parts

        paren_m = re.match(r"^(\w+)\s*\(([^)]+)\)\s*$", skill.strip())
        if paren_m:
            parent = paren_m.group(1)
            children = [c.strip() for c in paren_m.group(2).split(",") if c.strip()]
            skills = [parent] + children

        return skills

    @staticmethod
    def _extract_versions_from_token(token: str) -> tuple[str, list[str]]:
        """Extract version tokens (e.g. 11g, 10g, 2014, 5.6) from string; return (name_without_versions, versions)."""
        if not token or not token.strip():
            return token, []
        versions = VERSION_PATTERN.findall(token)
        name_clean = VERSION_PATTERN.sub("", token).strip()
        name_clean = re.sub(r"\s+", " ", name_clean).strip(" /,-")
        return name_clean or token, versions

    @staticmethod
    def _split_skills(value: str) -> list[str]:
        """Split by comma, newline, parentheses, slash; strip brackets/parens from each token to avoid 'Spanner)' etc."""
        if not value:
            return []
        text = value.replace("\u2022", ",").replace("•", ",").replace("|", ",").replace(";", ",")
        tokens = re.split(r"[,\n()/\t]", text)
        result: list[str] = []
        for t in tokens:
            cleaned = t.strip("-* ()[]\"'").strip()
            if not cleaned:
                continue
            lowered = cleaned.lower()
            if lowered in {"advanced", "intermediate", "beginner", "expert", "expertise", "proficient", "familiar"}:
                continue
            if len(cleaned) < 2 and not cleaned.isalnum():
                continue
            if re.search(r"[A-Za-z]", cleaned):
                result.append(cleaned)
        return result

    def _is_known_skill(self, token: str) -> bool:
        """Check if token (unigram or bigram) is a known skill from taxonomy or aliases."""
        _, canonical, category = self._canonicalize_token(token)
        return canonical in self._known_skills or category == "Soft Skills"

    def _extract_from_token_line(self, line: str) -> list[str]:
        """Match 3+ consecutive known taxonomy tokens on a single line."""
        tokens = line.split()
        hits = [t for t in tokens if self._is_known_skill(t)]
        if len(hits) >= 3:
            return hits
        # Also handle 2-word skills: 'Machine Learning', 'Node JS'
        bigrams = [f"{tokens[i]} {tokens[i + 1]}" for i in range(len(tokens) - 1)]
        bigram_hits = [b for b in bigrams if self._is_known_skill(b)]
        if len(hits) + len(bigram_hits) >= 3:
            return hits + bigram_hits
        return []

    def _load_taxonomy(self, taxonomy_path: str | None) -> list[dict]:
        path = (
            Path(taxonomy_path)
            if taxonomy_path
            else Path(__file__).resolve().parents[2]
            / "data"
            / "taxonomy"
            / "skills_seed.json"
        )
        if not path.exists():
            logger.warning("Skill taxonomy not found", extra={"path": str(path)})
            return []
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data.get("skills", [])

    @staticmethod
    def _build_synonym_map(taxonomy: list[dict]) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for item in taxonomy:
            canonical = item["normalized_name"]
            for synonym in item.get("synonyms", []):
                mapping[synonym.lower()] = canonical
            mapping[item["name"].lower()] = canonical
        return mapping
