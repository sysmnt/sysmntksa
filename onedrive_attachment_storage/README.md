# OneDrive Attachment Storage for Odoo

## Transform Your Odoo Storage Infrastructure

Store all Odoo attachments in Microsoft OneDrive/SharePoint and save up to 70% on server storage costs while leveraging Microsoft's enterprise-grade cloud infrastructure.

---

## 🌟 Key Features

### Zero Local Storage
- All attachments automatically uploaded to OneDrive
- Only URL references stored in Odoo database
- Free up valuable server disk space
- Reduce backup size and costs

### Automatic Integration
- Works transparently with ALL Odoo modules
- No code changes required
- Sales, Purchase, CRM, HR, Documents - everything works
- Users won't notice any difference

### Smart Migration
- Background job migrates existing attachments
- Process 100 files per batch automatically
- Real-time progress tracking
- Continues where it left off if interrupted

### Large File Support
- Handles files up to 15 GB
- Resumable chunked uploads for reliability
- Perfect for videos, large PDFs, and archives

### Lightning Fast Downloads
- Direct downloads from Microsoft's global CDN
- No server bandwidth usage
- Fast access from anywhere in the world

### Multi-Company Support
- Separate configuration per company
- Data isolation between companies
- Company-specific folder organization

### Enterprise Security
- OAuth2 authentication with automatic token refresh
- Encrypted token storage
- Respects Odoo access rights
- Microsoft's enterprise security infrastructure

---

## 📋 Requirements

- **Odoo**: 17.0 or higher (Community or Enterprise)
- **Python**: 3.10+
- **Dependencies**: requests library (included)
- **Azure**: Azure AD Application with API permissions
- **Microsoft**: Microsoft 365 / OneDrive for Business account

---

## 🚀 Quick Start

### 1. Install the Module

1. Download and extract to your Odoo addons directory
2. Restart Odoo server
3. Go to **Apps** → Remove "Apps" filter → Search "OneDrive Attachment Storage"
4. Click **Install**

### 2. Create Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Enter name: "Odoo OneDrive Integration"
5. Select **Accounts in this organizational directory only**
6. Click **Register**

### 3. Configure API Permissions

1. In your app, go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Application permissions**
3. Add:
   - `Sites.ReadWrite.All`
   - `Files.ReadWrite.All`
4. Click **Grant admin consent**

### 4. Create Client Secret

1. Go to **Certificates & secrets** → **New client secret**
2. Copy the secret value immediately (you won't see it again!)

### 5. Get IDs

From app **Overview** page, copy:
- **Application (client) ID**
- **Directory (tenant) ID**

### 6. Configure in Odoo

1. **Settings** → **Technical** → **OneDrive Storage**
2. Enter Tenant ID, Client ID, Client Secret
3. Click **Test Connection**
4. Enable **OneDrive Storage** toggle
5. Click **Sync Existing Attachments** (optional)

---

## 📁 Folder Organization

Files are organized as:

```
SharePoint/Documents/Odoo/Attachments/
└── [Model Name]/
    └── [Record ID]/
        └── files...
```

---

## 🔧 Troubleshooting

### Connection Test Fails

**Invalid Client ID/Secret**: Verify credentials copied correctly from Azure  
**Access Denied (403)**: Grant admin consent for API permissions  
**Invalid Tenant ID**: Check Directory (tenant) ID for typos

### Files Not Uploading

1. Verify OneDrive Storage toggle is enabled
2. Check connection test passes
3. Review Odoo logs: `tail -f /var/log/odoo.log`
4. Ensure client secret hasn't expired

---

## 📞 Support

**Professional Support Available:**
- Installation assistance
- Azure AD configuration
- Custom folder structures
- Training for administrators

**Contact:** info@sysmnt.com  
**Website:** www.sysmnt.com

---

## 📝 License

**Odoo Proprietary License v1.0 (OPL-1)**

This is proprietary software. Purchasing grants you the right to use it on one Odoo database instance.

For multi-instance licenses, contact: info@sysmnt.com

---

## 🔄 Changelog

### Version 17.0.1.0.0 (January 2026)

- Initial release
- Complete OneDrive/SharePoint integration
- Automatic upload and background migration
- Multi-company support
- OAuth2 authentication
- Large file support (up to 15 GB)
- Statistics dashboard
- 3 automated maintenance cron jobs

---

**© 2026 SYSMNT. All rights reserved.**
