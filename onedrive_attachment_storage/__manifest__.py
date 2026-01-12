# -*- coding: utf-8 -*-
{
    'name': 'OneDrive Attachment Storage',
    'version': '17.0.1.0.0',
    'category': 'Productivity/Documents',
    'summary': 'Store All Odoo Attachments in Microsoft OneDrive/SharePoint - Zero Server Storage',
    'description': """
        OneDrive Attachment Storage - Enterprise Cloud Storage Integration
        ===================================================================
        
        Transform your Odoo infrastructure by storing all attachments in Microsoft OneDrive/SharePoint.
        Save up to 70% on server storage costs while leveraging Microsoft's enterprise-grade cloud.
        
        🌟 Key Features:
        ----------------
        * **Zero Local Storage**: All attachments automatically stored in OneDrive
        * **Automatic Integration**: Works with ALL Odoo modules - no code changes
        * **Smart Migration**: Background job migrates existing attachments with progress tracking
        * **Large File Support**: Handles files up to 15 GB with resumable uploads
        * **Instant Downloads**: Direct downloads from Microsoft's global CDN
        * **Multi-Company**: Separate configurations per company with data isolation
        * **Smart Organization**: Organize by company, model, and record ID
        * **OAuth2 Security**: Enterprise-grade authentication with automatic token refresh
        * **Production Ready**: Graceful fallback, retry logic, comprehensive logging
        
        💼 Perfect For:
        ---------------
        * Enterprise customers with Microsoft 365 subscriptions
        * Global teams needing fast worldwide access
        * Growing businesses scaling storage independently
        * Compliance-focused organizations (GDPR, HIPAA, SOC 2)
        
        ⚡ Performance Benefits:
        -----------------------
        * Reduce server disk usage by 90%+
        * Faster downloads via Microsoft's global CDN
        * Unlimited scalability without server upgrades
        * No backup overhead for attachment data
        
        🔧 Easy Setup:
        --------------
        1. Register Azure AD application (5 minutes)
        2. Configure credentials in Odoo
        3. Test connection
        4. Enable automatic uploads
        5. Migrate existing files with one click
        
        📊 Statistics Dashboard:
        ------------------------
        Track migration progress, total files stored, and storage usage in real-time.
        
        🛡️ Enterprise Support:
        -----------------------
        Professional installation, configuration, and customization services available.
        
        Developed by SYSMNT | www.sysmnt.com | info@sysmnt.com
    """,
    'author': 'SYSMNT',
    'website': 'https://www.sysmnt.com',
    'license': 'OPL-1',
    'price': 199.00,
    'currency': 'USD',
    'support': 'info@sysmnt.com',
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/screenshot_config.png',
        'static/description/screenshot_statistics.png',
        'static/description/screenshot_sync.png',
    ],
    'depends': ['base', 'web', 'mail'],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/onedrive_settings.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
