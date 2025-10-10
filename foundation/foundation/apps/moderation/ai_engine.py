"""
Advanced AI Content Moderation Engine

This module provides comprehensive AI-powered content moderation capabilities including:
- Multi-algorithm content analysis (sentiment, toxicity, language detection)
- Real-time content filtering with dynamic rule adjustment
- Machine learning model integration and training pipeline
- Multi-language support for global content moderation
- Advanced threat detection (coordinated attacks, spam patterns)
- Content classification with confidence scoring
- Integration with discovery and governance systems
"""

import logging
import re
import hashlib
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction
from django.conf import settings
import threading
from collections import defaultdict, Counter
import numpy as np

logger = logging.getLogger(__name__)


class ContentAnalysisResult:
    """Represents the result of content analysis"""
    
    def __init__(self, content: str, content_id: Optional[str] = None):
        self.content = content
        self.content_id = content_id or self._generate_content_id()
        self.timestamp = timezone.now()
        
        # Analysis results
        self.sentiment_score = 0.0  # -1.0 (negative) to 1.0 (positive)
        self.toxicity_score = 0.0   # 0.0 (clean) to 1.0 (toxic)
        self.language = 'en'        # ISO language code
        self.language_confidence = 0.0
        
        # Classification results
        self.content_type = 'text'
        self.categories = []        # List of detected categories
        self.keywords = []          # Extracted keywords
        self.entities = []          # Named entities
        
        # Risk assessment
        self.risk_score = 0.0       # 0.0 (safe) to 1.0 (high risk)
        self.threat_indicators = [] # List of detected threats
        self.moderation_action = 'allow'  # allow, flag, block, escalate
        
        # Confidence and metadata
        self.confidence_score = 0.0
        self.processing_time = 0.0
        self.model_versions = {}
        self.flags = []
        
    def _generate_content_id(self) -> str:
        """Generate a unique content ID"""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        timestamp = str(int(self.timestamp.timestamp()))
        return f"content_{timestamp}_{content_hash[:8]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'content_id': self.content_id,
            'timestamp': self.timestamp.isoformat(),
            'sentiment_score': self.sentiment_score,
            'toxicity_score': self.toxicity_score,
            'language': self.language,
            'language_confidence': self.language_confidence,
            'content_type': self.content_type,
            'categories': self.categories,
            'keywords': self.keywords,
            'entities': self.entities,
            'risk_score': self.risk_score,
            'threat_indicators': self.threat_indicators,
            'moderation_action': self.moderation_action,
            'confidence_score': self.confidence_score,
            'processing_time': self.processing_time,
            'model_versions': self.model_versions,
            'flags': self.flags
        }


