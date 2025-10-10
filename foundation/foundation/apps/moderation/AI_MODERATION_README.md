# AI Content Moderation Engine

## Overview

The AI Content Moderation Engine is a comprehensive, real-time content moderation system that provides automated analysis and classification of user-generated content. It includes multi-algorithm analysis, threat detection, behavior pattern recognition, and integrated human review workflows.

## Features

### Core AI Capabilities
- **Multi-Algorithm Analysis**: Combines sentiment analysis, toxicity detection, language identification, and threat assessment
- **Real-Time Processing**: Sub-second analysis with caching for improved performance
- **Multi-Language Support**: Supports 10+ languages including English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, and Arabic
- **Advanced Threat Detection**: Identifies spam, coordinated attacks, bot behavior, and rapid-fire posting patterns
- **Machine Learning Integration**: Extensible framework for custom ML models with performance tracking

### Content Analysis Features
- **Sentiment Analysis**: Scores content from -1.0 (negative) to 1.0 (positive) with context-aware modifiers
- **Toxicity Detection**: Identifies harmful content using pattern matching and profanity scoring
- **Language Detection**: Automatic language identification with confidence scoring
- **Threat Assessment**: Detects spam patterns, duplicate content, and suspicious user behavior
- **Content Classification**: Categorizes content and extracts keywords and entities

### Automated Moderation Actions
- **Allow**: Safe content that passes all checks
- **Flag**: Content requiring human review
- **Block**: High-risk content automatically blocked
- **Escalate**: Critical content requiring immediate attention

### Human Review Integration
- **Moderation Queue**: Organized queue system with SLA tracking
- **Priority Management**: Critical, urgent, high, normal, and low priority levels
- **Review Workflows**: Assign, review, approve/deny with detailed notes
- **Appeal System**: User appeal process with reviewer assignment
- **Performance Tracking**: Review time, agreement rates, and override statistics

### Real-Time Monitoring & Alerts
- **Live Dashboard**: Real-time metrics and system health monitoring
- **Alert System**: Configurable thresholds with warning and critical alerts
- **Performance Metrics**: Processing time, accuracy, cache hit rates
- **Trend Analysis**: Historical data analysis and growth tracking
- **SLA Monitoring**: Queue management and response time tracking

## Architecture

### Core Components

1. **AI Engine** (`ai_engine.py`)
   - Main orchestration engine
   - Multi-algorithm analysis pipeline
   - Caching and performance optimization
   - Configuration management

2. **Analysis Components**
   - `SentimentAnalyzer`: Sentiment scoring with intensity modifiers
   - `ToxicityDetector`: Pattern-based toxicity detection
   - `LanguageDetector`: Multi-script language identification
   - `ThreatDetector`: Advanced threat and spam detection

3. **Database Models** (`ai_models.py`)
   - `AIContentModerationResult`: Analysis results storage
   - `UserBehaviorPattern`: Behavioral pattern tracking
   - `AIModerationQueue`: Human review queue management
   - `MLModelVersion`: Model versioning and performance tracking
   - `AIPerformanceMetrics`: Daily performance statistics

4. **API Layer** (`ai_views.py`)
   - RESTful API endpoints
   - Batch processing support
   - Queue management interfaces
   - Performance monitoring endpoints

5. **Monitoring Dashboard** (`dashboard.py`)
   - Real-time metrics aggregation
   - Alert generation and management
   - Trend analysis and reporting
   - Health check functionality

## Installation & Setup

### Requirements
- Django 3.2+
- PostgreSQL (for JSON field support)
- Redis (for caching)
- Python 3.8+

### Installation
```bash
# Install required packages
pip install django psycopg2-binary redis django-redis

# Add to INSTALLED_APPS in settings.py
INSTALLED_APPS = [
    'moderation',
    # ... other apps
]

# Configure caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Run migrations
python manage.py makemigrations moderation
python manage.py migrate
```

### URL Configuration
```python
# In your main urls.py
from django.urls import path, include

urlpatterns = [
    path('moderation/ai/', include('moderation.ai_urls')),
    # ... other URLs
]
```

## API Usage

### Content Analysis
```python
# Single content analysis
POST /moderation/ai/api/analyze/
{
    "content": "This is the content to analyze",
    "user_id": 123,
    "content_type": "comment",
    "source_url": "https://example.com/post/456"
}

# Response
{
    "content_id": "uuid-here",
    "moderation_action": "allow",
    "risk_score": 0.15,
    "confidence_score": 0.89,
    "sentiment_score": 0.23,
    "toxicity_score": 0.05,
    "detected_language": "en",
    "threat_indicators": [],
    "flags": [],
    "processing_time": 0.045,
    "needs_review": false,
    "timestamp": "2024-01-15T10:30:45Z"
}
```

