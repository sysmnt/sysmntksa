"""
OneDrive Attachment Storage Module

This module provides seamless integration between Odoo and Microsoft OneDrive,
automatically storing all attachments in the cloud instead of the local filestore.

Key Components:
--------------
1. onedrive_config.py: Configuration model for OneDrive settings
2. onedrive_client.py: Microsoft Graph API client for OneDrive operations
3. ir_attachment.py: Override of Odoo's attachment model

Main Features:
--------------
- Automatic upload of all attachments to OneDrive
- No binary storage on Odoo server (only URL references)
- OAuth2 authentication with Microsoft Graph API
- Automatic token refresh
- Support for large files (chunked upload)
- Multi-company support
- Background migration of existing attachments
- Configurable folder structure
- Graceful fallback to local storage

Usage:
------
Once configured, the module works automatically. All new attachments
are uploaded to OneDrive, and downloads redirect to OneDrive URLs.

For more information, see README.md
"""