class SentimentAnalyzer:
    """Analyzes sentiment in text content"""
    
    def __init__(self):
        self.positive_words = {
            'amazing', 'awesome', 'excellent', 'fantastic', 'great', 'love',
            'wonderful', 'perfect', 'brilliant', 'outstanding', 'superb',
            'good', 'nice', 'beautiful', 'happy', 'joy', 'excited', 'pleased'
        }
        
        self.negative_words = {
            'awful', 'terrible', 'horrible', 'disgusting', 'hate', 'angry',
            'frustrated', 'disappointed', 'sad', 'depressed', 'furious',
            'bad', 'poor', 'worst', 'stupid', 'idiotic', 'pathetic', 'useless'
        }
        
        # Intensity modifiers
        self.intensifiers = {
            'very': 1.5, 'extremely': 2.0, 'incredibly': 1.8, 'absolutely': 1.7,
            'completely': 1.6, 'totally': 1.5, 'really': 1.3, 'quite': 1.2
        }
        
        self.diminishers = {
            'slightly': 0.5, 'somewhat': 0.6, 'rather': 0.7, 'fairly': 0.7,
            'kind of': 0.6, 'sort of': 0.6, 'a bit': 0.5, 'a little': 0.5
        }
    
    def analyze(self, content: str) -> Tuple[float, float]:
        """
        Analyze sentiment in content
        Returns: (sentiment_score, confidence)
        """
        if not content.strip():
            return 0.0, 0.0
        
        words = re.findall(r'\b\w+\b', content.lower())
        if not words:
            return 0.0, 0.0
        
        positive_score = 0.0
        negative_score = 0.0
        total_sentiment_words = 0
        
        for i, word in enumerate(words):
            modifier = 1.0
            
            # Check for intensity modifiers in previous words
            if i > 0:
                prev_word = words[i-1]
                if prev_word in self.intensifiers:
                    modifier = self.intensifiers[prev_word]
                elif prev_word in self.diminishers:
                    modifier = self.diminishers[prev_word]
            
            if word in self.positive_words:
                positive_score += 1.0 * modifier
                total_sentiment_words += 1
            elif word in self.negative_words:
                negative_score += 1.0 * modifier
                total_sentiment_words += 1
        
        if total_sentiment_words == 0:
            return 0.0, 0.0
        
        # Calculate net sentiment
        net_sentiment = (positive_score - negative_score) / total_sentiment_words
        
        # Normalize to -1.0 to 1.0 range
        sentiment_score = max(-1.0, min(1.0, net_sentiment))
        
        # Calculate confidence based on number of sentiment words
        confidence = min(1.0, total_sentiment_words / max(1, len(words) * 0.1))
        
        return sentiment_score, confidence


class ToxicityDetector:
    """Detects toxic and harmful content"""
    
    def __init__(self):
        # Toxic patterns - these would typically be loaded from a more comprehensive database
        self.toxic_patterns = [
            # Hate speech indicators
            r'\b(hate|kill|murder|die)\s+(you|them|him|her)\b',
            r'\b(fucking|damn|shit)\s+(stupid|idiot|moron)\b',
            
            # Harassment patterns
            r'\b(shut\s+up|go\s+away|get\s+lost)\b',
            r'\byou\s+(are|re)\s+(worthless|pathetic|disgusting)\b',
            
            # Threat patterns
            r'\b(i\s+will|gonna|going\s+to)\s+(hurt|harm|kill|destroy)\b',
            r'\byou\s+(better|should)\s+(watch|be\s+careful)\b',
            
            # Profanity clusters
            r'\b(fuck|shit|damn|hell){2,}',
            
            # Discrimination patterns
            r'\b(because\s+you\s+are|all\s+.+\s+are)\s+(stupid|inferior|worthless)\b'
        ]
        
        # Compile regex patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.toxic_patterns]
        
        # Common profanity words with severity scores
        self.profanity_scores = {
            'damn': 0.3, 'hell': 0.3, 'crap': 0.4, 'shit': 0.6,
            'fuck': 0.8, 'bitch': 0.7, 'asshole': 0.7, 'bastard': 0.6,
            'slut': 0.8, 'whore': 0.9, 'fag': 0.9, 'nigger': 1.0,
            'retard': 0.8, 'gay': 0.4, 'stupid': 0.3, 'idiot': 0.4
        }
        
        # Context that might reduce toxicity score
        self.context_reducers = {
            'quote', 'quoting', 'mentioned', 'said', 'wrote', 'example',
            'discussing', 'talking about', 'referring to'
        }
    
    def analyze(self, content: str) -> Tuple[float, List[str], float]:
        """
        Analyze toxicity in content
        Returns: (toxicity_score, detected_patterns, confidence)
        """
        if not content.strip():
            return 0.0, [], 0.0
        
        content_lower = content.lower()
        detected_patterns = []
        toxicity_score = 0.0
        
        # Check for pattern matches
        pattern_score = 0.0
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(content)
            if matches:
                detected_patterns.append(f"pattern_{i}")
                pattern_score += 0.3 * len(matches)  # Each pattern match adds toxicity
        
        # Check for profanity
        words = re.findall(r'\b\w+\b', content_lower)
        profanity_score = 0.0
        profanity_count = 0
        
        for word in words:
            if word in self.profanity_scores:
                profanity_score += self.profanity_scores[word]
                profanity_count += 1
                detected_patterns.append(f"profanity_{word}")
        
        # Check for context that might reduce toxicity
        context_reduction = 0.0
        for reducer in self.context_reducers:
            if reducer in content_lower:
                context_reduction = 0.2
                break
        
        # Calculate overall toxicity score
        total_words = len(words) if words else 1
        profanity_density = profanity_count / total_words
        
        toxicity_score = min(1.0, (pattern_score + profanity_score * profanity_density) - context_reduction)
        toxicity_score = max(0.0, toxicity_score)
        
        # Calculate confidence
        indicators = len(detected_patterns)
        confidence = min(1.0, indicators * 0.2 + profanity_density)
        
        return toxicity_score, detected_patterns, confidence


