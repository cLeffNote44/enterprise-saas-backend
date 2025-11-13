# 📖 API Reference

Complete API documentation for the Enterprise SaaS Foundation.

## 🌐 Base URL

```
Development: http://localhost:8000/api/
Production:  https://api.yourcompany.com/api/
```

## 🔐 Authentication

The API supports multiple authentication methods:

### JWT Authentication (Recommended)

1. **Obtain Token**
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

2. **Use Token in Requests**
```http
GET /api/resource/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

3. **Refresh Token**
```http
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### API Key Authentication

1. **Create API Key** (via Admin Panel or API)
```http
POST /api/api-keys/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "name": "Production API Key",
  "scopes": ["read", "write"]
}
```

2. **Use API Key**
```http
GET /api/resource/
Authorization: Api-Key YOUR_API_KEY
```

## 📄 Response Format

### Success Response

```json
{
  "id": 1,
  "name": "Resource Name",
  "created_at": "2024-01-15T10:30:00Z"
}
```

### List Response (Paginated)

```json
{
  "count": 100,
  "next": "https://api.example.com/api/resource/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Item 1"
    },
    {
      "id": 2,
      "name": "Item 2"
    }
  ]
}
```

### Error Response

```json
{
  "error": "Invalid request",
  "detail": "Field 'email' is required",
  "code": "validation_error",
  "field_errors": {
    "email": ["This field is required"]
  }
}
```

## 🔢 HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH request |
| 201 | Created | Successful POST request |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## 📋 Common Parameters

### Pagination

```http
GET /api/resource/?page=2&page_size=50
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| page_size | integer | 20 | Items per page (max 100) |

### Filtering

```http
GET /api/resource/?status=active&created_after=2024-01-01
```

### Searching

```http
GET /api/resource/?search=keyword
```

### Ordering

```http
GET /api/resource/?ordering=-created_at,name
```

Use `-` prefix for descending order.

## 🔑 Core APIs

### Authentication API

#### Login

```http
POST /api/auth/login/
```

**Request:**
```json
{
  "username": "user@example.com",
  "password": "secure-password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "organization": {
      "id": 1,
      "name": "Acme Corp"
    }
  }
}
```

#### Register

```http
POST /api/auth/register/
```

**Request:**
```json
{
  "username": "newuser@example.com",
  "email": "newuser@example.com",
  "password": "secure-password",
  "first_name": "John",
  "last_name": "Doe",
  "organization_name": "My Company"
}
```

#### Logout

```http
POST /api/auth/logout/
Authorization: Bearer YOUR_TOKEN
```

#### Password Reset

```http
POST /api/auth/password-reset/
```

**Request:**
```json
{
  "email": "user@example.com"
}
```

### Organizations API

#### List Organizations

```http
GET /api/organizations/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "Acme Corp",
      "slug": "acme-corp",
      "settings": {
        "timezone": "America/New_York",
        "date_format": "MM/DD/YYYY"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "member_count": 15
    }
  ]
}
```

#### Get Organization

```http
GET /api/organizations/{id}/
Authorization: Bearer YOUR_TOKEN
```

#### Update Organization

```http
PATCH /api/organizations/{id}/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "Updated Name",
  "settings": {
    "timezone": "UTC"
  }
}
```

#### Organization Members

```http
GET /api/organizations/{id}/members/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe"
      },
      "role": "admin",
      "joined_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Invite Member

```http
POST /api/organizations/{id}/invite/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "email": "newmember@example.com",
  "role": "member"
}
```

### Teams API

#### List Teams

```http
GET /api/teams/
Authorization: Bearer YOUR_TOKEN
```

#### Create Team

```http
POST /api/teams/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "Engineering",
  "description": "Engineering team",
  "members": [1, 2, 3]
}
```

#### Add Member to Team

```http
POST /api/teams/{id}/add-member/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "user_id": 5
}
```

### Permissions API

#### List User Permissions

