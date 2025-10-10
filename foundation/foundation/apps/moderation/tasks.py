"""
Celery tasks for the moderation module.

This module contains background tasks for content moderation including:
- Async content scanning
- Bulk content analysis  
- Policy violation processing
- Cleanup and maintenance tasks
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def scan_content_async(self, content_text, user_id, scan_type='full'):
    """
    Asynchronously scan content for policy violations.
    
    Args:
        content_text (str): The content to scan
        user_id (int): ID of the user requesting the scan
        scan_type (str): Type of scan to perform ('full', 'quick', 'sensitive')
    
    Returns:
        dict: Scan results with violations found
    """
    try:
        from .content_analyzer import ContentAnalyzer
        from django.contrib.auth import get_user_model
        from .models import ContentScan
        
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        # Perform the content analysis
        analyzer = ContentAnalyzer()
        scan_result = analyzer.analyze_content(content_text)
        
        # Create a content scan record
        content_scan = ContentScan.objects.create(
            user=user,
            content_hash=analyzer._generate_content_hash(content_text),
            scan_score=scan_result.scan_score,
            violations_found=scan_result.violations_found,
            processing_time_ms=scan_result.processing_time_ms,
            metadata={
                'scan_type': scan_type,
                'task_id': self.request.id,
                'async': True
            }
        )
        
        logger.info(f"Async content scan completed. Scan ID: {content_scan.id}, "
                   f"Violations: {scan_result.violations_found}, "
                   f"Score: {scan_result.scan_score}")
        
        return {
            'scan_id': content_scan.id,
            'violations_found': scan_result.violations_found,
            'scan_score': scan_result.scan_score,
            'status': 'completed'
        }
        
    except Exception as exc:
        logger.error(f"Content scan task failed: {str(exc)}")
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@shared_task
def bulk_scan_content(content_items, user_id, scan_type='full'):
    """
    Process multiple content items for scanning in parallel.
    
    Args:
        content_items (list): List of content texts to scan
        user_id (int): ID of the user requesting the scans
        scan_type (str): Type of scan to perform
    
    Returns:
        dict: Summary of bulk scan results
    """
    from celery import group
    
    logger.info(f"Starting bulk scan of {len(content_items)} items for user {user_id}")
    
    # Create a group of scan tasks to run in parallel
    job = group(
        scan_content_async.s(content, user_id, scan_type) 
        for content in content_items
    )
    
    # Execute the group and wait for results
    result = job.apply_async()
    results = result.get()  # This will block until all tasks complete
    
    # Aggregate results
    total_violations = sum(r.get('violations_found', 0) for r in results)
    completed_scans = len([r for r in results if r.get('status') == 'completed'])
    
    logger.info(f"Bulk scan completed. {completed_scans}/{len(content_items)} successful, "
               f"Total violations: {total_violations}")
    
    return {
        'total_items': len(content_items),
        'completed_scans': completed_scans,
        'total_violations': total_violations,
        'results': results
    }

@shared_task
def cleanup_expired_scans():
    """
    Clean up old content scans and expired moderation actions.
    
    This task runs periodically to maintain database hygiene.
    """
    from .models import ContentScan, ModerationAction
    
    logger.info("Starting cleanup of expired scans and actions")
    
    # Remove scans older than 90 days
    cutoff_date = timezone.now() - timedelta(days=90)
    old_scans = ContentScan.objects.filter(scanned_at__lt=cutoff_date)
    old_scans_count = old_scans.count()
    old_scans.delete()
    
    # Remove expired moderation actions
    expired_actions = ModerationAction.objects.filter(
        expiry_date__lt=timezone.now(),
        expiry_date__isnull=False
    )
    expired_actions_count = expired_actions.count()
    expired_actions.delete()
    
    logger.info(f"Cleanup completed. Removed {old_scans_count} old scans "
               f"and {expired_actions_count} expired actions")
    
    return {
        'old_scans_removed': old_scans_count,
        'expired_actions_removed': expired_actions_count
    }

@shared_task(bind=True, max_retries=2)
def process_policy_violation(self, violation_id):
    """
    Process a policy violation and determine appropriate actions.
    
    Args:
        violation_id (int): ID of the PolicyViolation to process
    
    Returns:
        dict: Processing results and recommended actions
    """
    try:
        from .models import PolicyViolation, ModerationAction, ActionType, ModerationStatus
        
        violation = PolicyViolation.objects.get(id=violation_id)
        
        logger.info(f"Processing policy violation {violation_id}: {violation.violation_type}")
        
        # Determine recommended actions based on violation severity and type
        recommended_actions = []
        
        if violation.severity.value >= 80:  # Critical violations
            recommended_actions.extend([
                ActionType.QUARANTINE,
                ActionType.NOTIFY_ADMIN
            ])
        elif violation.severity.value >= 60:  # High severity
            recommended_actions.extend([
                ActionType.FLAG_CONTENT,
                ActionType.REQUIRE_REVIEW
            ])
        else:  # Medium/Low severity
            recommended_actions.append(ActionType.LOG_ONLY)
        
        # Create moderation actions for recommendations
        actions_created = []
        for action_type in recommended_actions:
            action = ModerationAction.objects.create(
                content_scan=violation.content_scan,
                violation=violation,
                action_type=action_type,
                action_status=ModerationStatus.PENDING,
                automated=True,
                reason=f"Automated response to {violation.violation_type} violation"
            )
            actions_created.append(action.id)
        
        logger.info(f"Created {len(actions_created)} moderation actions for violation {violation_id}")
        
        return {
            'violation_id': violation_id,
            'actions_created': actions_created,
            'recommended_actions': [action.value for action in recommended_actions],
            'status': 'processed'
        }
        
    except Exception as exc:
        logger.error(f"Failed to process policy violation {violation_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))

@shared_task
def generate_moderation_report(user_id, date_range_days=30):
    """
    Generate a comprehensive moderation report for a user.
    
    Args:
        user_id (int): ID of the user to generate report for
        date_range_days (int): Number of days to include in the report
    
    Returns:
        dict: Comprehensive moderation report data
    """
    from .models import ContentScan, PolicyViolation, ModerationAction
    from django.contrib.auth import get_user_model
    from django.db.models import Count, Avg
    
    User = get_user_model()
    user = User.objects.get(id=user_id)
    
    logger.info(f"Generating moderation report for user {user_id} "
               f"covering last {date_range_days} days")
    
    # Calculate date range
    start_date = timezone.now() - timedelta(days=date_range_days)
    
    # Gather scan statistics
    scans = ContentScan.objects.filter(user=user, scanned_at__gte=start_date)
    scan_stats = {
        'total_scans': scans.count(),
        'avg_scan_score': scans.aggregate(avg_score=Avg('scan_score'))['avg_score'] or 0,
        'high_risk_scans': scans.filter(scan_score__gte=60).count(),
    }
    
    # Gather violation statistics  
    violations = PolicyViolation.objects.filter(
        content_scan__user=user,
        created_at__gte=start_date
    )
    violation_stats = {
        'total_violations': violations.count(),
        'by_type': dict(violations.values('violation_type').annotate(count=Count('id')).values_list('violation_type', 'count')),
        'resolved_violations': violations.filter(is_resolved=True).count(),
    }
    
    # Gather action statistics
    actions = ModerationAction.objects.filter(
        triggered_by=user,
        created_at__gte=start_date
    )
    action_stats = {
        'total_actions': actions.count(),
        'by_type': dict(actions.values('action_type').annotate(count=Count('id')).values_list('action_type', 'count')),
        'pending_actions': actions.filter(action_status='pending').count(),
    }
    
    report = {
        'user_id': user_id,
        'report_period_days': date_range_days,
        'generated_at': timezone.now().isoformat(),
        'scan_statistics': scan_stats,
        'violation_statistics': violation_stats,
        'action_statistics': action_stats,
    }
    
    logger.info(f"Moderation report generated for user {user_id}: "
               f"{scan_stats['total_scans']} scans, {violation_stats['total_violations']} violations")
    
    return report
