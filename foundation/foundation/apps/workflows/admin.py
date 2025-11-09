from django.contrib import admin
from .models import Workflow, WorkflowInstance, ApprovalRequest

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'status']

@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'current_state', 'created_at']

@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ['workflow_instance', 'approver', 'status', 'requested_at']