```http
GET /api/permissions/my-permissions/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "permissions": [
    "accounts.view_organization",
    "accounts.manage_team",
    "billing.view_subscription",
    "billing.manage_payment"
  ]
}
```

#### Check Permission

```http
POST /api/permissions/check/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "permission": "billing.manage_subscription"
}
```

**Response:**
```json
{
  "has_permission": true
}
```

### API Keys API

#### List API Keys

```http
GET /api/api-keys/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Production Key",
      "key_prefix": "ak_prod_",
      "scopes": ["read", "write"],
      "created_at": "2024-01-01T00:00:00Z",
      "last_used_at": "2024-01-15T10:30:00Z",
      "expires_at": null
    }
  ]
}
```

#### Create API Key

```http
POST /api/api-keys/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "Integration Key",
  "scopes": ["read"],
  "expires_at": "2025-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "Integration Key",
  "key": "ak_live_1234567890abcdef",  // Only shown once!
  "key_prefix": "ak_live_",
  "scopes": ["read"],
  "created_at": "2024-01-15T10:30:00Z"
}
```

⚠️ **Important:** The full API key is only shown once during creation. Store it securely!

#### Revoke API Key

```http
DELETE /api/api-keys/{id}/
Authorization: Bearer YOUR_TOKEN
```

## 💳 Billing APIs

### Subscription Plans

#### List Plans

```http
GET /api/billing/plans/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Starter",
      "description": "Perfect for small teams",
      "price": "29.00",
      "billing_interval": "month",
      "trial_period_days": 14,
      "features": {
        "users": 5,
        "projects": 10,
        "storage_gb": 10
      },
      "is_active": true
    }
  ]
}
```

### Subscriptions

#### Get Current Subscription

```http
GET /api/billing/subscriptions/current/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "id": 1,
  "plan": {
    "id": 1,
    "name": "Starter",
    "price": "29.00"
  },
  "status": "active",
  "current_period_start": "2024-01-01T00:00:00Z",
  "current_period_end": "2024-02-01T00:00:00Z",
  "trial_end": null,
  "cancel_at_period_end": false
}
```

#### Create Subscription

```http
POST /api/billing/subscriptions/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "plan_id": 1,
  "payment_method_id": "pm_1234567890"
}
```

#### Update Subscription

```http
PATCH /api/billing/subscriptions/{id}/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "plan_id": 2
}
```

#### Cancel Subscription

```http
POST /api/billing/subscriptions/{id}/cancel/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "cancel_immediately": false  // If false, cancels at period end
}
```

### Payment Methods

#### List Payment Methods

```http
GET /api/billing/payment-methods/
Authorization: Bearer YOUR_TOKEN
```

#### Add Payment Method

```http
POST /api/billing/payment-methods/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "stripe_payment_method_id": "pm_1234567890",
  "set_as_default": true
}
```

### Invoices

#### List Invoices

```http
GET /api/billing/invoices/?status=paid
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "invoice_number": "INV-2024-001",
      "amount_total": "29.00",
      "amount_paid": "29.00",
      "status": "paid",
      "due_date": "2024-01-15T00:00:00Z",
      "paid_at": "2024-01-14T10:30:00Z",
      "pdf_url": "https://example.com/invoices/1.pdf"
    }
  ]
}
```

#### Download Invoice

```http
GET /api/billing/invoices/{id}/download/
Authorization: Bearer YOUR_TOKEN
```

### Usage Records

#### Record Usage

```http
POST /api/billing/usage/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "metric": "api_calls",
  "quantity": 1000,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Get Usage Summary

```http
GET /api/billing/usage/summary/?period=2024-01
Authorization: Bearer YOUR_TOKEN
```

## 🔔 Notification APIs

### Notifications

#### List Notifications

```http
GET /api/notifications/?is_read=false
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "title": "New Team Invitation",
      "message": "You've been invited to join the Engineering team",
      "priority": "high",
      "category": "team",
      "is_read": false,
      "action_url": "/teams/5/accept",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Mark as Read

