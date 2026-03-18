# TF-IDF Vectorizer for Resume Text Processing

import re
from typing import List, Dict, Any
from collections import Counter
import math

class SimpleTfidfVectorizer:
    """
    Simple TF-IDF vectorizer implementation
    Used for text processing and feature extraction
    """
    
    def __init__(self):
        self.vocabulary = {}
        self.idf_values = {}
        self.document_count = 0
        self.max_features = 1000
        self.min_df = 1
        self.max_df = 0.95
        
    def fit(self, documents: List[str]) -> 'SimpleTfidfVectorizer':
        """
        Fit the vectorizer to a list of documents
        
        Args:
            documents: List of text documents
            
        Returns:
            Self for method chaining
        """
        self.document_count = len(documents)
        
        # Tokenize all documents and build vocabulary
        tokenized_docs = [self._tokenize(doc) for doc in documents]
        
        # Count document frequency for each token
        doc_freq = Counter()
        for tokens in tokenized_docs:
            unique_tokens = set(tokens)
            doc_freq.update(unique_tokens)
        
        # Filter tokens by document frequency
        min_doc_count = max(1, int(self.min_df * self.document_count))
        max_doc_count = int(self.max_df * self.document_count)
        
        # Build vocabulary
        self.vocabulary = {}
        for token, freq in doc_freq.items():
            if min_doc_count <= freq <= max_doc_count:
                self.vocabulary[token] = len(self.vocabulary)
        
        # Limit vocabulary size
        if len(self.vocabulary) > self.max_features:
            # Keep most frequent tokens
            most_common = doc_freq.most_common(self.max_features)
            self.vocabulary = {token: idx for idx, (token, _) in enumerate(most_common)}
        
        # Calculate IDF values
        self.idf_values = {}
        for token in self.vocabulary:
            df = doc_freq.get(token, 0)
            idf = math.log(self.document_count / (df + 1))
            self.idf_values[token] = idf
        
        return self
    
    def transform(self, documents: List[str]) -> List[Dict[str, float]]:
        """
        Transform documents to TF-IDF vectors
        
        Args:
            documents: List of text documents
            
        Returns:
            List of dictionaries with token -> TF-IDF score
        """
        results = []
        
        for doc in documents:
            tokens = self._tokenize(doc)
            tf_counts = Counter(tokens)
            
            # Calculate TF-IDF for each token in vocabulary
            tfidf_vector = {}
            for token, idx in self.vocabulary.items():
                if token in tf_counts:
                    tf = tf_counts[token] / len(tokens)
                    tfidf = tf * self.idf_values[token]
                    tfidf_vector[token] = tfidf
            
            results.append(tfidf_vector)
        
        return results
    
    def fit_transform(self, documents: List[str]) -> List[Dict[str, float]]:
        """
        Fit and transform in one step
        
        Args:
            documents: List of text documents
            
        Returns:
            List of dictionaries with token -> TF-IDF score
        """
        return self.fit(documents).transform(documents)
    
    def get_feature_names_out(self) -> List[str]:
        """Get the feature names (vocabulary)"""
        return list(self.vocabulary.keys())
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-z\s]', ' ', text)
        
        # Split into tokens
        tokens = text.split()
        
        # Remove very short tokens
        tokens = [token for token in tokens if len(token) >= 2]
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'shall', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
            'them', 'my', 'your', 'his', 'its', 'our', 'their', 'a', 'an'
        }
        
        tokens = [token for token in tokens if token not in stop_words]
        
        return tokens
    
    def get_top_keywords(self, document: str, top_k: int = 10) -> List[tuple[str, float]]:
        """
        Get top keywords from a document
        
        Args:
            document: Input document
            top_k: Number of top keywords to return
            
        Returns:
            List of (keyword, tfidf_score) tuples
        """
        if not self.vocabulary:
            return []
        
        tfidf_vector = self.transform([document])[0]
        
        # Sort by TF-IDF score
        sorted_keywords = sorted(tfidf_vector.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_keywords[:top_k]

# Global instance
tfidf_vectorizer = SimpleTfidfVectorizer()