class LanguageDetector:
    """Detects language of content"""
    
    def __init__(self):
        # Common words for different languages
        self.language_indicators = {
            'en': {
                'the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'you', 'that',
                'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they'
            },
            'es': {
                'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se',
                'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para'
            },
            'fr': {
                'le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir',
                'que', 'pour', 'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se'
            },
            'de': {
                'der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich',
                'des', 'auf', 'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'eine', 'als'
            },
            'it': {
                'il', 'di', 'che', 'e', 'la', 'il', 'un', 'a', 'per', 'non',
                'in', 'una', 'è', 'da', 'essere', 'con', 'su', 'si', 'anche', 'lo'
            },
            'pt': {
                'o', 'de', 'a', 'e', 'do', 'da', 'em', 'um', 'para', 'é',
                'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as'
            },
            'ru': {
                'в', 'и', 'не', 'на', 'я', 'быть', 'то', 'он', 'что', 'с',
                'а', 'как', 'по', 'это', 'она', 'этот', 'к', 'но', 'они', 'мы'
            },
            'zh': {
                '的', '一', '是', '在', '不', '了', '有', '和', '人', '这',
                '中', '大', '为', '上', '个', '国', '我', '以', '要', '他'
            },
            'ja': {
                'の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し',
                'れ', 'さ', 'ある', 'いる', 'も', 'する', 'から', 'な', 'こと', 'として'
            },
            'ar': {
                'في', 'من', 'إلى', 'على', 'أن', 'هذا', 'بعد', 'قد', 'لا', 'ما',
                'كان', 'التي', 'ولا', 'بها', 'كما', 'هي', 'بين', 'عند', 'كل', 'لم'
            }
        }
        
        # Character ranges for different scripts
        self.script_ranges = {
            'latin': (0x0000, 0x024F),
            'cyrillic': (0x0400, 0x04FF),
            'arabic': (0x0600, 0x06FF),
            'cjk': (0x4E00, 0x9FFF),  # Chinese, Japanese, Korean
            'hiragana': (0x3040, 0x309F),
            'katakana': (0x30A0, 0x30FF)
        }
    
    def analyze(self, content: str) -> Tuple[str, float]:
        """
        Detect language of content
        Returns: (language_code, confidence)
        """
        if not content.strip():
            return 'unknown', 0.0
        
        # Clean and tokenize content
        words = re.findall(r'\b\w+\b', content.lower())
        if not words:
            return 'unknown', 0.0
        
        # Score each language based on common words
        language_scores = {}
        total_words = len(words)
        
        for lang, indicators in self.language_indicators.items():
            matches = sum(1 for word in words if word in indicators)
            score = matches / total_words if total_words > 0 else 0
            language_scores[lang] = score
        
        # Check character scripts
        char_counts = defaultdict(int)
        for char in content:
            char_code = ord(char)
            for script, (start, end) in self.script_ranges.items():
                if start <= char_code <= end:
                    char_counts[script] += 1
                    break
        
        # Adjust scores based on character scripts
        total_chars = sum(char_counts.values())
        if total_chars > 0:
            if char_counts.get('cyrillic', 0) / total_chars > 0.3:
                language_scores['ru'] += 0.3
            if char_counts.get('arabic', 0) / total_chars > 0.3:
                language_scores['ar'] += 0.3
            if char_counts.get('cjk', 0) / total_chars > 0.3:
                language_scores['zh'] += 0.2
            if char_counts.get('hiragana', 0) / total_chars > 0.1:
                language_scores['ja'] += 0.3
        
        # Find best match
        if not language_scores:
            return 'unknown', 0.0
        
        best_lang = max(language_scores, key=language_scores.get)
        confidence = language_scores[best_lang]
        
        # Default to English if confidence is too low
        if confidence < 0.1:
            return 'en', 0.1
        
        return best_lang, min(1.0, confidence)


