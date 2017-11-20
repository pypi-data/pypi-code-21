from django.conf import settings

ORG_MODEL = getattr(settings, 'ORGANIZATION_MODEL', 'report.Organization')
REPORT_PACKAGES = getattr(settings, 'REPORT_PACKAGES', [])
TYPE_CHOICES = getattr(settings, 'REPORT_TYPE_CHOICES', (
    ('pdf', 'PDF Document'),
    ('docx', 'Word Document'),
    ('xlsx', 'Excel Document'),
))
