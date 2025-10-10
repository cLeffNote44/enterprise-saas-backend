"""
Real-time monitoring dashboard for AI Content Moderation Engine

Provides comprehensive monitoring, alerting, and visualization capabilities
for the AI moderation system performance and health.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Avg, Max, Min, Q, F
from django.contrib.auth.models import User

from .ai_models import (
    AIContentModerationResult, UserBehaviorPattern, AIModerationQueue,
    MLModelVersion, AIPerformanceMetrics, ContentAppeal
)
from .ai_engine import ai_moderation_engine

logger = logging.getLogger(__name__)


class AIMonitoringDashboard:
    """Comprehensive monitoring dashboard for AI moderation system"""
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
        self.alert_thresholds = {
            'high_risk_ratio': 0.15,        # Alert if >15% high risk content
            'queue_overdue_count': 50,       # Alert if >50 overdue items
            'avg_processing_time': 2.0,      # Alert if >2s avg processing
            'low_confidence_ratio': 0.3,     # Alert if >30% low confidence
            'sla_breach_ratio': 0.1,         # Alert if >10% SLA breaches
            'human_override_ratio': 0.25,    # Alert if >25% human overrides
        }
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        cache_key = 'ai_moderation_realtime_metrics'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Calculate real-time metrics
        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_24h = now - timedelta(hours=24)
        
        # Recent activity metrics
        recent_results = AIContentModerationResult.objects.filter(created_at__gte=last_hour)
        daily_results = AIContentModerationResult.objects.filter(created_at__gte=last_24h)
        
        # Processing metrics
        total_analyzed_hour = recent_results.count()
        total_analyzed_day = daily_results.count()
        
        if total_analyzed_hour > 0:
            action_distribution_hour = {
                'allow': recent_results.filter(moderation_action='allow').count(),
                'flag': recent_results.filter(moderation_action='flag').count(),
                'block': recent_results.filter(moderation_action='block').count(),
                'escalate': recent_results.filter(moderation_action='escalate').count(),
            }
            
            avg_scores_hour = recent_results.aggregate(
                avg_risk=Avg('risk_score'),
                avg_confidence=Avg('confidence_score'),
                avg_processing_time=Avg('processing_time'),
                max_risk=Max('risk_score'),
                min_confidence=Min('confidence_score')
            )
            
            high_risk_count = recent_results.filter(risk_score__gte=0.7).count()
            low_confidence_count = recent_results.filter(confidence_score__lt=0.5).count()
        else:
            action_distribution_hour = {'allow': 0, 'flag': 0, 'block': 0, 'escalate': 0}
            avg_scores_hour = {}
            high_risk_count = 0
            low_confidence_count = 0
        
        # Queue metrics
        queue_stats = self._get_queue_statistics()
        
        # Engine performance
        engine_stats = ai_moderation_engine.get_statistics()
        
        # Threat detection
        threat_patterns = UserBehaviorPattern.objects.filter(
            created_at__gte=last_hour
        ).values('behavior_type').annotate(count=Count('id'))
        
        # Human review metrics
        reviewed_items = recent_results.filter(human_reviewed=True)
        human_overrides = reviewed_items.exclude(
            moderation_action=F('human_decision')
        ).count()
        
        metrics = {
            'timestamp': now.isoformat(),
            'activity': {
                'last_hour': {
                    'total_analyzed': total_analyzed_hour,
                    'actions': action_distribution_hour,
                    'high_risk_count': high_risk_count,
                    'low_confidence_count': low_confidence_count,
                },
                'last_24h': {
                    'total_analyzed': total_analyzed_day,
                    'hourly_rate': total_analyzed_day / 24,
                }
            },
            'performance': {
                'avg_processing_time': avg_scores_hour.get('avg_processing_time', 0),
                'cache_hit_ratio': engine_stats.get('cache_hit_ratio', 0),
                'engine_stats': engine_stats,
            },
            'quality': {
                'avg_risk_score': avg_scores_hour.get('avg_risk', 0),
                'avg_confidence': avg_scores_hour.get('avg_confidence', 0),
                'max_risk_score': avg_scores_hour.get('max_risk', 0),
                'min_confidence': avg_scores_hour.get('min_confidence', 1),
                'high_risk_ratio': high_risk_count / max(1, total_analyzed_hour),
                'low_confidence_ratio': low_confidence_count / max(1, total_analyzed_hour),
            },
            'queue': queue_stats,
            'threats': {
                'patterns_detected': [
                    {'type': item['behavior_type'], 'count': item['count']}
                    for item in threat_patterns
                ],
                'total_patterns': sum(item['count'] for item in threat_patterns)
            },
            'human_review': {
                'items_reviewed': reviewed_items.count(),
                'override_count': human_overrides,
                'override_ratio': human_overrides / max(1, reviewed_items.count())
            }
        }
        
        # Cache for 1 minute
        cache.set(cache_key, metrics, 60)
        return metrics
    
    def _get_queue_statistics(self) -> Dict[str, Any]:
        """Get detailed queue statistics"""
        now = timezone.now()
        
        # Basic queue counts
        pending_count = AIModerationQueue.objects.filter(status='pending').count()
        in_progress_count = AIModerationQueue.objects.filter(status='in_progress').count()
        
        # SLA metrics
        overdue_items = AIModerationQueue.objects.filter(
            status__in=['pending', 'in_progress'],
            sla_breached=True
        )
        overdue_count = overdue_items.count()
        
        # Priority distribution
        priority_dist = AIModerationQueue.objects.filter(
            status__in=['pending', 'in_progress']
        ).values('priority').annotate(count=Count('id'))
        
        # Average wait times
        avg_wait_time = AIModerationQueue.objects.filter(
            status='pending'
        ).aggregate(
            avg_wait=Avg(
                (now - F('created_at')).total_seconds() / 60
            )
        )['avg_wait'] or 0
        
        return {
            'pending': pending_count,
            'in_progress': in_progress_count,
            'overdue': overdue_count,
            'total_active': pending_count + in_progress_count,
            'avg_wait_time_minutes': avg_wait_time,
            'priority_distribution': {
                item['priority']: item['count'] for item in priority_dist
            },
            'sla_breach_ratio': overdue_count / max(1, pending_count + in_progress_count)
        }
    
    def get_trend_analysis(self, days: int = 7) -> Dict[str, Any]:
        """Get trend analysis over specified days"""
        cache_key = f'ai_moderation_trends_{days}d'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Get daily metrics
        daily_metrics = AIPerformanceMetrics.objects.filter(
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # Calculate trends
        trend_data = []
        for metric in daily_metrics:
            trend_data.append({
                'date': metric.date.isoformat(),
                'total_analyzed': metric.total_analyzed,
                'action_distribution': {
                    'allow': metric.total_allowed,
                    'flag': metric.total_flagged,
                    'block': metric.total_blocked,
                    'escalate': metric.total_escalated,
                },
                'avg_risk_score': metric.avg_risk_score,
                'avg_confidence': metric.avg_confidence_score,
                'avg_processing_time': metric.avg_processing_time,
                'threats_detected': metric.threats_detected,
                'spam_detected': metric.spam_detected,
                'human_overrides': metric.human_overrides,
                'sla_compliance': metric.sla_compliance_rate,
            })
        
        # Calculate period aggregates
        if daily_metrics:
            period_totals = {
                'total_analyzed': sum(m.total_analyzed for m in daily_metrics),
                'total_threats': sum(m.threats_detected for m in daily_metrics),
                'avg_risk_score': sum(m.avg_risk_score for m in daily_metrics) / len(daily_metrics),
                'avg_processing_time': sum(m.avg_processing_time for m in daily_metrics) / len(daily_metrics),
                'sla_compliance': sum(m.sla_compliance_rate for m in daily_metrics) / len(daily_metrics),
            }
        else:
            period_totals = {}
        
        # Growth calculations
        if len(trend_data) >= 2:
            recent_avg = sum(d['total_analyzed'] for d in trend_data[-3:]) / min(3, len(trend_data))
            early_avg = sum(d['total_analyzed'] for d in trend_data[:3]) / min(3, len(trend_data))
            growth_rate = ((recent_avg - early_avg) / max(1, early_avg)) * 100 if early_avg > 0 else 0
        else:
            growth_rate = 0
        
        trends = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'daily_data': trend_data,
            'period_totals': period_totals,
            'growth_rate_percent': growth_rate,
            'timestamp': timezone.now().isoformat()
        }
        
        # Cache for 10 minutes
        cache.set(cache_key, trends, 600)
        return trends
    
    def get_alert_status(self) -> Dict[str, Any]:
        """Check system health and generate alerts"""
        metrics = self.get_real_time_metrics()
        alerts = []
        warning_count = 0
        critical_count = 0
        
        # Check high risk content ratio
        high_risk_ratio = metrics['quality']['high_risk_ratio']
        if high_risk_ratio > self.alert_thresholds['high_risk_ratio']:
            alerts.append({
                'type': 'warning',
                'category': 'content_quality',
                'message': f'High risk content ratio: {high_risk_ratio:.1%}',
                'threshold': self.alert_thresholds['high_risk_ratio'],
                'current_value': high_risk_ratio,
                'timestamp': timezone.now().isoformat()
            })
            warning_count += 1
        
        # Check queue overdue items
        overdue_count = metrics['queue']['overdue']
        if overdue_count > self.alert_thresholds['queue_overdue_count']:
            severity = 'critical' if overdue_count > 100 else 'warning'
            alerts.append({
                'type': severity,
                'category': 'queue_management',
                'message': f'{overdue_count} overdue queue items',
                'threshold': self.alert_thresholds['queue_overdue_count'],
                'current_value': overdue_count,
                'timestamp': timezone.now().isoformat()
            })
            if severity == 'critical':
                critical_count += 1
            else:
                warning_count += 1
        
        # Check processing time
        avg_processing_time = metrics['performance']['avg_processing_time']
        if avg_processing_time > self.alert_thresholds['avg_processing_time']:
            alerts.append({
                'type': 'warning',
                'category': 'performance',
                'message': f'High average processing time: {avg_processing_time:.2f}s',
                'threshold': self.alert_thresholds['avg_processing_time'],
                'current_value': avg_processing_time,
                'timestamp': timezone.now().isoformat()
            })
            warning_count += 1
        
        # Check low confidence ratio
        low_confidence_ratio = metrics['quality']['low_confidence_ratio']
        if low_confidence_ratio > self.alert_thresholds['low_confidence_ratio']:
            alerts.append({
                'type': 'warning',
                'category': 'model_quality',
                'message': f'High low-confidence predictions: {low_confidence_ratio:.1%}',
                'threshold': self.alert_thresholds['low_confidence_ratio'],
                'current_value': low_confidence_ratio,
                'timestamp': timezone.now().isoformat()
            })
            warning_count += 1
        
        # Check SLA breach ratio
        sla_breach_ratio = metrics['queue']['sla_breach_ratio']
        if sla_breach_ratio > self.alert_thresholds['sla_breach_ratio']:
            severity = 'critical' if sla_breach_ratio > 0.2 else 'warning'
            alerts.append({
                'type': severity,
                'category': 'sla_management',
                'message': f'SLA breach ratio: {sla_breach_ratio:.1%}',
                'threshold': self.alert_thresholds['sla_breach_ratio'],
                'current_value': sla_breach_ratio,
                'timestamp': timezone.now().isoformat()
            })
            if severity == 'critical':
                critical_count += 1
            else:
                warning_count += 1
        
        # Check human override ratio
        override_ratio = metrics['human_review']['override_ratio']
        if override_ratio > self.alert_thresholds['human_override_ratio']:
            alerts.append({
                'type': 'warning',
                'category': 'model_accuracy',
                'message': f'High human override ratio: {override_ratio:.1%}',
                'threshold': self.alert_thresholds['human_override_ratio'],
                'current_value': override_ratio,
                'timestamp': timezone.now().isoformat()
            })
            warning_count += 1
        
        # Overall health status
        if critical_count > 0:
            health_status = 'critical'
        elif warning_count > 0:
            health_status = 'warning'
        else:
            health_status = 'healthy'
        
        return {
            'health_status': health_status,
            'alert_counts': {
                'critical': critical_count,
                'warning': warning_count,
                'total': len(alerts)
            },
            'alerts': alerts,
            'thresholds': self.alert_thresholds,
            'last_check': timezone.now().isoformat()
        }
    
    def get_user_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get user activity and behavior summary"""
        cache_key = f'ai_moderation_user_activity_{hours}h'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        start_time = timezone.now() - timedelta(hours=hours)
        
        # User behavior patterns
        behavior_patterns = UserBehaviorPattern.objects.filter(
            created_at__gte=start_time
        )
        
        # Risk level distribution
        risk_distribution = behavior_patterns.values('risk_level').annotate(
            count=Count('id')
        )
        
        # Behavior type distribution
        behavior_distribution = behavior_patterns.values('behavior_type').annotate(
            count=Count('id')
        )
        
        # Top users by risk patterns
        top_risk_users = behavior_patterns.filter(
            risk_level__in=['high', 'critical']
        ).values('user__username').annotate(
            pattern_count=Count('id'),
            max_risk_level=Max('risk_level')
        ).order_by('-pattern_count')[:10]
        
        # Most common threats
        threat_summary = behavior_patterns.filter(
            behavior_type__in=['spam_indicators', 'coordinated_activity', 'bot_behavior']
        ).values('behavior_type').annotate(count=Count('id'))
        
        summary = {
            'period_hours': hours,
            'total_patterns': behavior_patterns.count(),
            'risk_distribution': {
                item['risk_level']: item['count'] for item in risk_distribution
            },
            'behavior_distribution': {
                item['behavior_type']: item['count'] for item in behavior_distribution
            },
            'top_risk_users': list(top_risk_users),
            'threat_summary': {
                item['behavior_type']: item['count'] for item in threat_summary
            },
            'timestamp': timezone.now().isoformat()
        }
        
        # Cache for 15 minutes
        cache.set(cache_key, summary, 900)
        return summary
    
    def get_model_performance_breakdown(self) -> Dict[str, Any]:
        """Get detailed model performance breakdown"""
        # Get active models
        active_models = MLModelVersion.objects.filter(is_active=True)
        
        # Recent results for analysis
        recent_results = AIContentModerationResult.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        )
        
        model_performance = {}
        for model in active_models:
            # Get results that used this model version
            model_results = recent_results.filter(
                model_versions__contains={model.model_type: model.version}
            )
            
            if model_results.exists():
                performance_data = model_results.aggregate(
                    avg_processing_time=Avg('processing_time'),
                    avg_confidence=Avg('confidence_score'),
                    total_predictions=Count('id')
                )
                
                # Calculate accuracy if human reviews are available
                reviewed = model_results.filter(human_reviewed=True)
                if reviewed.exists():
                    correct_predictions = reviewed.filter(
                        moderation_action=F('human_decision')
                    ).count()
                    accuracy = correct_predictions / reviewed.count()
                else:
                    accuracy = None
                
                model_performance[f"{model.model_name}_v{model.version}"] = {
                    'type': model.model_type,
                    'avg_processing_time': performance_data['avg_processing_time'],
                    'avg_confidence': performance_data['avg_confidence'],
                    'total_predictions': performance_data['total_predictions'],
                    'accuracy': accuracy,
                    'deployment_date': model.deployment_date.isoformat() if model.deployment_date else None
                }
        
        return {
            'models': model_performance,
            'timestamp': timezone.now().isoformat()
        }
    
    def generate_summary_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        # Get all metrics
        real_time = self.get_real_time_metrics()
        trends = self.get_trend_analysis(days)
        alerts = self.get_alert_status()
        user_activity = self.get_user_activity_summary(24)
        model_performance = self.get_model_performance_breakdown()
        
        # Calculate key insights
        insights = []
        
        # Volume trends
        if trends['period_totals']:
            total_analyzed = trends['period_totals']['total_analyzed']
            daily_average = total_analyzed / days
            insights.append(f"Analyzed {total_analyzed:,} items over {days} days (avg: {daily_average:.0f}/day)")
        
        # Risk patterns
        high_risk_ratio = real_time['quality']['high_risk_ratio']
        if high_risk_ratio > 0.1:
            insights.append(f"High risk content ratio: {high_risk_ratio:.1%}")
        
        # Queue health
        queue_health = "good" if alerts['alert_counts']['critical'] == 0 else "needs attention"
        insights.append(f"Queue health: {queue_health}")
        
        # Model accuracy
        avg_confidence = real_time['quality']['avg_confidence']
        insights.append(f"Average model confidence: {avg_confidence:.1%}")
        
        return {
            'report_period': {
                'days': days,
                'generated_at': timezone.now().isoformat()
            },
            'executive_summary': {
                'health_status': alerts['health_status'],
                'key_insights': insights,
                'alert_counts': alerts['alert_counts']
            },
            'metrics': {
                'real_time': real_time,
                'trends': trends,
                'alerts': alerts,
                'user_activity': user_activity,
                'model_performance': model_performance
            }
        }