```http
POST /api/notifications/{id}/mark-read/
Authorization: Bearer YOUR_TOKEN
```

#### Mark All as Read

```http
POST /api/notifications/mark-all-read/
Authorization: Bearer YOUR_TOKEN
```

### Notification Preferences

#### Get Preferences

```http
GET /api/notifications/preferences/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "email_enabled": true,
  "sms_enabled": false,
  "push_enabled": true,
  "digest_enabled": true,
  "digest_frequency": "daily",
  "category_preferences": {
    "billing": {
      "email": true,
      "sms": false,
      "push": true
    },
    "team": {
      "email": true,
      "sms": false,
      "push": false
    }
  }
}
```

#### Update Preferences

```http
PATCH /api/notifications/preferences/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "email_enabled": true,
  "digest_frequency": "weekly"
}
```

## 🚩 Feature Flags APIs

### Feature Flags

#### List Feature Flags

```http
GET /api/feature-flags/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": 1,
      "key": "advanced_analytics",
      "name": "Advanced Analytics",
      "description": "Enable advanced analytics dashboard",
      "is_active": true,
      "rollout_type": "percentage",
      "rollout_percentage": 50
    }
  ]
}
```

#### Check Feature Flag

```http
GET /api/feature-flags/check/{key}/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "key": "advanced_analytics",
  "enabled": true
}
```

### A/B Testing

#### List Experiments

```http
GET /api/feature-flags/experiments/
Authorization: Bearer YOUR_TOKEN
```

#### Get User Variant

```http
GET /api/feature-flags/experiments/{id}/variant/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "experiment": "pricing_page_test",
  "variant": "variant_b",
  "variant_data": {
    "button_color": "green",
    "pricing_display": "annual_first"
  }
}
```

#### Track Event

```http
POST /api/feature-flags/experiments/{id}/track/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "event_type": "conversion",
  "properties": {
    "plan_selected": "premium",
    "amount": 99.00
  }
}
```

## 📁 File Management APIs

### Files

#### Upload File

```http
POST /api/files/
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

file: (binary)
name: "document.pdf"
description: "Q1 Financial Report"
visibility: "organization"
```

**Response:**
```json
{
  "id": 1,
  "name": "document.pdf",
  "original_filename": "document.pdf",
  "file_type": "application/pdf",
  "size": 1048576,
  "url": "https://cdn.example.com/files/abc123/document.pdf",
  "thumbnail_url": "https://cdn.example.com/files/abc123/thumb_document.png",
  "visibility": "organization",
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

#### List Files

```http
GET /api/files/?file_type=application/pdf&uploaded_after=2024-01-01
Authorization: Bearer YOUR_TOKEN
```

#### Download File

```http
GET /api/files/{id}/download/
Authorization: Bearer YOUR_TOKEN
```

#### Delete File

```http
DELETE /api/files/{id}/
Authorization: Bearer YOUR_TOKEN
```

### File Sharing

#### Create Share Link

```http
POST /api/files/{id}/share/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "expires_at": "2024-12-31T23:59:59Z",
  "max_downloads": 10,
  "require_authentication": false
}
```

**Response:**
```json
{
  "id": 1,
  "share_url": "https://example.com/share/abc123xyz",
  "expires_at": "2024-12-31T23:59:59Z",
  "max_downloads": 10,
  "download_count": 0
}
```

## 📊 Data Exchange APIs

### Import Jobs

#### Create Import

```http
POST /api/data-exchange/imports/
Authorization: Bearer YOUR_TOKEN
Content-Type: multipart/form-data

