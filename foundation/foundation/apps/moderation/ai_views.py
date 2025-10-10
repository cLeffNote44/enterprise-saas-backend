"""
API views for AI Content Moderation Engine

Provides REST API endpoints for content analysis, moderation queue management,
and real-time monitoring integration.
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Max, Min
from django.conf import settings
import json

from .ai_engine import ai_moderation_engine, analyze_content, batch_analyze_content
from .ai_models import (
    AIContentModerationResult, UserBehaviorPattern, AIModerationQueue,
    MLModelVersion, AIPerformanceMetrics, ContentAppeal, AITrainingData
)

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class ContentAnalysisAPIView(View):
    """API endpoint for analyzing content with AI moderation"""
    
    def post(self, request):
        """Analyze content for moderation"""
        try:
            data = json.loads(request.body)
            content = data.get('content', '')
            
            if not content:
                return JsonResponse({'error': 'Content is required'}, status=400)
            
            if len(content) > 10000:  # Configurable limit
                return JsonResponse({'error': 'Content too long'}, status=400)
            
            # Extract metadata
            user_id = data.get('user_id')
            metadata = {
                'source_url': data.get('source_url'),
                'content_type': data.get('content_type', 'text'),
                'timestamp': timezone.now(),
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'session_id': data.get('session_id', ''),
            }
            
            # Perform AI analysis
            result = analyze_content(content, user_id, metadata)
            
            # Store result in database
            db_result = self._store_analysis_result(result, content, user_id, metadata)
            
            # Check if human review is needed and add to queue
            if result.moderation_action in ['flag', 'escalate']:
                self._add_to_moderation_queue(db_result, result.moderation_action)
            
            # Prepare response
            response_data = {
                'content_id': str(db_result.content_id),
                'moderation_action': result.moderation_action,
                'risk_score': result.risk_score,
                'confidence_score': result.confidence_score,
                'sentiment_score': result.sentiment_score,
                'toxicity_score': result.toxicity_score,
                'detected_language': result.language,
                'threat_indicators': result.threat_indicators,
                'flags': result.flags,
                'processing_time': result.processing_time,
                'needs_review': db_result.needs_human_review,
                'timestamp': db_result.created_at.isoformat()
            }
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error in content analysis: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _store_analysis_result(self, result, content, user_id, metadata):
        """Store analysis result in database"""
        from django.contrib.auth.models import User
        
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        db_result = AIContentModerationResult.objects.create(
            content_hash=result._generate_content_id().split('_')[-1],  # Extract hash part
            content_type=metadata.get('content_type', 'text'),
            content_preview=content[:500],
            content_length=len(content),
            source_url=metadata.get('source_url'),
            source_ip=metadata.get('ip_address'),
            user=user,
            user_agent=metadata.get('user_agent', ''),
            session_id=metadata.get('session_id', ''),
            sentiment_score=result.sentiment_score,
            toxicity_score=result.toxicity_score,
            risk_score=result.risk_score,
            confidence_score=result.confidence_score,
            detected_language=result.language,
            language_confidence=result.language_confidence,
            categories=result.categories,
            keywords=result.keywords,
            entities=result.entities,
            threat_indicators=result.threat_indicators,
            flags=result.flags,
            moderation_action=result.moderation_action,
            processing_time=result.processing_time,
            model_versions=result.model_versions,
            final_action=result.moderation_action  # Initially same as moderation_action
        )
        
        return db_result
    
    def _add_to_moderation_queue(self, db_result, action):
        """Add content to moderation queue"""
        queue_type = 'ai_flagged' if action == 'flag' else 'ai_escalated'
        priority = 'high' if action == 'escalate' else 'normal'
        
        if db_result.is_high_risk:
            queue_type = 'high_risk_ai'
            priority = 'urgent' if db_result.risk_score >= 0.9 else 'high'
        
        AIModerationQueue.objects.create(
            queue_type=queue_type,
            priority=priority,
            ai_moderation_result=db_result,
            context_notes=f"AI {action}: Risk score {db_result.risk_score:.3f}, "
                         f"Confidence {db_result.confidence_score:.3f}"
        )


@method_decorator(csrf_exempt, name='dispatch')
class BatchAnalysisAPIView(View):
    """API endpoint for batch content analysis"""
    
    def post(self, request):
        """Analyze multiple content items in batch"""
        try:
            data = json.loads(request.body)
            content_list = data.get('content_list', [])
            
            if not content_list:
                return JsonResponse({'error': 'Content list is required'}, status=400)
            
            if len(content_list) > 100:  # Configurable limit
                return JsonResponse({'error': 'Too many items in batch (max 100)'}, status=400)
            
            # Prepare batch data
            batch_data = []
            for i, item in enumerate(content_list):
                if isinstance(item, str):
                    # Simple string content
                    batch_data.append({'content': item})
                elif isinstance(item, dict):
                    # Content with metadata
                    batch_data.append(item)
                else:
                    return JsonResponse({'error': f'Invalid content format at index {i}'}, status=400)
            
            # Perform batch analysis
            results = batch_analyze_content(batch_data)
            
            # Store results and prepare response
            response_items = []
            for result, original_item in zip(results, batch_data):
                # Store in database
                db_result = self._store_batch_result(result, original_item)
                
                # Add to queue if needed
                if result.moderation_action in ['flag', 'escalate']:
                    self._add_to_moderation_queue(db_result, result.moderation_action)
                
                response_items.append({
                    'content_id': str(db_result.content_id),
                    'moderation_action': result.moderation_action,
                    'risk_score': result.risk_score,
                    'confidence_score': result.confidence_score,
                    'processing_time': result.processing_time
                })
            
            return JsonResponse({
                'batch_id': f"batch_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
                'total_items': len(results),
                'results': response_items,
                'summary': {
                    'allowed': sum(1 for r in results if r.moderation_action == 'allow'),
                    'flagged': sum(1 for r in results if r.moderation_action == 'flag'),
                    'blocked': sum(1 for r in results if r.moderation_action == 'block'),
                    'escalated': sum(1 for r in results if r.moderation_action == 'escalate'),
                    'avg_processing_time': sum(r.processing_time for r in results) / len(results)
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error in batch analysis: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    def _store_batch_result(self, result, item):
        """Store batch analysis result"""
        content = item.get('content', '')
        user_id = item.get('user_id')
        
        from django.contrib.auth.models import User
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass
        
        return AIContentModerationResult.objects.create(
            content_hash=result._generate_content_id().split('_')[-1],
            content_type=item.get('content_type', 'text'),
            content_preview=content[:500],
            content_length=len(content),
            user=user,
            sentiment_score=result.sentiment_score,
            toxicity_score=result.toxicity_score,
            risk_score=result.risk_score,
            confidence_score=result.confidence_score,
            detected_language=result.language,
            language_confidence=result.language_confidence,
            threat_indicators=result.threat_indicators,
            flags=result.flags,
            moderation_action=result.moderation_action,
            processing_time=result.processing_time,
            model_versions=result.model_versions,
            final_action=result.moderation_action
        )
    
    def _add_to_moderation_queue(self, db_result, action):
        """Add batch result to moderation queue"""
        queue_type = 'ai_flagged' if action == 'flag' else 'ai_escalated'
        priority = 'normal'  # Batch items get normal priority by default
        
        AIModerationQueue.objects.create(
            queue_type=queue_type,
            priority=priority,
            ai_moderation_result=db_result,
            context_notes=f"Batch AI {action}: Risk score {db_result.risk_score:.3f}"
        )


class ModerationQueueAPIView(View):
    """API for managing AI moderation queue"""
    
    @method_decorator(login_required)
    @method_decorator(permission_required('moderation.view_aimoderationqueue'))
    def get(self, request):
        """Get moderation queue items"""
        try:
            # Parse query parameters
            status = request.GET.get('status', 'pending')
            queue_type = request.GET.get('queue_type')
            priority = request.GET.get('priority')
            assigned_to = request.GET.get('assigned_to')
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)
            
            # Build query
            queryset = AIModerationQueue.objects.select_related(
                'ai_moderation_result', 'assigned_to'
            )
            
            if status:
                queryset = queryset.filter(status=status)
            if queue_type:
                queryset = queryset.filter(queue_type=queue_type)
            if priority:
                queryset = queryset.filter(priority=priority)
            if assigned_to:
                if assigned_to == 'me':
                    queryset = queryset.filter(assigned_to=request.user)
                else:
                    queryset = queryset.filter(assigned_to_id=assigned_to)
            
            # Paginate
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # Serialize results
            items = []
            for item in page_obj:
                result = item.ai_moderation_result
                items.append({
                    'id': item.id,
                    'queue_type': item.queue_type,
                    'priority': item.priority,
                    'status': item.status,
                    'content_id': str(result.content_id),
                    'content_preview': result.content_preview[:200] + '...' if len(result.content_preview) > 200 else result.content_preview,
                    'risk_score': result.risk_score,
                    'moderation_action': result.moderation_action,
                    'assigned_to': item.assigned_to.username if item.assigned_to else None,
                    'created_at': item.created_at.isoformat(),
                    'time_remaining': item.time_remaining,
                    'sla_breached': item.sla_breached,
                    'context_notes': item.context_notes
                })
            
            return JsonResponse({
                'items': items,
                'pagination': {
                    'page': page,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous()
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting moderation queue: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    @method_decorator(permission_required('moderation.change_aimoderationqueue'))
    def post(self, request):
        """Update queue item status"""
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            action = data.get('action')  # assign, start, complete, skip
            
            item = get_object_or_404(AIModerationQueue, id=item_id)
            
            if action == 'assign':
                item.assigned_to = request.user
                item.assigned_at = timezone.now()
                item.status = 'in_progress'
                item.started_at = timezone.now()
                
            elif action == 'start':
                if item.assigned_to != request.user:
                    return JsonResponse({'error': 'Item not assigned to you'}, status=403)
                item.status = 'in_progress'
                item.started_at = timezone.now()
                
            elif action == 'complete':
                if item.assigned_to != request.user:
                    return JsonResponse({'error': 'Item not assigned to you'}, status=403)
                
                # Update the AI result with human decision
                decision = data.get('decision')
                notes = data.get('notes', '')
                
                if decision:
                    result = item.ai_moderation_result
                    result.human_reviewed = True
                    result.human_reviewer = request.user
                    result.human_decision = decision
                    result.review_notes = notes
                    result.reviewed_at = timezone.now()
                    result.final_action = decision
                    result.save()
                
                item.status = 'completed'
                item.completed_at = timezone.now()
                item.internal_notes = notes
                
                # Calculate processing time
                if item.started_at:
                    processing_time = (timezone.now() - item.started_at).total_seconds()
                    item.processing_time = int(processing_time)
                
            elif action == 'skip':
                item.status = 'skipped'
                item.completed_at = timezone.now()
                item.internal_notes = data.get('reason', 'Skipped by reviewer')
            
            item.save()
            
            return JsonResponse({
                'success': True,
                'item': {
                    'id': item.id,
                    'status': item.status,
                    'assigned_to': item.assigned_to.username if item.assigned_to else None,
                    'updated_at': item.updated_at.isoformat()
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error updating queue item: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


class AIPerformanceAPIView(View):
    """API for AI performance metrics and monitoring"""
    
    def get(self, request):
        """Get AI performance metrics"""
        try:
            # Parse date range
            days = int(request.GET.get('days', 7))
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            # Get daily metrics
            daily_metrics = AIPerformanceMetrics.objects.filter(
                date__range=[start_date, end_date]
            ).order_by('date')
            
            # Get current engine statistics
            engine_stats = ai_moderation_engine.get_statistics()
            
            # Recent results for trend analysis
            recent_results = AIContentModerationResult.objects.filter(
                created_at__date__range=[start_date, end_date]
            )
            
            # Calculate aggregated metrics
            total_analyzed = recent_results.count()
            if total_analyzed > 0:
                action_distribution = {
                    'allow': recent_results.filter(moderation_action='allow').count(),
                    'flag': recent_results.filter(moderation_action='flag').count(),
                    'block': recent_results.filter(moderation_action='block').count(),
                    'escalate': recent_results.filter(moderation_action='escalate').count(),
                }
                
                avg_scores = recent_results.aggregate(
                    avg_risk=Avg('risk_score'),
                    avg_confidence=Avg('confidence_score'),
                    avg_toxicity=Avg('toxicity_score'),
                    avg_sentiment=Avg('sentiment_score'),
                    avg_processing_time=Avg('processing_time')
                )
                
                # Language distribution
                language_dist = {}
                for result in recent_results.values('detected_language').annotate(count=Count('id')):
                    language_dist[result['detected_language']] = result['count']
            else:
                action_distribution = {'allow': 0, 'flag': 0, 'block': 0, 'escalate': 0}
                avg_scores = {}
                language_dist = {}
            
            # Human review metrics
            reviewed_items = recent_results.filter(human_reviewed=True)
            human_overrides = reviewed_items.exclude(
                moderation_action=models.F('human_decision')
            ).count()
            
            # Queue metrics
            queue_stats = {
                'pending': AIModerationQueue.objects.filter(status='pending').count(),
                'in_progress': AIModerationQueue.objects.filter(status='in_progress').count(),
                'overdue': AIModerationQueue.objects.filter(
                    status__in=['pending', 'in_progress'],
                    sla_breached=True
                ).count()
            }
            
            # Prepare response
            response_data = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'summary': {
                    'total_analyzed': total_analyzed,
                    'action_distribution': action_distribution,
                    'avg_scores': avg_scores,
                    'language_distribution': language_dist,
                    'human_review': {
                        'items_reviewed': reviewed_items.count(),
                        'human_overrides': human_overrides,
                        'agreement_rate': 1 - (human_overrides / max(1, reviewed_items.count()))
                    }
                },
                'daily_metrics': [
                    {
                        'date': metric.date.isoformat(),
                        'total_analyzed': metric.total_analyzed,
                        'avg_risk_score': metric.avg_risk_score,
                        'avg_processing_time': metric.avg_processing_time,
                        'threats_detected': metric.threats_detected,
                        'spam_detected': metric.spam_detected
                    }
                    for metric in daily_metrics
                ],
                'engine_stats': engine_stats,
                'queue_stats': queue_stats,
                'timestamp': timezone.now().isoformat()
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            logger.error(f"Error getting AI performance metrics: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


class UserBehaviorAPIView(View):
    """API for user behavior pattern analysis"""
    
    @method_decorator(login_required)
    @method_decorator(permission_required('moderation.view_userbehaviorpattern'))
    def get(self, request):
        """Get user behavior patterns"""
        try:
            user_id = request.GET.get('user_id')
            behavior_type = request.GET.get('behavior_type')
            risk_level = request.GET.get('risk_level')
            days = int(request.GET.get('days', 7))
            
            end_time = timezone.now()
            start_time = end_time - timedelta(days=days)
            
            # Build query
            queryset = UserBehaviorPattern.objects.filter(
                created_at__range=[start_time, end_time]
            ).select_related('user')
            
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            if behavior_type:
                queryset = queryset.filter(behavior_type=behavior_type)
            if risk_level:
                queryset = queryset.filter(risk_level=risk_level)
            
            # Serialize patterns
            patterns = []
            for pattern in queryset.order_by('-created_at'):
                patterns.append({
                    'id': pattern.id,
                    'user': {
                        'id': pattern.user.id,
                        'username': pattern.user.username
                    },
                    'behavior_type': pattern.behavior_type,
                    'risk_level': pattern.risk_level,
                    'confidence_score': pattern.confidence_score,
                    'duration_minutes': pattern.duration_minutes,
                    'pattern_data': pattern.pattern_data,
                    'action_taken': pattern.action_taken,
                    'verified_by_human': pattern.verified_by_human,
                    'created_at': pattern.created_at.isoformat()
                })
            
            # Get summary statistics
            risk_distribution = queryset.values('risk_level').annotate(count=Count('id'))
            behavior_distribution = queryset.values('behavior_type').annotate(count=Count('id'))
            
            return JsonResponse({
                'patterns': patterns,
                'summary': {
                    'total_patterns': queryset.count(),
                    'risk_distribution': {item['risk_level']: item['count'] for item in risk_distribution},
                    'behavior_distribution': {item['behavior_type']: item['count'] for item in behavior_distribution},
                },
                'period': {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'days': days
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting behavior patterns: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ModelConfigAPIView(View):
    """API for managing AI model configuration"""
    
    @method_decorator(login_required)
    @method_decorator(permission_required('moderation.view_mlmodelversion'))
    def get(self, request):
        """Get current model versions and configuration"""
        try:
            # Get active models
            active_models = MLModelVersion.objects.filter(is_active=True)
            
            # Get engine configuration
            engine_config = ai_moderation_engine.config
            engine_stats = ai_moderation_engine.get_statistics()
            
            models_info = []
            for model in active_models:
                models_info.append({
                    'id': model.id,
                    'name': model.model_name,
                    'type': model.model_type,
                    'version': model.version,
                    'description': model.description,
                    'accuracy_score': model.accuracy_score,
                    'deployment_date': model.deployment_date.isoformat() if model.deployment_date else None,
                    'total_predictions': model.total_predictions,
                    'avg_inference_time': model.avg_inference_time
                })
            
            return JsonResponse({
                'active_models': models_info,
                'engine_config': engine_config,
                'engine_stats': engine_stats,
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error getting model configuration: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    @method_decorator(login_required)
    @method_decorator(permission_required('moderation.change_mlmodelversion'))
    def post(self, request):
        """Update AI engine configuration"""
        try:
            data = json.loads(request.body)
            config_updates = data.get('config', {})
            
            # Validate configuration keys
            valid_keys = {
                'toxicity_threshold', 'threat_threshold', 'auto_block_threshold',
                'auto_flag_threshold', 'enable_sentiment_analysis', 'enable_threat_detection',
                'enable_caching', 'cache_duration', 'max_content_length'
            }
            
            filtered_config = {k: v for k, v in config_updates.items() if k in valid_keys}
            
            if filtered_config:
                ai_moderation_engine.update_config(filtered_config)
                
                return JsonResponse({
                    'success': True,
                    'updated_config': filtered_config,
                    'timestamp': timezone.now().isoformat()
                })
            else:
                return JsonResponse({'error': 'No valid configuration updates provided'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error updating model configuration: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)


# Health check endpoint for monitoring integration
class HealthCheckAPIView(View):
    """Health check endpoint for monitoring systems"""
    
    def get(self, request):
        """Check AI moderation engine health"""
        try:
            # Test basic engine functionality
            test_result = analyze_content("This is a test message for health check.")
            
            # Check database connectivity
            recent_count = AIContentModerationResult.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            # Check queue status
            pending_queue = AIModerationQueue.objects.filter(status='pending').count()
            overdue_queue = AIModerationQueue.objects.filter(
                status__in=['pending', 'in_progress'],
                sla_breached=True
            ).count()
            
            # Engine statistics
            engine_stats = ai_moderation_engine.get_statistics()
            
            # Determine health status
            health_status = 'healthy'
            issues = []
            
            if test_result.processing_time > 5.0:  # Slow processing
                health_status = 'degraded'
                issues.append('Slow processing times detected')
            
            if overdue_queue > 10:  # Too many overdue items
                health_status = 'degraded'
                issues.append(f'{overdue_queue} overdue queue items')
            
            if engine_stats['avg_processing_time'] > 2.0:
                health_status = 'degraded' 
                issues.append('High average processing time')
            
            return JsonResponse({
                'status': health_status,
                'timestamp': timezone.now().isoformat(),
                'version': '1.0.0',
                'engine_stats': {
                    'total_analyzed': engine_stats['total_analyzed'],
                    'avg_processing_time': engine_stats['avg_processing_time'],
                    'cache_hit_ratio': engine_stats['cache_hit_ratio']
                },
                'queue_stats': {
                    'pending': pending_queue,
                    'overdue': overdue_queue
                },
                'recent_activity': {
                    'last_hour_count': recent_count
                },
                'issues': issues,
                'test_result': {
                    'processing_time': test_result.processing_time,
                    'action': test_result.moderation_action
                }
            })
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return JsonResponse({
                'status': 'unhealthy',
                'timestamp': timezone.now().isoformat(),
                'error': str(e)
            }, status=503)
