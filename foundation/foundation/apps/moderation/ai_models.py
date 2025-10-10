"""
Django models for AI Content Moderation Engine

These models store AI-powered moderation results, user behavior patterns, and system configurations
for the comprehensive AI-powered content moderation system including machine learning integration.
"""

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField, ArrayField
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
import uuid


class AIContentModerationResult(models.Model):
    """Results from AI content moderation analysis"""
    
    MODERATION_ACTIONS = [
        ('allow', 'Allow'),
        ('flag', 'Flag for Review'),
        ('block', 'Block'),
        ('escalate', 'Escalate to Human'),
    ]
    
    CONTENT_TYPES = [
        ('text', 'Text'),
        ('comment', 'Comment'),
        ('review', 'Review'),
        ('post', 'Post'),
        ('message', 'Message'),
        ('upload', 'Upload'),
        ('other', 'Other'),
    ]
    
    # Identification
    content_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    content_hash = models.CharField(max_length=64, db_index=True, help_text="MD5 hash of content")
    
    # Content metadata
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='text')
    content_preview = models.TextField(max_length=500, help_text="First 500 chars of content")
    content_length = models.IntegerField()
    source_url = models.URLField(blank=True, null=True)
    source_ip = models.GenericIPAddressField(blank=True, null=True)
    
    # User information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    # AI Analysis results
    sentiment_score = models.FloatField(
        validators=[MinValueValidator(-1.0), MaxValueValidator(1.0)],
        help_text="Sentiment score (-1.0 to 1.0)"
    )
    toxicity_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Toxicity score (0.0 to 1.0)"
    )
    risk_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Overall risk score (0.0 to 1.0)"
    )
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Analysis confidence (0.0 to 1.0)"
    )
    
    # Language detection
    detected_language = models.CharField(max_length=10, default='en')
    language_confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        default=0.0
    )
    
    # Classification results
    categories = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="Detected content categories"
    )
    keywords = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Extracted keywords"
    )
    entities = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Named entities"
    )
    
    # Threat indicators
    threat_indicators = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="Detected threat types"
    )
    
    # Flags and patterns
    flags = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True,
        help_text="Analysis flags and detected patterns"
    )
    
    # Moderation decision
    moderation_action = models.CharField(max_length=20, choices=MODERATION_ACTIONS)
    action_reason = models.TextField(blank=True, help_text="Reason for moderation action")
    
    # AI Model performance metrics
    processing_time = models.FloatField(help_text="Processing time in seconds")
    model_versions = JSONField(default=dict, help_text="AI model versions used")
    
    # Review and override
    human_reviewed = models.BooleanField(default=False)
    human_reviewer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='ai_reviewed_content'
    )
    human_decision = models.CharField(
        max_length=20, 
        choices=MODERATION_ACTIONS, 
        blank=True,
        help_text="Human reviewer decision"
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    is_appealed = models.BooleanField(default=False)
    appeal_status = models.CharField(max_length=20, blank=True)
    final_action = models.CharField(
        max_length=20, 
        choices=MODERATION_ACTIONS,
        help_text="Final action after any reviews/appeals"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_content_moderation_results'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_hash']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['moderation_action', '-created_at']),
            models.Index(fields=['risk_score', '-created_at']),
            models.Index(fields=['human_reviewed', '-created_at']),
            models.Index(fields=['detected_language', '-created_at']),
        ]
    
    def __str__(self):
        return f"AI Moderation Result {self.content_id} - {self.moderation_action}"
    
    def get_absolute_url(self):
        return reverse('moderation:ai_result_detail', kwargs={'content_id': self.content_id})
    
    @property
    def needs_human_review(self):
        """Check if content needs human review"""
        return (
            self.moderation_action in ['flag', 'escalate'] and 
            not self.human_reviewed
        )
    
    @property
    def is_high_risk(self):
        """Check if content is high risk"""
        return self.risk_score >= 0.7
    
    @property
    def effective_action(self):
        """Get the effective moderation action (considering human review)"""
        if self.human_reviewed and self.human_decision:
            return self.human_decision
        return self.moderation_action