file: (CSV/Excel file)
import_type: "users"
options: {"skip_duplicates": true}
```

**Response:**
```json
{
  "id": 1,
  "status": "pending",
  "import_type": "users",
  "total_rows": 1000,
  "processed_rows": 0,
  "successful_rows": 0,
  "failed_rows": 0,
  "started_at": null,
  "completed_at": null
}
```

#### Get Import Status

```http
GET /api/data-exchange/imports/{id}/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "id": 1,
  "status": "processing",
  "import_type": "users",
  "total_rows": 1000,
  "processed_rows": 456,
  "successful_rows": 450,
  "failed_rows": 6,
  "progress_percentage": 45.6,
  "error_log": [
    {
      "row": 12,
      "error": "Invalid email format"
    }
  ]
}
```

### Export Jobs

#### Create Export

```http
POST /api/data-exchange/exports/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "export_type": "users",
  "format": "csv",
  "filters": {
    "created_after": "2024-01-01",
    "status": "active"
  }
}
```

#### Download Export

```http
GET /api/data-exchange/exports/{id}/download/
Authorization: Bearer YOUR_TOKEN
```

## 🔍 Search APIs

### Global Search

```http
GET /api/search/?q=project&types=project,task,user
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "results": [
    {
      "type": "project",
      "id": 1,
      "title": "Project Management System",
      "highlight": "...building a <mark>project</mark> management...",
      "url": "/projects/1/",
      "score": 0.95
    },
    {
      "type": "task",
      "id": 42,
      "title": "Complete project documentation",
      "highlight": "Complete <mark>project</mark> documentation",
      "url": "/tasks/42/",
      "score": 0.87
    }
  ],
  "facets": {
    "type": {
      "project": 5,
      "task": 12,
      "user": 3
    }
  }
}
```

### Saved Searches

#### Save Search

```http
POST /api/search/saved/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "Active Projects",
  "query": "status:active type:project"
}
```

#### List Saved Searches

```http
GET /api/search/saved/
Authorization: Bearer YOUR_TOKEN
```

## 🔗 Webhook APIs

### Webhooks

#### List Webhooks

```http
GET /api/webhooks/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "url": "https://example.com/webhooks/",
      "events": ["user.created", "invoice.paid"],
      "is_active": true,
      "secret": "whsec_...",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Create Webhook

```http
POST /api/webhooks/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "url": "https://example.com/webhooks/",
  "events": ["user.created", "user.updated"],
  "description": "User synchronization webhook"
}
```

#### Test Webhook

```http
POST /api/webhooks/{id}/test/
Authorization: Bearer YOUR_TOKEN
```

### Webhook Deliveries

#### List Deliveries

```http
GET /api/webhooks/{id}/deliveries/?status=failed
Authorization: Bearer YOUR_TOKEN
```

#### Retry Failed Delivery

```http
POST /api/webhooks/deliveries/{id}/retry/
Authorization: Bearer YOUR_TOKEN
```

## 📝 Audit & Compliance APIs

### Audit Logs

#### List Audit Logs

```http
GET /api/audit/logs/?action=user.login&date_from=2024-01-01
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "timestamp": "2024-01-15T10:30:00Z",
      "level": "info",
      "action": "user.login",
      "user": {
        "id": 1,
        "email": "user@example.com"
      },
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "extra_data": {
        "method": "jwt",
        "success": true
      }
    }
  ]
}
```

### Change History

#### List Changes for Object

```http
GET /api/audit/changes/?content_type=project&object_id=1
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "timestamp": "2024-01-15T10:30:00Z",
      "action": "update",
      "user": {
        "id": 1,
        "email": "user@example.com"
      },
      "changes": {
        "status": {
          "old": "planning",
          "new": "active"
        },
        "name": {
          "old": "Project A",
          "new": "Project Alpha"
        }
      }
    }
  ]
}
```

### Compliance Reports

#### Generate Compliance Report

```http
POST /api/compliance/reports/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "report_type": "gdpr_data_access",
  "user_id": 123,
  "period_start": "2024-01-01",
  "period_end": "2024-01-31"
}
```

## 🌍 Internationalization APIs

### Languages

#### List Languages

```http
GET /api/i18n/languages/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "code": "en",
      "name": "English",
      "is_active": true,
      "is_rtl": false
    },
    {
      "code": "es",
      "name": "Spanish",
      "is_active": true,
      "is_rtl": false
    }
  ]
}
```

