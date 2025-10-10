"""
URL routing for AI Content Moderation API endpoints
"""

from django.urls import path, include
from . import ai_views

app_name = 'ai_moderation'

urlpatterns = [
    # Content Analysis API
    path('api/analyze/', ai_views.ContentAnalysisAPIView.as_view(), name='analyze_content'),
    path('api/batch-analyze/', ai_views.BatchAnalysisAPIView.as_view(), name='batch_analyze'),
    
    # Moderation Queue Management
    path('api/queue/', ai_views.ModerationQueueAPIView.as_view(), name='moderation_queue'),
    
    # Performance & Monitoring
    path('api/performance/', ai_views.AIPerformanceAPIView.as_view(), name='performance_metrics'),
    path('api/health/', ai_views.HealthCheckAPIView.as_view(), name='health_check'),
    
    # User Behavior Analysis
    path('api/behavior/', ai_views.UserBehaviorAPIView.as_view(), name='user_behavior'),
    
    # Model Configuration
    path('api/config/', ai_views.ModelConfigAPIView.as_view(), name='model_config'),
]
