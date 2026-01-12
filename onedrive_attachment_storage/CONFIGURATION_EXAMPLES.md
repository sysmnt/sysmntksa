# OneDrive Attachment Storage - Configuration Examples

This file contains example configurations for different use cases.

## Basic Configuration

**Single Company, Simple Structure**

```yaml
Company: My Company
Enable OneDrive Storage: Yes
Tenant ID: "12345678-1234-1234-1234-123456789012"
Client ID: "87654321-4321-4321-4321-210987654321"
Client Secret: "your-secret-value-here"
Drive ID: (empty - use default)
Root Folder: "/Odoo/Attachments"
Organize by Company: No
Organize by Model: No
Organize by Record ID: No
```

**Result**: All files in flat structure
```
/Odoo/Attachments/
  ├── invoice_001.pdf
  ├── quotation_042.pdf
  └── contract.docx
```

---

## Advanced Configuration

**Multi-Company with Full Organization**

```yaml
Company: Company A
Enable OneDrive Storage: Yes
Tenant ID: "your-tenant-id"
Client ID: "your-client-id"
Client Secret: "your-client-secret"
Drive ID: (empty)
Root Folder: "/Odoo/Files"
Organize by Company: Yes
Organize by Model: Yes
Organize by Record ID: Yes
```

**Result**: Hierarchical structure
```
/Odoo/Files/
  ├── Company A/
  │   ├── sale.order/
  │   │   ├── 42/
  │   │   │   ├── quotation.pdf
  │   │   │   └── signed_contract.pdf
  │   │   └── 43/
  │   │       └── order_confirmation.pdf
  │   ├── res.partner/
  │   │   └── 15/
  │   │       └── company_logo.png
  │   └── hr.employee/
  │       └── 7/
  │           └── resume.pdf
  └── Company B/
      └── ...
```

---

## SharePoint Configuration

**Using Specific SharePoint Site**

First, get your Drive ID:
```bash
# Using Microsoft Graph Explorer or PowerShell
GET https://graph.microsoft.com/v1.0/sites/{site-id}/drives
```

Then configure:
```yaml
Company: My Company
Enable OneDrive Storage: Yes
Tenant ID: "your-tenant-id"
Client ID: "your-client-id"
Client Secret: "your-client-secret"
Drive ID: "b!abc123..." # Specific SharePoint drive ID
Root Folder: "/Shared Documents/Odoo"
Organize by Company: Yes
Organize by Model: Yes
Organize by Record ID: No
```

---

## Department-Based Configuration

**Organize by Department (Custom)**

For this, you might want to customize the folder structure logic:

```python
# Custom modification in onedrive_client.py
def upload_file(self, file_content, filename, model=None, res_id=None, 
                company_id=None, department_id=None):
    """Modified to support department folders"""
    
    folder_parts = [config.root_folder]
    
    if department_id:
        department = self.env['hr.department'].browse(department_id)
        folder_parts.append(department.name)
    
    if config.use_model_folders and model:
        folder_parts.append(model)
    
    # ... rest of the logic
```

**Result**:
```
/Odoo/Attachments/
  ├── Sales Department/
  │   └── sale.order/
  │       └── quotation.pdf
  ├── HR Department/
  │   └── hr.employee/
  │       └── contract.pdf
  └── Finance Department/
      └── account.move/
          └── invoice.pdf
```

---

## Date-Based Configuration

**Organize by Year and Month**

Custom modification:
```python
from datetime import datetime

def upload_file(self, file_content, filename, model=None, res_id=None, company_id=None):
    folder_parts = [config.root_folder]
    
    # Add year and month
    now = datetime.now()
    folder_parts.append(str(now.year))
    folder_parts.append(now.strftime('%m-%B'))  # "01-January"
    
    if config.use_model_folders and model:
        folder_parts.append(model)
    
    # ... rest
```

**Result**:
```
/Odoo/Attachments/
  ├── 2026/
  │   ├── 01-January/
  │   │   ├── sale.order/
  │   │   └── account.move/
  │   └── 02-February/
  │       └── ...
  └── 2025/
      └── ...
```

---

## Regional Configuration

**Multi-Region Deployment**

```yaml
# Configuration for US Region
Company: US Branch
Enable OneDrive Storage: Yes
Tenant ID: "your-tenant-id"
Client ID: "your-client-id"
Client Secret: "your-client-secret"
Drive ID: "us-drive-id"  # US-based SharePoint drive
Root Folder: "/US/Odoo/Attachments"

# Configuration for EU Region  
Company: EU Branch
Enable OneDrive Storage: Yes
Tenant ID: "your-tenant-id"
Client ID: "your-client-id"
Client Secret: "your-client-secret"
Drive ID: "eu-drive-id"  # EU-based SharePoint drive
Root Folder: "/EU/Odoo/Attachments"
```

---

## Security-Enhanced Configuration

**With Additional Security Measures**

```yaml
Company: Secure Corp
Enable OneDrive Storage: Yes
Tenant ID: "your-tenant-id"
Client ID: "your-client-id"
Client Secret: "your-client-secret"
Drive ID: (empty)
Root Folder: "/Secure/Odoo/Vault"
Organize by Company: Yes
Organize by Model: Yes
Organize by Record ID: Yes
```

**Additional Security in Azure**:
- Enable Conditional Access policies
- Require MFA for administrators
- Set up Data Loss Prevention (DLP) policies
- Enable audit logging
- Configure retention policies

---

## Development vs Production

### Development Environment