class UserBehaviorPattern(models.Model):
    """Track user behavior patterns for advanced threat detection"""
    
    BEHAVIOR_TYPES = [
        ('posting_frequency', 'Posting Frequency'),
        ('content_similarity', 'Content Similarity'),
        ('spam_indicators', 'Spam Indicators'),
        ('coordinated_activity', 'Coordinated Activity'),
        ('rapid_fire', 'Rapid Fire Posting'),
        ('suspicious_timing', 'Suspicious Timing'),
        ('bot_behavior', 'Bot-like Behavior'),
        ('sockpuppet', 'Sockpuppet Account'),
    ]
    
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_behavior_patterns')
    behavior_type = models.CharField(max_length=50, choices=BEHAVIOR_TYPES)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    
    # Pattern details
    pattern_data = JSONField(default=dict, help_text="Detailed pattern data")
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence in pattern detection"
    )
    
    # Time window
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.IntegerField(help_text="Pattern duration in minutes")
    
    # Related content
    related_results = models.ManyToManyField(
        AIContentModerationResult,
        blank=True,
        help_text="Content moderation results related to this pattern"
    )
    
    # Actions taken
    action_taken = models.CharField(max_length=100, blank=True)
    action_effective = models.BooleanField(null=True, blank=True)
    
    # Metadata
    detection_algorithm = models.CharField(max_length=100)
    false_positive = models.BooleanField(null=True, blank=True)
    verified_by_human = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_user_behavior_patterns'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['behavior_type', 'risk_level']),
            models.Index(fields=['start_time', 'end_time']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.behavior_type} ({self.risk_level})"