### Batch Analysis
```python
# Batch processing
POST /moderation/ai/api/batch-analyze/
{
    "content_list": [
        {"content": "First piece of content", "user_id": 123},
        {"content": "Second piece of content", "user_id": 124},
        "Simple string content"
    ]
}

# Response
{
    "batch_id": "batch_20240115_103045",
    "total_items": 3,
    "results": [...],
    "summary": {
        "allowed": 2,
        "flagged": 1,
        "blocked": 0,
        "escalated": 0,
        "avg_processing_time": 0.038
    }
}
```

### Moderation Queue
```python
# Get queue items
GET /moderation/ai/api/queue/?status=pending&priority=high

# Update queue item
POST /moderation/ai/api/queue/
{
    "item_id": 123,
    "action": "complete",
    "decision": "allow",
    "notes": "Content is acceptable after review"
}
```

### Performance Monitoring
```python
# Get performance metrics
GET /moderation/ai/api/performance/?days=7

# Health check
GET /moderation/ai/api/health/
```

## Configuration

### Engine Configuration
```python
# Default configuration
config = {
    'toxicity_threshold': 0.7,
    'threat_threshold': 0.6,
    'auto_block_threshold': 0.8,
    'auto_flag_threshold': 0.5,
    'enable_sentiment_analysis': True,
    'enable_threat_detection': True,
    'enable_caching': True,
    'cache_duration': 3600,
    'supported_languages': ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ar'],
    'max_content_length': 10000,
    'batch_processing_enabled': True
}

# Update configuration via API
POST /moderation/ai/api/config/
{
    "config": {
        "toxicity_threshold": 0.6,
        "auto_flag_threshold": 0.4
    }
}
```

### Alert Thresholds
```python
# Monitoring alert thresholds
alert_thresholds = {
    'high_risk_ratio': 0.15,         # Alert if >15% high risk content
    'queue_overdue_count': 50,       # Alert if >50 overdue items
    'avg_processing_time': 2.0,      # Alert if >2s avg processing
    'low_confidence_ratio': 0.3,     # Alert if >30% low confidence
    'sla_breach_ratio': 0.1,         # Alert if >10% SLA breaches
    'human_override_ratio': 0.25,    # Alert if >25% human overrides
}
```

## Advanced Usage

### Custom Models Integration
```python
from moderation.ai_models import MLModelVersion

# Register new model version
model = MLModelVersion.objects.create(
    model_name='custom_toxicity_detector',
    model_type='toxicity',
    version='2.1.0',
    description='Enhanced toxicity detection model',
    accuracy_score=0.94,
    is_active=True
)
```

### Behavior Pattern Analysis
```python
# Query user behavior patterns
from moderation.ai_models import UserBehaviorPattern

patterns = UserBehaviorPattern.objects.filter(
    user_id=123,
    risk_level__in=['high', 'critical'],
    created_at__gte=timezone.now() - timedelta(days=7)
)

for pattern in patterns:
    print(f"Pattern: {pattern.behavior_type}, Risk: {pattern.risk_level}")
    print(f"Confidence: {pattern.confidence_score}")
    print(f"Data: {pattern.pattern_data}")
```

### Custom Analysis Pipeline
```python
from moderation.ai_engine import ai_moderation_engine, analyze_content

# Analyze content with custom metadata
result = analyze_content(
    content="Content to analyze",
    user_id=123,
    metadata={
        'source_url': 'https://example.com/post/456',
        'content_type': 'forum_post',
        'timestamp': timezone.now(),
        'additional_context': {'topic': 'politics', 'forum': 'general'}
    }
)

print(f"Action: {result.moderation_action}")
print(f"Risk Score: {result.risk_score}")
print(f"Threats: {result.threat_indicators}")
```

### Dashboard Integration
```python
from moderation.dashboard import get_dashboard_data

# Get real-time metrics
metrics = get_dashboard_data('realtime')
print(f"Total analyzed (last hour): {metrics['activity']['last_hour']['total_analyzed']}")

# Get trend analysis
trends = get_dashboard_data('trends', days=30)
print(f"Growth rate: {trends['growth_rate_percent']:.1f}%")

# Get alert status
alerts = get_dashboard_data('alerts')
print(f"Health status: {alerts['health_status']}")
for alert in alerts['alerts']:
    print(f"Alert: {alert['message']}")
```

## Performance Optimization

### Caching Strategy
- **Content Analysis**: 1-hour cache for identical content analysis
- **Dashboard Metrics**: 1-minute cache for real-time data, 10-minute cache for trends
- **User Behavior**: 15-minute cache for behavior summaries
- **Model Performance**: 1-hour cache for performance breakdowns

