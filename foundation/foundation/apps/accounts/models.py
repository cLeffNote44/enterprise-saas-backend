"""Core authentication models for the foundation."""
import secrets
import hashlib
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class UserActivity(models.Model):
    """
    Log of user activities for audit purposes.
    """
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('profile_update', 'Profile Update'),
        ('api_access', 'API Access'),
        ('data_access', 'Data Access'),
        ('admin_action', 'Admin Action'),
        ('export', 'Data Export'),
        ('delete', 'Data Deletion'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the action"
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        help_text="IP address from which action was performed"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string from the request"
    )
    metadata = models.JSONField(
        default=dict,
        help_text="Additional metadata about the action"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action occurred"
    )
    
    class Meta:
        db_table = 'foundation_useractivity'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"


class APIKey(models.Model):
    """
    Model for API key management with rotation and expiration.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='api_keys'
    )
    name = models.CharField(
        max_length=100,
        help_text="Human-readable name for this API key"
    )
    key_hash = models.CharField(
        max_length=64,
        unique=True,
        help_text="SHA256 hash of the API key"
    )
    key_prefix = models.CharField(
        max_length=8,
        help_text="First 8 characters of the API key for identification"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(
        help_text="When this API key expires"
    )
    
    class Meta:
        db_table = 'foundation_apikey'
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.key_prefix}...)"
    
    @classmethod
    def generate_key(cls, user, name: str, expires_in_days: int = 365):
        """
        Generate a new API key for a user.
        
        Returns:
            tuple: (api_key_instance, raw_key)
        """
        # Generate a random API key
        raw_key = secrets.token_urlsafe(32)  # 256-bit key
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        key_prefix = raw_key[:8]
        
        # Calculate expiration date
        expires_at = timezone.now() + timezone.timedelta(days=expires_in_days)
        
        # Create the API key record
        api_key = cls.objects.create(
            user=user,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            expires_at=expires_at
        )
        
        return api_key, raw_key
    
    def rotate_key(self):
        """
        Rotate this API key by generating a new one.
        
        Returns:
            str: New raw API key
        """
        raw_key = secrets.token_urlsafe(32)
        self.key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        self.key_prefix = raw_key[:8]
        self.save(update_fields=['key_hash', 'key_prefix'])
        
        return raw_key
    
    def record_usage(self):
        """
        Record that this API key was used.
        """
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])


class UserSecurityProfile(models.Model):
    """
    Extended security profile for users.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='security_profile'
    )
    mfa_enabled = models.BooleanField(
        default=False,
        help_text="Whether multi-factor authentication is enabled"
    )
    last_mfa_setup = models.DateTimeField(
        null=True, blank=True,
        help_text="When MFA was last configured"
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    account_locked_until = models.DateTimeField(
        null=True, blank=True,
        help_text="When account lock expires"
    )
    password_changed_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When password was last changed"
    )
    security_questions_enabled = models.BooleanField(
        default=False,
        help_text="Whether security questions are configured"
    )
    
    class Meta:
        db_table = 'foundation_usersecurityprofile'
        verbose_name = 'User Security Profile'
        verbose_name_plural = 'User Security Profiles'
    
    def __str__(self):
        return f"Security Profile for {self.user.username}"
    
    def is_account_locked(self):
        """
        Check if the account is currently locked.
        """
        if not self.account_locked_until:
            return False
        return timezone.now() < self.account_locked_until
    
    def lock_account(self, duration_minutes: int = 15):
        """
        Lock the account for a specified duration.
        """
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """
        Unlock the account and reset failed login attempts.
        """
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])
    
    def record_failed_login(self, max_attempts: int = 5):
        """
        Record a failed login attempt and lock account if needed.
        """
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= max_attempts:
            self.lock_account()
        
        self.save(update_fields=['failed_login_attempts'])
    
    def record_successful_login(self):
        """
        Record a successful login and reset failed attempts.
        """
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])