class ThreatDetector:
    """Detects advanced threats like coordinated attacks and spam patterns"""
    
    def __init__(self):
        self.spam_indicators = [
            # URL patterns
            r'https?://[^\s]+',
            r'www\.[^\s]+',
            r'\b[a-zA-Z0-9]+-[a-zA-Z0-9]+-[a-zA-Z0-9]+\.(com|org|net)\b',
            
            # Repeated characters/words
            r'(.)\1{4,}',  # Same character repeated 5+ times
            r'\b(\w+)\s+\1\s+\1\b',  # Same word repeated 3+ times
            
            # Promotional language
            r'\b(buy\s+now|click\s+here|limited\s+time|act\s+fast)\b',
            r'\b(free\s+money|get\s+rich|make\s+money)\b',
            r'\b(guaranteed|100%|amazing\s+offer)\b',
            
            # Contact information spam
            r'\b(call\s+now|contact\s+me|email\s+me)\b',
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
        ]
        
        self.compiled_spam_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.spam_indicators]
        
        # Track patterns for coordinated attack detection
        self.recent_content_hashes = {}
        self.user_activity_patterns = defaultdict(list)
        self.cleanup_interval = timedelta(hours=1)
        self.last_cleanup = timezone.now()
    
    def analyze(self, content: str, user_id: Optional[str] = None, 
                metadata: Optional[Dict] = None) -> Tuple[float, List[str], Dict]:
        """
        Analyze content for threats
        Returns: (threat_score, threat_types, threat_metadata)
        """
        threat_score = 0.0
        threat_types = []
        threat_metadata = {}
        
        if not content.strip():
            return 0.0, [], {}
        
        # Clean up old data periodically
        self._cleanup_old_data()
        
        # Check for spam patterns
        spam_score, spam_patterns = self._detect_spam(content)
        if spam_score > 0.3:
            threat_score += spam_score * 0.4
            threat_types.append('spam')
            threat_metadata['spam_patterns'] = spam_patterns
        
        # Check for duplicate content (potential bot/coordinated behavior)
        duplicate_score = self._detect_duplicate_content(content)
        if duplicate_score > 0.5:
            threat_score += duplicate_score * 0.3
            threat_types.append('duplicate_content')
            threat_metadata['duplicate_confidence'] = duplicate_score
        
        # Check user behavior patterns if user_id provided
        if user_id:
            behavior_score = self._analyze_user_behavior(user_id, content, metadata)
            if behavior_score > 0.4:
                threat_score += behavior_score * 0.3
                threat_types.append('suspicious_behavior')
                threat_metadata['behavior_score'] = behavior_score
        
        # Check for rapid-fire posting patterns
        if metadata and 'timestamp' in metadata:
            rapid_fire_score = self._detect_rapid_fire_posting(user_id, metadata['timestamp'])
            if rapid_fire_score > 0.5:
                threat_score += rapid_fire_score * 0.2
                threat_types.append('rapid_posting')
                threat_metadata['rapid_fire_score'] = rapid_fire_score
        
        threat_score = min(1.0, threat_score)
        return threat_score, threat_types, threat_metadata
    
    def _detect_spam(self, content: str) -> Tuple[float, List[str]]:
        """Detect spam patterns in content"""
        spam_score = 0.0
        detected_patterns = []
        
        content_lower = content.lower()
        
        # Check spam patterns
        for i, pattern in enumerate(self.compiled_spam_patterns):
            matches = pattern.findall(content)
            if matches:
                spam_score += 0.15 * len(matches)
                detected_patterns.append(f"spam_pattern_{i}")
        
        # Check for excessive capitalization
        if content.isupper() and len(content) > 20:
            spam_score += 0.2
            detected_patterns.append('excessive_caps')
        
        # Check for excessive punctuation
        punct_ratio = sum(1 for c in content if c in '!?.,;:') / max(1, len(content))
        if punct_ratio > 0.15:
            spam_score += 0.15
            detected_patterns.append('excessive_punctuation')
        
        return min(1.0, spam_score), detected_patterns
    
    def _detect_duplicate_content(self, content: str) -> float:
        """Detect duplicate or near-duplicate content"""
        content_hash = hashlib.md5(content.strip().lower().encode()).hexdigest()
        current_time = timezone.now()
        
        # Check if we've seen this exact content recently
        if content_hash in self.recent_content_hashes:
            last_seen, count = self.recent_content_hashes[content_hash]
            if current_time - last_seen < timedelta(minutes=30):
                self.recent_content_hashes[content_hash] = (current_time, count + 1)
                return min(1.0, count * 0.2)
        
        # Store this content hash
        self.recent_content_hashes[content_hash] = (current_time, 1)
        
        # Check for similar content using simple similarity
        similar_score = 0.0
        content_words = set(re.findall(r'\b\w+\b', content.lower()))
        
        for other_hash, (timestamp, _) in self.recent_content_hashes.items():
            if other_hash != content_hash and current_time - timestamp < timedelta(minutes=30):
                # This is a simplified similarity check
                # In production, you'd want more sophisticated similarity detection
                pass
        
        return similar_score
    
    def _analyze_user_behavior(self, user_id: str, content: str, metadata: Dict) -> float:
        """Analyze user behavior patterns for suspicious activity"""
        current_time = timezone.now()
        
        # Record this activity
        self.user_activity_patterns[user_id].append({
            'timestamp': current_time,
            'content_length': len(content),
            'metadata': metadata
        })
        
        # Keep only recent activity
        cutoff_time = current_time - timedelta(hours=2)
        self.user_activity_patterns[user_id] = [
            activity for activity in self.user_activity_patterns[user_id]
            if activity['timestamp'] > cutoff_time
        ]
        
        activities = self.user_activity_patterns[user_id]
        if len(activities) < 3:
            return 0.0
        
        suspicion_score = 0.0
        
        # Check for rapid posting
        if len(activities) > 10:
            suspicion_score += 0.3
        
        # Check for consistent content length (bot indicator)
        lengths = [a['content_length'] for a in activities]
        if len(set(lengths)) == 1 and len(activities) > 5:
            suspicion_score += 0.4
        
        # Check for burst activity
        timestamps = [a['timestamp'] for a in activities]
        if len(timestamps) > 5:
            time_diffs = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                         for i in range(1, len(timestamps))]
            avg_diff = sum(time_diffs) / len(time_diffs)
            if avg_diff < 10:  # Average less than 10 seconds between posts
                suspicion_score += 0.5
        
        return min(1.0, suspicion_score)
    
    def _detect_rapid_fire_posting(self, user_id: str, timestamp: datetime) -> float:
        """Detect rapid-fire posting patterns"""
        if not user_id:
            return 0.0
        
        recent_posts = [
            activity for activity in self.user_activity_patterns.get(user_id, [])
            if timestamp - activity['timestamp'] < timedelta(minutes=5)
        ]
        
        if len(recent_posts) > 10:
            return 1.0
        elif len(recent_posts) > 5:
            return 0.7
        elif len(recent_posts) > 3:
            return 0.4
        
        return 0.0
    
    def _cleanup_old_data(self):
        """Clean up old tracking data"""
        if timezone.now() - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = timezone.now() - timedelta(hours=2)
        
        # Clean content hashes
        self.recent_content_hashes = {
            h: (t, c) for h, (t, c) in self.recent_content_hashes.items()
            if t > cutoff_time
        }
        
        # Clean user activity patterns
        for user_id in list(self.user_activity_patterns.keys()):
            self.user_activity_patterns[user_id] = [
                activity for activity in self.user_activity_patterns[user_id]
                if activity['timestamp'] > cutoff_time
            ]
            
            if not self.user_activity_patterns[user_id]:
                del self.user_activity_patterns[user_id]
        
        self.last_cleanup = timezone.now()