# Global dashboard instance
ai_dashboard = AIMonitoringDashboard()


def get_dashboard_data(request_type: str = 'summary', **kwargs) -> Dict[str, Any]:
    """
    Convenience function to get dashboard data
    
    Args:
        request_type: Type of data requested ('summary', 'realtime', 'trends', 'alerts')
        **kwargs: Additional parameters for specific request types
    
    Returns:
        Dictionary containing requested dashboard data
    """
    try:
        if request_type == 'realtime':
            return ai_dashboard.get_real_time_metrics()
        elif request_type == 'trends':
            days = kwargs.get('days', 7)
            return ai_dashboard.get_trend_analysis(days)
        elif request_type == 'alerts':
            return ai_dashboard.get_alert_status()
        elif request_type == 'user_activity':
            hours = kwargs.get('hours', 24)
            return ai_dashboard.get_user_activity_summary(hours)
        elif request_type == 'model_performance':
            return ai_dashboard.get_model_performance_breakdown()
        elif request_type == 'summary':
            days = kwargs.get('days', 7)
            return ai_dashboard.generate_summary_report(days)
        else:
            return {'error': f'Unknown request type: {request_type}'}
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return {'error': str(e)}


if __name__ == '__main__':
    # Example usage and testing
    dashboard = AIMonitoringDashboard()
    
    print("AI Moderation Dashboard Test")
    print("=" * 50)
    
    # Test real-time metrics
    print("\n--- Real-time Metrics ---")
    metrics = dashboard.get_real_time_metrics()
    print(f"Total analyzed (last hour): {metrics['activity']['last_hour']['total_analyzed']}")
    print(f"Average processing time: {metrics['performance']['avg_processing_time']:.3f}s")
    print(f"High risk ratio: {metrics['quality']['high_risk_ratio']:.1%}")
    
    # Test alerts
    print("\n--- Alert Status ---")
    alerts = dashboard.get_alert_status()
    print(f"Health status: {alerts['health_status']}")
    print(f"Active alerts: {alerts['alert_counts']['total']}")
    for alert in alerts['alerts']:
        print(f"  - {alert['type'].upper()}: {alert['message']}")
    
    # Test trends
    print("\n--- 7-Day Trends ---")
    trends = dashboard.get_trend_analysis(7)
    if trends['period_totals']:
        print(f"Total analyzed: {trends['period_totals']['total_analyzed']:,}")
        print(f"Average risk score: {trends['period_totals']['avg_risk_score']:.3f}")
        print(f"Growth rate: {trends['growth_rate_percent']:.1f}%")