### Translations

#### Get Translations

```http
GET /api/i18n/translations/?language=es&context=dashboard
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "dashboard.welcome": "Bienvenido",
  "dashboard.projects": "Proyectos",
  "dashboard.tasks": "Tareas"
}
```

### User Preferences

#### Update Language Preference

```http
PATCH /api/i18n/preferences/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "language": "es",
  "timezone": "America/Mexico_City"
}
```

## 🔄 Workflow APIs

### Workflows

#### List Workflows

```http
GET /api/workflows/
Authorization: Bearer YOUR_TOKEN
```

#### Create Workflow Instance

```http
POST /api/workflows/{id}/start/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "context": {
    "project_id": 123,
    "request_type": "budget_approval",
    "amount": 50000
  }
}
```

#### Get Workflow Status

```http
GET /api/workflows/instances/{id}/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "id": 1,
  "workflow": {
    "id": 1,
    "name": "Budget Approval"
  },
  "status": "pending_approval",
  "current_state": "manager_review",
  "context": {
    "project_id": 123,
    "amount": 50000,
    "approvals": []
  },
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": null
}
```

### Approval Requests

#### List Pending Approvals

```http
GET /api/workflows/approvals/?status=pending
Authorization: Bearer YOUR_TOKEN
```

#### Approve/Reject

```http
POST /api/workflows/approvals/{id}/decide/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "decision": "approved",
  "comments": "Budget looks reasonable"
}
```

## 🏥 Health & Monitoring APIs

### Health Check

```http
GET /health/
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": {
    "database": "healthy",
    "redis": "healthy",
    "celery": "healthy"
  }
}
```

### Metrics

```http
GET /metrics/
Authorization: Bearer YOUR_TOKEN
```

Returns Prometheus-formatted metrics.

## 📊 Rate Limits

Default rate limits per endpoint:

| Endpoint Category | Authenticated | Unauthenticated |
|-------------------|---------------|-----------------|
| Authentication | 100/hour | 20/hour |
| Read operations | 1000/hour | 100/hour |
| Write operations | 300/hour | N/A |
| File uploads | 50/hour | N/A |
| Webhooks | 1000/hour | N/A |

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1610713200
```

When rate limit is exceeded:
```json
{
  "error": "Rate limit exceeded",
  "detail": "Request limit reached. Try again in 3600 seconds",
  "retry_after": 3600
}
```

## 🔒 Security Best Practices

1. **Always use HTTPS** in production
2. **Store API keys securely** - never in client-side code
3. **Rotate API keys regularly** - especially after team member departures
4. **Use minimal scopes** - grant only necessary permissions
5. **Validate webhook signatures** - verify webhook authenticity
6. **Implement retry logic** - with exponential backoff
7. **Monitor rate limits** - implement backoff when approaching limits
8. **Log API usage** - for security auditing

## 📚 SDKs & Libraries

### Official SDKs

- **Python**: `pip install enterprise-saas-sdk`
- **JavaScript/TypeScript**: `npm install @enterprise-saas/sdk`
- **Ruby**: `gem install enterprise-saas`
- **Go**: `go get github.com/enterprise-saas/go-sdk`

### Example Usage (Python)

```python
from enterprise_saas import Client

client = Client(api_key="YOUR_API_KEY")

# List projects
projects = client.projects.list(status="active")

# Create task
task = client.tasks.create(
    project_id=1,
    title="New task",
    priority="high"
)
```

## 🆘 Support

- **Documentation**: https://docs.yourcompany.com
- **API Status**: https://status.yourcompany.com
- **Support Email**: api-support@yourcompany.com
- **Enterprise Support**: Available 24/7 for enterprise customers

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for API version history and breaking changes.

---

**Need more help?** Contact our API support team at api-support@yourcompany.com or visit our [Developer Portal](https://developers.yourcompany.com).