### Batch Processing
- Process up to 100 items per batch request
- Memory-efficient processing in chunks of 50 items
- Automatic fallback to individual analysis on batch failure

### Database Optimization
- Indexed fields for common queries
- Automatic cleanup of old tracking data
- Signal-based metrics aggregation
- Optimized query patterns with select_related and prefetch_related

## Monitoring & Alerts

### Health Check Endpoint
```bash
curl http://localhost:8000/moderation/ai/api/health/
```

### Key Metrics to Monitor
- **Processing Time**: Average content analysis time
- **Queue Health**: Pending items and SLA breaches
- **Model Performance**: Confidence scores and human override rates
- **Threat Detection**: Pattern detection rates and false positives
- **System Resources**: Cache hit ratios and database performance

### Alert Categories
- **Content Quality**: High risk content ratios, low confidence predictions
- **Queue Management**: Overdue items, SLA breaches
- **Performance**: High processing times, low cache hit ratios
- **Model Accuracy**: High human override rates, accuracy degradation

## Security Considerations

### Data Privacy
- Content preview limited to 500 characters in database
- Full content not stored, only analysis results
- User data anonymization options available
- GDPR compliance features for data deletion

### API Security
- Authentication required for queue management endpoints
- Permission-based access control
- Rate limiting recommendations for public endpoints
- Input validation and sanitization

### Threat Mitigation
- Real-time detection of coordinated attacks
- Bot behavior identification and blocking
- Spam pattern recognition with adaptive thresholds
- User behavior analysis for sockpuppet detection

## Extending the System

### Adding Custom Analyzers
```python
class CustomAnalyzer:
    def analyze(self, content: str) -> Tuple[float, float]:
        # Your custom analysis logic
        score = self.calculate_score(content)
        confidence = self.calculate_confidence(content)
        return score, confidence

# Register with the engine
ai_moderation_engine.add_analyzer('custom', CustomAnalyzer())
```

### Custom Threat Detection
```python
class CustomThreatDetector:
    def analyze(self, content: str, user_id: str, metadata: dict) -> Tuple[float, List[str], dict]:
        # Your threat detection logic
        return threat_score, threat_types, metadata

# Integration with existing system
threat_detector = CustomThreatDetector()
```

## Testing

### Unit Tests
```python
# Test content analysis
from moderation.ai_engine import analyze_content

def test_content_analysis():
    result = analyze_content("This is a test message")
    assert result.moderation_action in ['allow', 'flag', 'block', 'escalate']
    assert 0 <= result.risk_score <= 1
    assert 0 <= result.confidence_score <= 1
```

### Performance Testing
```python
# Benchmark processing time
import time
from moderation.ai_engine import batch_analyze_content

content_list = [{"content": f"Test message {i}"} for i in range(100)]
start_time = time.time()
results = batch_analyze_content(content_list)
processing_time = time.time() - start_time

print(f"Processed {len(results)} items in {processing_time:.2f} seconds")
print(f"Average: {processing_time / len(results):.4f} seconds per item")
```

## Migration & Deployment

### Database Migrations
```bash
# Create and apply migrations
python manage.py makemigrations moderation
python manage.py migrate

# Create initial performance metrics
python manage.py shell -c "
from moderation.ai_models import AIPerformanceMetrics
from datetime import date
AIPerformanceMetrics.objects.get_or_create(date=date.today())
"
```

### Production Deployment
1. Configure Redis for caching
2. Set up database indexes
3. Configure monitoring and alerting
4. Set up log aggregation
5. Configure rate limiting
6. Set up automated backups

### Scaling Considerations
- Horizontal scaling with load balancers
- Database read replicas for analytics
- Redis clustering for cache distribution
- Async task processing for batch operations
- CDN integration for static assets

## Support & Maintenance

### Regular Maintenance Tasks
- Monitor alert thresholds and adjust as needed
- Review model performance and retrain if necessary
- Clean up old data according to retention policies
- Update language models and pattern databases
- Performance optimization based on usage patterns

### Troubleshooting
- Check health endpoint for system status
- Review alert logs for performance issues
- Monitor database query performance
- Analyze cache hit ratios
- Review processing time trends

### Performance Tuning
- Adjust cache timeouts based on usage
- Optimize database queries
- Tune alert thresholds
- Update model configurations
- Scale resources based on load

## License & Contributing

This AI Content Moderation Engine is part of the Data Destroyer project. See the main project documentation for licensing and contribution guidelines.

For technical support or feature requests, please refer to the main project repository.
