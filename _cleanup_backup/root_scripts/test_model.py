from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

MODEL_PATH = r"C:\Users\anjir\Downloads\resume-ner-deberta\resume-ner-deberta"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

print("Loading model...")
model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)

print("Creating pipeline...")
ner = pipeline(
    "ner",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple"
)

text = """
PROFESSIONAL EXPERIENCE
Senior Manager
Company: Infosys
Location: Mumbai, India
Duration: 2019 – Present
Responsibilities:
•	Architected production ML pipelines using Azure Machine Learning.
•	Built end-to-end NLP pipelines using Hugging Face Transformers.
•	Implemented RAG architecture with Azure Cosmos DB Vector Search.
Software Engineer
Company: Wipro
Location: Hyderabad, India
Duration: 2018 – 2019
Responsibilities:
•	Designed production ML pipelines for credit risk modeling.
•	Orchestrated workflows using AWS Step Functions.
•	Maintained PCI-DSS compliance via AWS IAM policy enforcement.
EDUCATION
Bachelor of Technology (B.Tech) – Computer Science
Institution: Sreenidhi Institute of Science and Technology
Duration: Aug 2010 – May 2014


"""

print("Running model...")
results = ner(text)

for r in results:
    print(r)