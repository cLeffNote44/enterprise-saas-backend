"""
Enterprise security features for Data Destroyer.

This module provides multi-factor authentication, API key management,
and enhanced security features for the Data Destroyer platform.
"""
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from django_otp import match_token
from django_otp.models import Device
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_email.models import EmailDevice
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers

User = get_user_model()


class APIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class for API key-based authentication with rotation.
    """
    
    def authenticate(self, request):
        """
        Authenticate using API key in header or query parameter.
        """
        api_key = self.get_api_key(request)
        if not api_key:
            return None
            
        user = self.get_user_for_api_key(api_key)
        if not user:
            raise AuthenticationFailed('Invalid API key')
            
        if not user.is_active:
            raise AuthenticationFailed('User account is disabled')
            
        # Check if API key needs rotation
        self.check_api_key_rotation(user, api_key)
        
        return (user, None)
    
    def get_api_key(self, request) -> Optional[str]:
        """Extract API key from request headers or query params."""
        # Try Authorization header first
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('ApiKey '):
            return auth_header[7:]  # Remove 'ApiKey ' prefix
            
        # Try X-API-Key header
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key:
            return api_key
            
        # Try query parameter
        return request.GET.get('api_key')
    
    def get_user_for_api_key(self, api_key: str) -> Optional[AbstractUser]:
        """Get user associated with the API key."""
        # Use cache to avoid database lookups for every request
        cache_key = f"api_key:{hashlib.sha256(api_key.encode()).hexdigest()}"
        user_id = cache.get(cache_key)
        
        if user_id:
            try:
                return User.objects.get(id=user_id, is_active=True)
            except User.DoesNotExist:
                cache.delete(cache_key)
                return None
        
        # If not in cache, validate against stored hash
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        try:
            from .models import APIKey
            api_key_obj = APIKey.objects.select_related('user').get(
                key_hash=api_key_hash,
                is_active=True,
                expires_at__gt=timezone.now()
            )
            
            # Cache the result for 5 minutes
            cache.set(cache_key, api_key_obj.user.id, 300)
            return api_key_obj.user
            
        except APIKey.DoesNotExist:
            return None
    
    def check_api_key_rotation(self, user: AbstractUser, api_key: str):
        """Check if API key should be rotated based on age."""
        try:
            from .models import APIKey
            api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            api_key_obj = APIKey.objects.get(
                user=user,
                key_hash=api_key_hash,
                is_active=True
            )
            
            rotation_days = getattr(settings, 'API_KEY_ROTATION_DAYS', 90)
            rotation_date = api_key_obj.created_at + timedelta(days=rotation_days)
            
            if timezone.now() > rotation_date:
                # Trigger rotation warning (could send email, log, etc.)
                pass  # Implementation depends on notification system
                
        except APIKey.DoesNotExist:
            pass


class MFAManager:
    """
    Manager class for Multi-Factor Authentication operations.
    """
    
    @staticmethod
    def setup_totp(user: AbstractUser, device_name: str = "default") -> Dict[str, Any]:
        """
        Set up TOTP device for a user.
        
        Returns:
            Dict containing QR code URL and backup codes.
        """
        # Create or get TOTP device
        device, created = TOTPDevice.objects.get_or_create(
            user=user,
            name=device_name,
            defaults={'confirmed': False}
        )
        
        if not created:
            # Reset the device if it already exists
            device.confirmed = False
            device.save()
        
        # Generate backup codes
        backup_codes = MFAManager.generate_backup_codes(user)
        
        # Generate QR code URL
        qr_url = device.config_url
        
        return {
            'qr_url': qr_url,
            'secret': device.bin_key.hex(),
            'backup_codes': backup_codes,
            'device_id': device.id
        }
    
    @staticmethod
    def confirm_totp(user: AbstractUser, token: str, device_id: int = None) -> bool:
        """
        Confirm TOTP setup with a token.
        """
        try:
            if device_id:
                device = TOTPDevice.objects.get(user=user, id=device_id)
            else:
                device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
            
            if not device:
                return False
            
            # Verify the token
            if device.verify_token(token):
                device.confirmed = True
                device.save()
                return True
                
        except TOTPDevice.DoesNotExist:
            pass
            
        return False
    
    @staticmethod
    def generate_backup_codes(user: AbstractUser, count: int = 10) -> List[str]:
        """
        Generate backup codes for a user.
        """
        # Remove existing backup codes
        static_device, created = StaticDevice.objects.get_or_create(
            user=user,
            name='backup_codes'
        )
        
        # Clear existing tokens
        static_device.token_set.all().delete()
        
        # Generate new backup codes
        backup_codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()  # 8-character hex code
            backup_codes.append(code)
            
            StaticToken.objects.create(
                device=static_device,
                token=code
            )
        
        return backup_codes
    
    @staticmethod
    def verify_mfa_token(user: AbstractUser, token: str) -> bool:
        """
        Verify MFA token from any configured device.
        """
        # Try to match against any device
        device = match_token(user, token)
        return device is not None
    
    @staticmethod
    def is_mfa_enabled(user: AbstractUser) -> bool:
        """
        Check if user has MFA enabled.
        """
        return user.totpdevice_set.filter(confirmed=True).exists()
    
    @staticmethod
    def disable_mfa(user: AbstractUser) -> bool:
        """
        Disable all MFA devices for a user.
        """
        # Disable TOTP devices
        user.totpdevice_set.update(confirmed=False)
        
        # Remove backup codes
        static_devices = StaticDevice.objects.filter(user=user, name='backup_codes')
        for device in static_devices:
            device.token_set.all().delete()
            device.delete()
        
        # Disable email devices
        user.emaildevice_set.update(confirmed=False)
        
        return True


class WebhookSignatureValidator:
    """
    Validator for webhook signatures to ensure authenticity.
    """
    
    @staticmethod
    def validate_signature(payload: bytes, signature: str, secret: str) -> bool:
        """
        Validate webhook signature using HMAC-SHA256.
        
        Args:
            payload: Raw webhook payload
            signature: Signature from webhook header (e.g., "sha256=hash")
            secret: Webhook secret for validation
            
        Returns:
            bool: True if signature is valid
        """
        if not secret:
            return False
            
        # Parse signature format (e.g., "sha256=hash")
        try:
            method, signature_hash = signature.split('=', 1)
        except ValueError:
            return False
            
        if method.lower() != 'sha256':
            return False
        
        # Calculate expected signature
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (constant-time comparison)
        return hmac.compare_digest(signature_hash, expected_signature)


# Serializers for API endpoints
class SetupMFASerializer(serializers.Serializer):
    """Serializer for MFA setup."""
    device_name = serializers.CharField(max_length=64, default="default")


class ConfirmMFASerializer(serializers.Serializer):
    """Serializer for MFA confirmation."""
    token = serializers.CharField(max_length=6, min_length=6)
    device_id = serializers.IntegerField(required=False)


class VerifyMFASerializer(serializers.Serializer):
    """Serializer for MFA verification."""
    token = serializers.CharField(max_length=8)  # Supports both TOTP and backup codes


class GenerateAPIKeySerializer(serializers.Serializer):
    """Serializer for API key generation."""
    name = serializers.CharField(max_length=100)
    expires_in_days = serializers.IntegerField(default=365, min_value=1, max_value=365)
