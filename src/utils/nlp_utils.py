import re
from typing import List, Dict, Tuple, Optional
import numpy as np
from collections import Counter
from datetime import datetime


class NLPProcessor:
    """NLP utilities for text processing and analysis"""

    def __init__(self):
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize sentence transformer model (lazy loading)"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load sentence transformer: {e}")
            self.model = None

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get sentence embedding for text"""
        if self.model is None:
            return None

        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        if self.model is None:
            return [[] for _ in texts]

        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return [[] for _ in texts]

    def cosine_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not emb1 or not emb2:
            return 0.0

        vec1 = np.array(emb1)
        vec2 = np.array(emb2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract keywords from text using simple frequency analysis"""
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', ' ', text.lower())

        # Common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'that', 'this',
            'these', 'those', 'it', 'its', 'he', 'she', 'they', 'them', 'their'
        }

        # Tokenize and filter
        words = text.split()
        words = [w for w in words if len(w) > 3 and w not in stop_words]

        # Count frequencies
        word_freq = Counter(words)

        return [word for word, _ in word_freq.most_common(top_n)]

    def extract_phrases(self, text: str, n_gram: int = 2) -> List[Tuple[str, int]]:
        """Extract n-gram phrases from text"""
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()

        phrases = []
        for i in range(len(words) - n_gram + 1):
            phrase = ' '.join(words[i:i + n_gram])
            phrases.append(phrase)

        phrase_freq = Counter(phrases)
        return phrase_freq.most_common(20)

    def analyze_sentiment_simple(self, text: str) -> float:
        """Simple sentiment analysis using keyword matching"""
        positive_words = {
            'peace', 'agreement', 'cooperation', 'dialogue', 'resolve', 'support',
            'alliance', 'positive', 'success', 'progress', 'stability', 'diplomatic'
        }

        negative_words = {
            'war', 'conflict', 'crisis', 'threat', 'attack', 'violence', 'tension',
            'dispute', 'sanctions', 'invasion', 'hostility', 'aggression', 'warning',
            'menacing', 'escalate', 'condemn', 'oppose'
        }

        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)

        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)

        total = pos_count + neg_count
        if total == 0:
            return 0.0

        # Return score from -1 (negative) to 1 (positive)
        return (pos_count - neg_count) / total

    def detect_urgency_indicators(self, text: str) -> List[str]:
        """Detect urgency indicators in text"""
        urgency_patterns = [
            r'\b(imminent|urgent|immediate|breaking|crisis|emergency)\b',
            r'\b(escalat\w+|intensif\w+)\b',
            r'\b(deadline|ultimatum)\b',
            r'\b(critical|crucial|vital)\b',
            r'\b(now|today|tonight|must)\b'
        ]

        text_lower = text.lower()
        indicators = []

        for pattern in urgency_patterns:
            matches = re.findall(pattern, text_lower)
            indicators.extend(matches)

        return list(set(indicators))

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Simple entity extraction (countries, leaders, organizations)"""
        # Common geopolitical entities
        countries = {
            'china', 'russia', 'usa', 'america', 'iran', 'israel', 'ukraine',
            'taiwan', 'india', 'pakistan', 'korea', 'japan', 'germany', 'france',
            'britain', 'turkey', 'syria', 'iraq', 'afghanistan', 'greenland'
        }

        leaders = {
            'trump', 'biden', 'xi', 'putin', 'modi', 'macron', 'scholz',
            'erdogan', 'netanyahu', 'zelensky'
        }

        organizations = {
            'nato', 'un', 'eu', 'brics', 'who', 'wto', 'imf', 'opec'
        }

        text_lower = text.lower()
        words = set(re.findall(r'\w+', text_lower))

        return {
            'countries': [c for c in countries if c in words],
            'leaders': [l for l in leaders if l in words],
            'organizations': [o for o in organizations if o in words]
        }

    def compare_rhetoric(self, texts_old: List[str], texts_new: List[str]) -> Dict[str, any]:
        """Compare rhetoric between two time periods"""
        # Extract keywords from both periods
        old_text = ' '.join(texts_old)
        new_text = ' '.join(texts_new)

        old_keywords = set(self.extract_keywords(old_text, top_n=20))
        new_keywords = set(self.extract_keywords(new_text, top_n=20))

        # Sentiment comparison
        old_sentiment = np.mean([self.analyze_sentiment_simple(t) for t in texts_old])
        new_sentiment = np.mean([self.analyze_sentiment_simple(t) for t in texts_new])

        # Urgency comparison
        old_urgency = sum(len(self.detect_urgency_indicators(t)) for t in texts_old)
        new_urgency = sum(len(self.detect_urgency_indicators(t)) for t in texts_new)

        return {
            'sentiment_change': float(new_sentiment - old_sentiment),
            'urgency_change': new_urgency - old_urgency,
            'new_keywords': list(new_keywords - old_keywords),
            'dropped_keywords': list(old_keywords - new_keywords),
            'persistent_keywords': list(old_keywords & new_keywords)
        }
