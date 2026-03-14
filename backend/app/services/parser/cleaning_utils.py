
import spacy
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def get_spacy_model(model_name: str) -> Optional[spacy.Language]:
    try:
        return spacy.load(model_name)
    except Exception as e:
        logger.error(f"Error loading spacy model {model_name}: {e}")
        return None

def fix_concatenated_words(text: str) -> str:
    # Basic implementation if needed by other parts of the system
    return text