class AIModerationQueue(models.Model):
    """Queue for content requiring human review from AI moderation"""
    
    QUEUE_TYPES = [
        ('ai_flagged', 'AI Flagged Content'),
        ('ai_escalated', 'AI Escalated Content'),
        ('appealed_ai', 'Appealed AI Decisions'),
        ('high_risk_ai', 'High Risk AI Content'),
        ('pattern_detected', 'Behavior Pattern Detected'),
        ('false_positive', 'Potential False Positive'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low Priority'),
        ('normal', 'Normal Priority'),
        ('high', 'High Priority'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    # Queue identification
    queue_type = models.CharField(max_length=50, choices=QUEUE_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Content reference
    ai_moderation_result = models.ForeignKey(
        AIContentModerationResult,
        on_delete=models.CASCADE,
        related_name='ai_queue_items'
    )
    behavior_pattern = models.ForeignKey(
        UserBehaviorPattern,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ai_queue_items'
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_ai_moderation_items'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Processing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    processing_time = models.IntegerField(null=True, blank=True, help_text="Processing time in seconds")
    
    # Notes and context
    context_notes = models.TextField(blank=True, help_text="Additional context for reviewers")
    internal_notes = models.TextField(blank=True, help_text="Internal reviewer notes")
    
    # SLA tracking
    target_response_time = models.IntegerField(help_text="Target response time in minutes")
    sla_breached = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_moderation_queue'
        ordering = ['priority', '-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['queue_type', 'status']),
            models.Index(fields=['sla_breached', 'created_at']),
        ]
    
    def __str__(self):
        return f"AI Queue Item {self.id} - {self.queue_type} ({self.priority})"


class MLModelVersion(models.Model):
    """Track different versions of ML models used in content moderation"""
    
    MODEL_TYPES = [
        ('sentiment', 'Sentiment Analysis'),
        ('toxicity', 'Toxicity Detection'),
        ('language', 'Language Detection'),
        ('threat', 'Threat Detection'),
        ('spam', 'Spam Detection'),
        ('content_classifier', 'Content Classification'),
        ('behavior_analysis', 'Behavior Analysis'),
    ]
    
    model_name = models.CharField(max_length=100)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    version = models.CharField(max_length=50)
    
    # Model metadata
    description = models.TextField(blank=True)
    training_data_size = models.IntegerField(null=True, blank=True)
    accuracy_score = models.FloatField(null=True, blank=True)
    precision_score = models.FloatField(null=True, blank=True)
    recall_score = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    
    # Model configuration
    hyperparameters = JSONField(default=dict, blank=True)
    feature_config = JSONField(default=dict, blank=True)
    
    # Deployment info
    is_active = models.BooleanField(default=False)
    deployment_date = models.DateTimeField(null=True, blank=True)
    retirement_date = models.DateTimeField(null=True, blank=True)
    
    # Performance tracking
    total_predictions = models.IntegerField(default=0)
    avg_inference_time = models.FloatField(default=0.0)
    false_positive_rate = models.FloatField(null=True, blank=True)
    false_negative_rate = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ml_model_versions'
        ordering = ['-created_at']
        unique_together = ['model_name', 'version']
    
    def __str__(self):
        return f"{self.model_name} v{self.version} ({self.model_type})"


class AIPerformanceMetrics(models.Model):
    """Daily performance metrics for AI moderation system"""
    
    date = models.DateField(unique=True)
    
    # Volume metrics
    total_analyzed = models.IntegerField(default=0)
    total_allowed = models.IntegerField(default=0)
    total_flagged = models.IntegerField(default=0)
    total_blocked = models.IntegerField(default=0)
    total_escalated = models.IntegerField(default=0)
    
    # AI-specific metrics
    avg_sentiment_score = models.FloatField(default=0.0)
    avg_toxicity_score = models.FloatField(default=0.0)
    avg_risk_score = models.FloatField(default=0.0)
    avg_confidence_score = models.FloatField(default=0.0)
    
    # Language distribution
    language_distribution = JSONField(default=dict, help_text="Distribution by detected language")
    
    # Performance metrics
    avg_processing_time = models.FloatField(default=0.0)
    cache_hit_ratio = models.FloatField(default=0.0)
    model_accuracy = models.FloatField(default=0.0)
    
    # Human review metrics
    items_reviewed = models.IntegerField(default=0)
    avg_review_time = models.FloatField(default=0.0)
    ai_human_agreement_rate = models.FloatField(default=0.0)
    human_overrides = models.IntegerField(default=0)
    
    # Threat detection metrics
    threats_detected = models.IntegerField(default=0)
    spam_detected = models.IntegerField(default=0)
    coordinated_attacks = models.IntegerField(default=0)
    behavior_patterns_detected = models.IntegerField(default=0)
    
    # Model performance breakdown
    model_performance = JSONField(default=dict, help_text="Performance by model type")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_performance_metrics'
        ordering = ['-date']
    
    def __str__(self):
        return f"AI Performance Metrics for {self.date}"


class ContentAppeal(models.Model):
    """User appeals for AI moderation decisions"""
    
    APPEAL_STATUS = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Appeal Approved'),
        ('denied', 'Appeal Denied'),
        ('invalid', 'Invalid Appeal'),
    ]
    
    # Appeal identification
    appeal_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Related content
    ai_moderation_result = models.ForeignKey(
        AIContentModerationResult,
        on_delete=models.CASCADE,
        related_name='ai_appeals'
    )
    
    # Appeal details
    appellant = models.ForeignKey(User, on_delete=models.CASCADE)
    appeal_reason = models.TextField(help_text="User's reason for appeal")
    supporting_evidence = models.TextField(blank=True)
    
    # Review process
    status = models.CharField(max_length=20, choices=APPEAL_STATUS, default='pending')
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_ai_appeals'
    )
    review_notes = models.TextField(blank=True)
    final_decision = models.CharField(
        max_length=20, 
        choices=AIContentModerationResult.MODERATION_ACTIONS, 
        blank=True
    )
    decision_reason = models.TextField(blank=True)
    
    # AI feedback integration
    ai_confidence_at_appeal = models.FloatField(null=True, blank=True)
    model_retrained = models.BooleanField(default=False)
    training_feedback_provided = models.BooleanField(default=False)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'ai_content_appeals'
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['status', '-submitted_at']),
            models.Index(fields=['appellant', '-submitted_at']),
            models.Index(fields=['reviewer', 'status']),
        ]
    
    def __str__(self):
        return f"AI Appeal {self.appeal_id} - {self.status}"
    
    def get_absolute_url(self):
        return reverse('moderation:ai_appeal_detail', kwargs={'appeal_id': self.appeal_id})


class AITrainingData(models.Model):
    """Store training data for ML model improvement"""
    
    DATA_TYPES = [
        ('content_sample', 'Content Sample'),
        ('user_feedback', 'User Feedback'),
        ('human_review', 'Human Review Result'),
        ('appeal_outcome', 'Appeal Outcome'),
        ('false_positive', 'False Positive Example'),
        ('false_negative', 'False Negative Example'),
    ]
    
    data_type = models.CharField(max_length=50, choices=DATA_TYPES)
    content_hash = models.CharField(max_length=64, db_index=True)
    
    # Training labels
    ground_truth_action = models.CharField(
        max_length=20, 
        choices=AIContentModerationResult.MODERATION_ACTIONS
    )
    ground_truth_scores = JSONField(default=dict, help_text="True scores for training")
    
    # Context data
    content_metadata = JSONField(default=dict)
    user_context = JSONField(default=dict, blank=True)
    
    # Validation
    is_validated = models.BooleanField(default=False)
    validated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    validation_confidence = models.FloatField(null=True, blank=True)
    
    # Usage tracking
    used_in_training = models.BooleanField(default=False)
    training_runs = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_training_data'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['data_type', '-created_at']),
            models.Index(fields=['is_validated', 'used_in_training']),
            models.Index(fields=['content_hash']),
        ]
    
    def __str__(self):
        return f"Training Data {self.id} - {self.data_type}"