```yaml
Company: Dev Company
Enable OneDrive Storage: Yes
Tenant ID: "dev-tenant-id"
Client ID: "dev-client-id"
Client Secret: "dev-client-secret"
Drive ID: "dev-drive-id"  # Separate dev drive
Root Folder: "/Odoo/DEV/Attachments"
Organize by Company: No  # Simpler structure for testing
Organize by Model: Yes
Organize by Record ID: No
```

### Production Environment

```yaml
Company: Production Company
Enable OneDrive Storage: Yes
Tenant ID: "prod-tenant-id"
Client ID: "prod-client-id"
Client Secret: "prod-client-secret"
Drive ID: (empty)
Root Folder: "/Odoo/PROD/Attachments"
Organize by Company: Yes
Organize by Model: Yes
Organize by Record ID: Yes
```

---

## Migration Strategy Configurations

### Phase 1: Testing (Disabled)
```yaml
Enable OneDrive Storage: No  # Test first without activation
# ... other settings configured
```

### Phase 2: New Files Only
```yaml
Enable OneDrive Storage: Yes  # Only new attachments go to OneDrive
# Don't enable migration cron yet
```

### Phase 3: Gradual Migration
```yaml
Enable OneDrive Storage: Yes
# Enable migration cron with small batch size
# Scheduled Actions → OneDrive: Migrate Attachments
# Batch size: 50
# Interval: Every 2 hours
```

### Phase 4: Full Migration
```yaml
Enable OneDrive Storage: Yes
# Increase batch size
# Batch size: 200
# Interval: Every 30 minutes
# Until all migrated
```

---

## Performance-Optimized Configuration

**For High-Volume Environments**

```yaml
Company: High Volume Corp
Enable OneDrive Storage: Yes
Tenant ID: "your-tenant-id"
Client ID: "your-client-id"
Client Secret: "your-client-secret"
Drive ID: (empty)
Root Folder: "/Odoo/Attachments"
Organize by Company: No   # Less API calls
Organize by Model: Yes    # Balance between organization and performance
Organize by Record ID: No # Reduces folder creation overhead
```

**Odoo Configuration** (`odoo.conf`):
```ini
[options]
workers = 8
max_cron_threads = 4
limit_memory_hard = 4294967296  # 4GB
limit_time_cpu = 600
limit_time_real = 1200
```

---

## Example Azure AD App Settings

### Application Registration

**Basic Information**:
```
Name: Odoo OneDrive Integration
Application Type: Web
Supported Account Types: Single tenant
```

**API Permissions**:
```
Microsoft Graph (Application Permissions):
- Files.ReadWrite.All
- Sites.ReadWrite.All (for SharePoint)

Status: Admin consent granted ✓
```

**Certificates & Secrets**:
```
Client Secret Description: Odoo Integration Secret
Expires: 24 months
Secret Value: [Copy this immediately]
```

**Optional - Advanced**:
```
Token configuration:
- access_token lifetime: 60 minutes (default)
- refresh_token lifetime: N/A (using client credentials flow)

Conditional Access:
- Require MFA: No (service account)
- Allowed IP ranges: Your Odoo server IP
```

---

## Backup and Disaster Recovery

### Configuration Backup

**Export current configuration**:
```python
# In Odoo shell
config = env['onedrive.config'].search([])
for c in config:
    print(f"""
    Company: {c.company_id.name}
    Active: {c.active}
    Tenant ID: {c.tenant_id}
    Client ID: {c.client_id}
    Root Folder: {c.root_folder}
    Use Company Folders: {c.use_company_folders}
    Use Model Folders: {c.use_model_folders}
    Use Record Folders: {c.use_record_folders}
    """)
```

### Restore Configuration

```python
# Create configuration from backup
env['onedrive.config'].create({
    'company_id': env.company.id,
    'active': True,
    'tenant_id': 'your-tenant-id',
    'client_id': 'your-client-id',
    'client_secret': 'your-client-secret',
    'root_folder': '/Odoo/Attachments',
    'use_company_folders': True,
    'use_model_folders': True,
    'use_record_folders': True,
})
```

---

## Troubleshooting Configurations

### Test Configuration (Minimal)

Use this to isolate issues:
```yaml
Company: Test Company
Enable OneDrive Storage: Yes
Tenant ID: "your-tenant-id"
Client ID: "your-client-id"
Client Secret: "your-client-secret"
Drive ID: (empty)
Root Folder: "/Test"
Organize by Company: No
Organize by Model: No
Organize by Record ID: No
```

If this works, gradually add complexity.

---

## Environment Variables (Optional)

For deployment automation, you could use environment variables:

```bash
# .env file
ONEDRIVE_TENANT_ID=your-tenant-id
ONEDRIVE_CLIENT_ID=your-client-id
ONEDRIVE_CLIENT_SECRET=your-secret
ONEDRIVE_ROOT_FOLDER=/Odoo/Attachments
ONEDRIVE_USE_COMPANY_FOLDERS=true
ONEDRIVE_USE_MODEL_FOLDERS=true
ONEDRIVE_USE_RECORD_FOLDERS=false
```

Then modify `onedrive_config.py` to read from environment:
```python
import os

@api.model
def create(self, vals):
    # Override with environment variables if available
    if os.getenv('ONEDRIVE_TENANT_ID'):
        vals['tenant_id'] = os.getenv('ONEDRIVE_TENANT_ID')
    # ... etc
    return super().create(vals)
```

---

## Questions?

Contact support@yourcompany.com with your use case for personalized configuration advice.
