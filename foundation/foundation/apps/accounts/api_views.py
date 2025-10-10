"""
API views for security and authentication features.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from .security import (
    MFAManager, APIKeyAuthentication,
    SetupMFASerializer, ConfirmMFASerializer, 
    VerifyMFASerializer, GenerateAPIKeySerializer
)
from .models import APIKey, UserSecurityProfile

User = get_user_model()


class SetupMFAView(APIView):
    """
    Set up Multi-Factor Authentication for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=SetupMFASerializer,
        responses={200: 'MFA setup initiated successfully'},
        summary="Setup MFA for user",
        description="Initiate MFA setup by generating TOTP device and backup codes"
    )
    def post(self, request):
        serializer = SetupMFASerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        device_name = serializer.validated_data['device_name']
        
        try:
            result = MFAManager.setup_totp(request.user, device_name)
            
            # Create or update security profile
            security_profile, created = UserSecurityProfile.objects.get_or_create(
                user=request.user
            )
            security_profile.last_mfa_setup = timezone.now()
            security_profile.save()
            
            return Response({
                'message': 'MFA setup initiated successfully',
                'qr_code_url': result['qr_url'],
                'backup_codes': result['backup_codes'],
                'device_id': result['device_id']
            })
            
        except Exception as e:
            return Response({
                'error': 'Failed to setup MFA',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmMFAView(APIView):
    """
    Confirm MFA setup by verifying a TOTP token.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=ConfirmMFASerializer,
        responses={200: 'MFA confirmed successfully'},
        summary="Confirm MFA setup",
        description="Confirm MFA setup by providing a valid TOTP token"
    )
    def post(self, request):
        serializer = ConfirmMFASerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        device_id = serializer.validated_data.get('device_id')
        
        if MFAManager.confirm_totp(request.user, token, device_id):
            # Update security profile
            security_profile, created = UserSecurityProfile.objects.get_or_create(
                user=request.user
            )
            security_profile.mfa_enabled = True
            security_profile.save()
            
            return Response({
                'message': 'MFA confirmed successfully',
                'mfa_enabled': True
            })
        else:
            return Response({
                'error': 'Invalid token or MFA setup not found'
            }, status=status.HTTP_400_BAD_REQUEST)


class DisableMFAView(APIView):
    """
    Disable MFA for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: 'MFA disabled successfully'},
        summary="Disable MFA",
        description="Disable multi-factor authentication for the current user"
    )
    def post(self, request):
        if MFAManager.disable_mfa(request.user):
            # Update security profile
            security_profile, created = UserSecurityProfile.objects.get_or_create(
                user=request.user
            )
            security_profile.mfa_enabled = False
            security_profile.save()
            
            return Response({
                'message': 'MFA disabled successfully',
                'mfa_enabled': False
            })
        else:
            return Response({
                'error': 'Failed to disable MFA'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MFAStatusView(APIView):
    """
    Get MFA status for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: 'MFA status retrieved successfully'},
        summary="Get MFA status",
        description="Get current MFA configuration status for the user"
    )
    def get(self, request):
        mfa_enabled = MFAManager.is_mfa_enabled(request.user)
        
        # Get security profile info
        try:
            security_profile = request.user.security_profile
            last_setup = security_profile.last_mfa_setup
        except UserSecurityProfile.DoesNotExist:
            last_setup = None
        
        return Response({
            'mfa_enabled': mfa_enabled,
            'last_mfa_setup': last_setup
        })


class GenerateAPIKeyView(APIView):
    """
    Generate a new API key for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=GenerateAPIKeySerializer,
        responses={201: 'API key generated successfully'},
        summary="Generate API key",
        description="Generate a new API key with specified name and expiration"
    )
    def post(self, request):
        serializer = GenerateAPIKeySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        name = serializer.validated_data['name']
        expires_in_days = serializer.validated_data['expires_in_days']
        
        try:
            api_key, raw_key = APIKey.generate_key(
                user=request.user,
                name=name,
                expires_in_days=expires_in_days
            )
            
            return Response({
                'message': 'API key generated successfully',
                'api_key': raw_key,  # Only returned once!
                'key_id': api_key.id,
                'key_prefix': api_key.key_prefix,
                'expires_at': api_key.expires_at,
                'warning': 'Store this key securely. It will not be shown again.'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Failed to generate API key',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListAPIKeysView(APIView):
    """
    List all API keys for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: 'API keys retrieved successfully'},
        summary="List API keys",
        description="List all API keys for the current user (without showing the actual keys)"
    )
    def get(self, request):
        api_keys = APIKey.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-created_at')
        
        keys_data = []
        for key in api_keys:
            keys_data.append({
                'id': key.id,
                'name': key.name,
                'key_prefix': key.key_prefix,
                'created_at': key.created_at,
                'last_used_at': key.last_used_at,
                'expires_at': key.expires_at,
                'is_expired': key.expires_at < timezone.now()
            })
        
        return Response({
            'api_keys': keys_data,
            'count': len(keys_data)
        })


class RevokeAPIKeyView(APIView):
    """
    Revoke an API key.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: 'API key revoked successfully'},
        summary="Revoke API key",
        description="Revoke (deactivate) an API key by its ID"
    )
    def delete(self, request, key_id):
        try:
            api_key = APIKey.objects.get(
                id=key_id,
                user=request.user,
                is_active=True
            )
            
            api_key.is_active = False
            api_key.save()
            
            return Response({
                'message': 'API key revoked successfully'
            })
            
        except APIKey.DoesNotExist:
            return Response({
                'error': 'API key not found'
            }, status=status.HTTP_404_NOT_FOUND)


class RotateAPIKeyView(APIView):
    """
    Rotate an existing API key (generate new key value).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        responses={200: 'API key rotated successfully'},
        summary="Rotate API key",
        description="Generate a new key value for an existing API key"
    )
    def post(self, request, key_id):
        try:
            api_key = APIKey.objects.get(
                id=key_id,
                user=request.user,
                is_active=True
            )
            
            new_key = api_key.rotate_key()
            
            return Response({
                'message': 'API key rotated successfully',
                'new_api_key': new_key,  # Only returned once!
                'key_prefix': api_key.key_prefix,
                'warning': 'Store this key securely. It will not be shown again.'
            })
            
        except APIKey.DoesNotExist:
            return Response({
                'error': 'API key not found'
            }, status=status.HTTP_404_NOT_FOUND)


# Function-based view for webhook signature validation
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def validate_webhook_signature(request):
    """
    Validate webhook signature for incoming webhooks.
    This is typically used internally by other services.
    """
    from .security import WebhookSignatureValidator
    from django.conf import settings
    
    # Get signature from header
    signature = request.META.get('HTTP_X_SIGNATURE_256', '')
    if not signature:
        return Response({
            'error': 'Missing signature header'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get webhook secret from settings
    webhook_secret = getattr(settings, 'API_WEBHOOK_SECRET', '')
    if not webhook_secret:
        return Response({
            'error': 'Webhook secret not configured'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Validate signature
    payload = request.body
    is_valid = WebhookSignatureValidator.validate_signature(
        payload, signature, webhook_secret
    )
    
    if is_valid:
        return Response({
            'message': 'Signature valid',
            'valid': True
        })
    else:
        return Response({
            'error': 'Invalid signature',
            'valid': False
        }, status=status.HTTP_401_UNAUTHORIZED)