# Signal handlers for automatic metrics updates
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Avg
from datetime import date

@receiver(post_save, sender=AIContentModerationResult)
def update_ai_performance_metrics(sender, instance, created, **kwargs):
    """Update daily AI performance metrics when new results are created"""
    if created:
        today = date.today()
        metrics, created = AIPerformanceMetrics.objects.get_or_create(date=today)
        
        # Update basic counts
        metrics.total_analyzed += 1
        
        if instance.moderation_action == 'allow':
            metrics.total_allowed += 1
        elif instance.moderation_action == 'flag':
            metrics.total_flagged += 1
        elif instance.moderation_action == 'block':
            metrics.total_blocked += 1
        elif instance.moderation_action == 'escalate':
            metrics.total_escalated += 1
        
        # Update language distribution
        lang_dist = metrics.language_distribution
        lang = instance.detected_language
        lang_dist[lang] = lang_dist.get(lang, 0) + 1
        metrics.language_distribution = lang_dist
        
        # Update averages (simplified - in production you'd want more sophisticated aggregation)
        all_today = AIContentModerationResult.objects.filter(created_at__date=today)
        metrics.avg_processing_time = all_today.aggregate(Avg('processing_time'))['processing_time__avg'] or 0.0
        metrics.avg_sentiment_score = all_today.aggregate(Avg('sentiment_score'))['sentiment_score__avg'] or 0.0
        metrics.avg_toxicity_score = all_today.aggregate(Avg('toxicity_score'))['toxicity_score__avg'] or 0.0
        metrics.avg_risk_score = all_today.aggregate(Avg('risk_score'))['risk_score__avg'] or 0.0
        metrics.avg_confidence_score = all_today.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0.0
        
        metrics.save()


@receiver(post_save, sender=UserBehaviorPattern)
def update_behavior_pattern_metrics(sender, instance, created, **kwargs):
    """Update metrics when behavior patterns are detected"""
    if created:
        today = date.today()
        metrics, created = AIPerformanceMetrics.objects.get_or_create(date=today)
        
        metrics.behavior_patterns_detected += 1
        
        if instance.behavior_type == 'spam_indicators':
            metrics.spam_detected += 1
        elif instance.behavior_type == 'coordinated_activity':
            metrics.coordinated_attacks += 1
        
        metrics.save()
