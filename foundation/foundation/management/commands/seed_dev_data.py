"""
Management command to seed development data
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from django.db import transaction
from faker import Faker
import random
from datetime import timedelta

from foundation.apps.accounts.models import APIKey, UserSecurityProfile
from foundation.apps.accounts.enterprise import (
    Organization, OrganizationMembership, Department, Role
)
from foundation.apps.analytics.models import AnalyticsSnapshot, PrivacyInsight
from foundation.apps.compliance.models import CompliancePolicy, ConsentRecord

fake = Faker()


class Command(BaseCommand):
    help = 'Seeds the database with development data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=20,
            help='Number of users to create (default: 20)',
        )
        parser.add_argument(
            '--orgs',
            type=int,
            default=5,
            help='Number of organizations to create (default: 5)',
        )
    
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding development data...")
        
        if options['clear']:
            self.clear_data()
        
        # Create superuser if it doesn't exist
        self.create_superuser()
        
        # Create organizations
        orgs = self.create_organizations(options['orgs'])
        
        # Create users
        users = self.create_users(options['users'])
        
        # Create departments
        departments = self.create_departments(orgs)
        
        # Create roles
        roles = self.create_roles(orgs)
        
        # Create memberships
        self.create_memberships(users, orgs, roles, departments)
        
        # Create API keys
        self.create_api_keys(users)
        
        # Create compliance policies
        self.create_compliance_policies(orgs)
        
        # Create sample analytics data
        self.create_analytics_data(users)
        
        self.stdout.write(self.style.SUCCESS('✅ Development data seeded successfully!'))
        self.print_summary(users, orgs)
    
    def clear_data(self):
        """Clear existing data (except superuser)"""
        self.stdout.write("🗑️  Clearing existing data...")
        
        # Keep superuser
        User.objects.filter(is_superuser=False).delete()
        Organization.objects.all().delete()
        
        self.stdout.write("   Data cleared!")
    
    def create_superuser(self):
        """Create a superuser if it doesn't exist"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@foundation.local',
                password='admin123456',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write("👤 Created superuser (admin/admin123456)")
        else:
            self.stdout.write("👤 Superuser already exists")
    
    def create_organizations(self, count):
        """Create organizations with different tiers"""
        self.stdout.write(f"🏢 Creating {count} organizations...")
        
        orgs = []
        tiers = ['free', 'starter', 'professional', 'enterprise', 'enterprise_plus']
        industries = ['Technology', 'Healthcare', 'Finance', 'Education', 'Retail', 'Manufacturing']
        
        for i in range(count):
            org = Organization.objects.create(
                name=fake.company(),
                slug=f"org-{i+1}",
                description=fake.catch_phrase(),
                website=fake.url(),
                primary_contact_email=fake.company_email(),
                primary_contact_name=fake.name(),
                billing_email=fake.company_email(),
                technical_contact_email=fake.company_email(),
                subscription_tier=random.choice(tiers),
                max_users=random.randint(10, 1000),
                storage_quota_gb=random.randint(10, 1000),
                api_rate_limit=random.randint(1000, 100000),
                industry=random.choice(industries),
                company_size=random.choice(['1-10', '11-50', '51-200', '201-500', '500+']),
                country=fake.country_code(),
                timezone='America/New_York',
                is_active=True,
                enforce_2fa=random.choice([True, False]),
                allow_api_access=True,
                data_retention_days=random.randint(30, 365)
            )
            orgs.append(org)
            
        self.stdout.write(f"   Created {len(orgs)} organizations")
        return orgs
    
    def create_users(self, count):
        """Create regular users"""
        self.stdout.write(f"👥 Creating {count} users...")
        
        users = []
        for i in range(count):
            username = fake.user_name() + str(i)
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True
            )
            
            # Create security profile
            UserSecurityProfile.objects.create(
                user=user,
                two_factor_enabled=random.choice([True, False]),
                backup_codes_generated=random.choice([True, False]),
                failed_login_attempts=random.randint(0, 3),
                last_password_change=timezone.now() - timedelta(days=random.randint(1, 365))
            )
            
            users.append(user)
        
        self.stdout.write(f"   Created {len(users)} users")
        return users
    
    def create_departments(self, orgs):
        """Create departments for organizations"""
        self.stdout.write("🏗️  Creating departments...")
        
        departments = []
        dept_names = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Operations', 'Support']
        
        for org in orgs:
            for dept_name in random.sample(dept_names, k=random.randint(3, 6)):
                dept = Department.objects.create(
                    organization=org,
                    name=dept_name,
                    description=f"{dept_name} department for {org.name}",
                    is_active=True
                )
                departments.append(dept)
        
        self.stdout.write(f"   Created {len(departments)} departments")
        return departments
    
    def create_roles(self, orgs):
        """Create roles for organizations"""
        self.stdout.write("🎭 Creating roles...")
        
        roles = []
        role_templates = [
            ('Admin', 'Full administrative access', True),
            ('Manager', 'Management level access', False),
            ('Developer', 'Development team access', False),
            ('Viewer', 'Read-only access', False),
            ('Editor', 'Content editing access', False)
        ]
        
        for org in orgs:
            for name, desc, is_admin in role_templates:
                role = Role.objects.create(
                    organization=org,
                    name=f"{name} - {org.slug}",
                    description=desc,
                    is_system_role=is_admin
                )
                
                # Add some random permissions
                if is_admin:
                    # Admin gets all permissions for the org
                    perms = Permission.objects.all()[:20]
                else:
                    # Others get random subset
                    perms = Permission.objects.order_by('?')[:random.randint(5, 15)]
                
                role.permissions.set(perms)
                roles.append(role)
        
        self.stdout.write(f"   Created {len(roles)} roles")
        return roles
    
    def create_memberships(self, users, orgs, roles, departments):
        """Create organization memberships"""
        self.stdout.write("🔗 Creating organization memberships...")
        
        memberships = []
        
        # Assign each user to 1-3 organizations
        for user in users:
            num_orgs = random.randint(1, min(3, len(orgs)))
            user_orgs = random.sample(orgs, k=num_orgs)
            
            for org in user_orgs:
                # Get random role and department from this org
                org_roles = [r for r in roles if r.organization == org]
                org_depts = [d for d in departments if d.organization == org]
                
                if org_roles and org_depts:
                    membership = OrganizationMembership.objects.create(
                        user=user,
                        organization=org,
                        role=random.choice(org_roles),
                        department=random.choice(org_depts) if org_depts else None,
                        is_admin=random.choice([True, False]) if random.random() > 0.8 else False,
                        joined_at=timezone.now() - timedelta(days=random.randint(1, 365))
                    )
                    memberships.append(membership)
        
        self.stdout.write(f"   Created {len(memberships)} memberships")
        return memberships
    
    def create_api_keys(self, users):
        """Create API keys for some users"""
        self.stdout.write("🔑 Creating API keys...")
        
        keys = []
        # Create API keys for 30% of users
        api_users = random.sample(users, k=int(len(users) * 0.3))
        
        for user in api_users:
            for i in range(random.randint(1, 3)):
                key, raw_key = APIKey.generate_key(
                    user=user,
                    name=f"{fake.word()}-api-key-{i+1}",
                    expires_in_days=random.randint(30, 365)
                )
                key.description = fake.sentence()
                key.rate_limit = random.randint(100, 10000)
                key.daily_limit = random.randint(1000, 100000)
                key.save()
                keys.append(key)
        
        self.stdout.write(f"   Created {len(keys)} API keys")
        return keys
    
    def create_compliance_policies(self, orgs):
        """Create compliance policies"""
        self.stdout.write("📋 Creating compliance policies...")
        
        policies = []
        frameworks = ['gdpr', 'hipaa', 'soc2', 'pci_dss', 'iso27001']
        
        for org in orgs:
            # Each org gets 2-4 compliance policies
            for framework in random.sample(frameworks, k=random.randint(2, 4)):
                policy = CompliancePolicy.objects.create(
                    name=f"{framework.upper()} Policy - {org.name}",
                    description=f"Compliance policy for {framework.upper()} framework",
                    framework=framework,
                    version="1.0",
                    is_active=True,
                    enforcement_level=random.choice(['strict', 'moderate', 'relaxed']),
                    created_by=User.objects.filter(is_superuser=True).first()
                )
                policies.append(policy)
        
        self.stdout.write(f"   Created {len(policies)} compliance policies")
        return policies
    
    def create_analytics_data(self, users):
        """Create sample analytics data"""
        self.stdout.write("📊 Creating analytics data...")
        
        # Create some analytics snapshots for random users
        sample_users = random.sample(users, k=min(10, len(users)))
        
        for user in sample_users:
            # Create snapshots for the last 7 days
            for days_ago in range(7):
                date = timezone.now().date() - timedelta(days=days_ago)
                
                AnalyticsSnapshot.objects.create(
                    user=user,
                    date=date,
                    total_documents=random.randint(10, 1000),
                    total_messages=random.randint(50, 5000),
                    total_forum_posts=random.randint(5, 500),
                    storage_used_bytes=random.randint(1000000, 10000000000),
                    storage_used_mb=random.randint(1, 10000),
                    shared_documents_count=random.randint(0, 100),
                    public_documents_count=random.randint(0, 50),
                    encrypted_documents_count=random.randint(0, 200),
                    retention_violations_count=random.randint(0, 10),
                    privacy_score=random.randint(60, 100),
                    security_score=random.randint(70, 100),
                    api_calls_count=random.randint(0, 10000),
                    failed_login_attempts=random.randint(0, 5),
                    successful_exports=random.randint(0, 50),
                    data_subject_requests=random.randint(0, 5)
                )
            
            # Create some privacy insights
            for _ in range(random.randint(1, 5)):
                PrivacyInsight.objects.create(
                    user=user,
                    insight_type=random.choice(['recommendation', 'alert', 'tip']),
                    severity=random.choice(['low', 'medium', 'high']),
                    title=fake.sentence(nb_words=5),
                    description=fake.text(max_nb_chars=200),
                    action_text="Review Now",
                    action_url="/dashboard/",
                    is_read=random.choice([True, False]),
                    is_dismissed=False,
                    expires_at=timezone.now() + timedelta(days=random.randint(7, 30))
                )
        
        self.stdout.write("   Created analytics data")
    
    def print_summary(self, users, orgs):
        """Print summary of created data"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📈 SEED DATA SUMMARY")
        self.stdout.write("="*50)
        
        summary = {
            'Superuser': 'admin / admin123456',
            'Regular Users': f'{len(users)} users (password: password123)',
            'Organizations': Organization.objects.count(),
            'Departments': Department.objects.count(),
            'Roles': Role.objects.count(),
            'Memberships': OrganizationMembership.objects.count(),
            'API Keys': APIKey.objects.count(),
            'Compliance Policies': CompliancePolicy.objects.count(),
            'Analytics Snapshots': AnalyticsSnapshot.objects.count(),
            'Privacy Insights': PrivacyInsight.objects.count(),
        }
        
        for key, value in summary.items():
            self.stdout.write(f"  {key}: {value}")
        
        self.stdout.write("="*50)
        self.stdout.write("\n🎉 You can now login at: http://localhost:8000/admin")
        self.stdout.write("   Username: admin")
        self.stdout.write("   Password: admin123456\n")