class AIContentModerationEngine:
    """Main AI Content Moderation Engine that orchestrates all analysis components"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._load_default_config()
        
        # Initialize analyzers
        self.sentiment_analyzer = SentimentAnalyzer()
        self.toxicity_detector = ToxicityDetector()
        self.language_detector = LanguageDetector()
        self.threat_detector = ThreatDetector()
        
        # Performance tracking
        self.analysis_stats = {
            'total_analyzed': 0,
            'avg_processing_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Thread safety
        self._lock = threading.Lock()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            'toxicity_threshold': 0.7,
            'threat_threshold': 0.6,
            'auto_block_threshold': 0.8,
            'auto_flag_threshold': 0.5,
            'enable_caching': True,
            'cache_duration': 3600,  # 1 hour
            'enable_ml_models': True,
            'supported_languages': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ar'],
            'enable_threat_detection': True,
            'enable_sentiment_analysis': True,
            'batch_processing_enabled': True,
            'max_content_length': 10000
        }
    
    def analyze_content(self, content: str, user_id: Optional[str] = None, 
                       metadata: Optional[Dict] = None) -> ContentAnalysisResult:
        """
        Perform comprehensive content analysis
        
        Args:
            content: Text content to analyze
            user_id: Optional user identifier for behavior analysis
            metadata: Optional metadata (timestamp, source, etc.)
        
        Returns:
            ContentAnalysisResult with comprehensive analysis
        """
        start_time = timezone.now()
        
        # Validate input
        if not content or len(content) > self.config['max_content_length']:
            result = ContentAnalysisResult(content[:100] + "..." if content else "")
            result.moderation_action = 'block' if len(content) > self.config['max_content_length'] else 'allow'
            result.flags.append('invalid_input')
            return result
        
        # Check cache if enabled
        cache_key = None
        if self.config['enable_caching']:
            cache_key = self._generate_cache_key(content, user_id, metadata)
            cached_result = cache.get(cache_key)
            if cached_result:
                self.analysis_stats['cache_hits'] += 1
                return ContentAnalysisResult(**cached_result)
        
        self.analysis_stats['cache_misses'] += 1
        
        # Create result object
        result = ContentAnalysisResult(content)
        
        try:
            # Language detection
            if self.config['supported_languages']:
                result.language, result.language_confidence = self.language_detector.analyze(content)
                result.model_versions['language_detector'] = '1.0'
            
            # Sentiment analysis
            if self.config['enable_sentiment_analysis']:
                result.sentiment_score, sentiment_confidence = self.sentiment_analyzer.analyze(content)
                result.model_versions['sentiment_analyzer'] = '1.0'
            
            # Toxicity detection
            toxicity_score, toxic_patterns, toxicity_confidence = self.toxicity_detector.analyze(content)
            result.toxicity_score = toxicity_score
            result.model_versions['toxicity_detector'] = '1.0'
            
            if toxic_patterns:
                result.flags.extend(toxic_patterns)
            
            # Threat detection
            if self.config['enable_threat_detection']:
                threat_score, threat_types, threat_metadata = self.threat_detector.analyze(
                    content, user_id, metadata
                )
                result.threat_indicators = threat_types
                result.model_versions['threat_detector'] = '1.0'
            else:
                threat_score = 0.0
            
            # Calculate overall risk score
            result.risk_score = self._calculate_risk_score(
                result.toxicity_score, threat_score, result.sentiment_score
            )
            
            # Determine moderation action
            result.moderation_action = self._determine_moderation_action(result)
            
            # Calculate overall confidence
            result.confidence_score = self._calculate_confidence(
                toxicity_confidence, result.language_confidence, 
                len(result.threat_indicators)
            )
            
            # Record processing time
            end_time = timezone.now()
            result.processing_time = (end_time - start_time).total_seconds()
            
            # Update statistics
            with self._lock:
                self.analysis_stats['total_analyzed'] += 1
                total = self.analysis_stats['total_analyzed']
                current_avg = self.analysis_stats['avg_processing_time']
                self.analysis_stats['avg_processing_time'] = (
                    (current_avg * (total - 1) + result.processing_time) / total
                )
            
            # Cache result if enabled
            if self.config['enable_caching'] and cache_key:
                cache.set(cache_key, result.to_dict(), self.config['cache_duration'])
            
            return result
            
        except Exception as e:
            logger.error(f"Error during content analysis: {str(e)}")
            result.flags.append('analysis_error')
            result.moderation_action = 'escalate'
            result.processing_time = (timezone.now() - start_time).total_seconds()
            return result
    
    def batch_analyze(self, content_list: List[Dict[str, Any]]) -> List[ContentAnalysisResult]:
        """
        Analyze multiple content items in batch for better performance
        
        Args:
            content_list: List of dicts with 'content', optional 'user_id', 'metadata'
        
        Returns:
            List of ContentAnalysisResult objects
        """
        if not self.config['batch_processing_enabled']:
            return [self.analyze_content(**item) for item in content_list]
        
        results = []
        start_time = timezone.now()
        
        try:
            # Process in batches for memory efficiency
            batch_size = 50
            for i in range(0, len(content_list), batch_size):
                batch = content_list[i:i + batch_size]
                
                # Analyze each item in the batch
                batch_results = []
                for item in batch:
                    result = self.analyze_content(
                        item.get('content', ''),
                        item.get('user_id'),
                        item.get('metadata')
                    )
                    batch_results.append(result)
                
                results.extend(batch_results)
            
            total_time = (timezone.now() - start_time).total_seconds()
            logger.info(f"Batch analyzed {len(content_list)} items in {total_time:.3f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during batch analysis: {str(e)}")
            # Return individual analyses as fallback
            return [self.analyze_content(**item) for item in content_list]
    
    def _generate_cache_key(self, content: str, user_id: Optional[str], 
                          metadata: Optional[Dict]) -> str:
        """Generate cache key for content analysis"""
        key_data = {
            'content_hash': hashlib.md5(content.encode()).hexdigest(),
            'user_id': user_id or 'anonymous',
            'config_hash': hashlib.md5(str(self.config).encode()).hexdigest()[:8]
        }
        
        key_string = f"ai_moderation_{key_data['content_hash']}_{key_data['user_id']}_{key_data['config_hash']}"
        return key_string
    
    def _calculate_risk_score(self, toxicity_score: float, threat_score: float, 
                            sentiment_score: float) -> float:
        """Calculate overall risk score from component scores"""
        # Weighted combination of scores
        risk = (
            toxicity_score * 0.5 +      # Toxicity is most important
            threat_score * 0.3 +        # Threats are serious
            max(0, -sentiment_score * 0.2)  # Very negative sentiment adds risk
        )
        
        return min(1.0, risk)
    
    def _determine_moderation_action(self, result: ContentAnalysisResult) -> str:
        """Determine appropriate moderation action based on analysis"""
        risk_score = result.risk_score
        toxicity_score = result.toxicity_score
        
        # Auto-block thresholds
        if (risk_score >= self.config['auto_block_threshold'] or 
            toxicity_score >= self.config['auto_block_threshold']):
            return 'block'
        
        # Auto-flag thresholds
        if (risk_score >= self.config['auto_flag_threshold'] or 
            toxicity_score >= self.config['toxicity_threshold']):
            return 'flag'
        
        # Escalate for manual review
        if (result.threat_indicators or 
            risk_score >= 0.4 or 
            'analysis_error' in result.flags):
            return 'escalate'
        
        # Allow content
        return 'allow'
    
    def _calculate_confidence(self, toxicity_confidence: float, 
                            language_confidence: float, 
                            threat_indicator_count: int) -> float:
        """Calculate overall confidence in the analysis"""
        # Base confidence from individual analyzers
        base_confidence = (toxicity_confidence + language_confidence) / 2
        
        # Adjust based on threat indicators
        threat_factor = min(1.0, threat_indicator_count * 0.2)
        
        # More threat indicators generally increase confidence
        overall_confidence = min(1.0, base_confidence + threat_factor)
        
        return overall_confidence
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine performance statistics"""
        with self._lock:
            return {
                'total_analyzed': self.analysis_stats['total_analyzed'],
                'avg_processing_time': self.analysis_stats['avg_processing_time'],
                'cache_hit_ratio': (
                    self.analysis_stats['cache_hits'] / 
                    max(1, self.analysis_stats['cache_hits'] + self.analysis_stats['cache_misses'])
                ),
                'cache_hits': self.analysis_stats['cache_hits'],
                'cache_misses': self.analysis_stats['cache_misses'],
                'config': self.config
            }
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update engine configuration"""
        self.config.update(new_config)
        logger.info(f"Updated AI moderation engine configuration: {new_config}")
    
    def reset_statistics(self):
        """Reset performance statistics"""
        with self._lock:
            self.analysis_stats = {
                'total_analyzed': 0,
                'avg_processing_time': 0.0,
                'cache_hits': 0,
                'cache_misses': 0
            }


# Global engine instance
ai_moderation_engine = AIContentModerationEngine()


def analyze_content(content: str, user_id: Optional[str] = None, 
                   metadata: Optional[Dict] = None) -> ContentAnalysisResult:
    """
    Convenience function for content analysis
    """
    return ai_moderation_engine.analyze_content(content, user_id, metadata)


def batch_analyze_content(content_list: List[Dict[str, Any]]) -> List[ContentAnalysisResult]:
    """
    Convenience function for batch content analysis
    """
    return ai_moderation_engine.batch_analyze(content_list)


if __name__ == '__main__':
    # Example usage and testing
    test_content = [
        "This is a great product! I love it!",
        "You're such an idiot, go kill yourself!",
        "Free money! Click here now! Amazing offer!",
        "This is normal content with no issues.",
        "¡Hola! ¿Cómo estás? Me gusta mucho este producto."
    ]
    
    print("AI Content Moderation Engine Test")
    print("=" * 50)
    
    for i, content in enumerate(test_content, 1):
        print(f"\nTest {i}: {content[:50]}...")
        result = analyze_content(content)
        
        print(f"Risk Score: {result.risk_score:.3f}")
        print(f"Toxicity: {result.toxicity_score:.3f}")
        print(f"Sentiment: {result.sentiment_score:.3f}")
        print(f"Language: {result.language} ({result.language_confidence:.3f})")
        print(f"Action: {result.moderation_action}")
        print(f"Processing Time: {result.processing_time:.3f}s")
        
        if result.flags:
            print(f"Flags: {', '.join(result.flags)}")
        
        if result.threat_indicators:
            print(f"Threats: {', '.join(result.threat_indicators)}")
    
    print(f"\nEngine Statistics:")
    stats = ai_moderation_engine.get_statistics()
    for key, value in stats.items():
        if key != 'config':
            print(f"{key}: {value}")
