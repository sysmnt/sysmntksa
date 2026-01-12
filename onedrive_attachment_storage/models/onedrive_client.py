# -*- coding: utf-8 -*-
import logging
import requests
import json
import base64
import re
from datetime import datetime, timedelta
from urllib.parse import quote
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class OneDriveClient(models.AbstractModel):
    _name = 'onedrive.client'
    _description = 'OneDrive API Client'
    
    # Microsoft Graph API endpoints
    AUTHORITY = "https://login.microsoftonline.com"
    GRAPH_API = "https://graph.microsoft.com/v1.0"
    SCOPE = ["https://graph.microsoft.com/.default"]
    
    @staticmethod
    def _sanitize_filename(filename):
        """
        Sanitize filename to be compatible with OneDrive/SharePoint
        - Remove illegal characters: <>:"/\|?*
        - Trim leading/trailing spaces and dots
        - Limit length to 250 characters
        - Preserve file extension
        """
        if not filename:
            return "unnamed_file"
        
        # Split name and extension
        name_parts = filename.rsplit('.', 1)
        name = name_parts[0]
        ext = f".{name_parts[1]}" if len(name_parts) > 1 else ""
        
        # Remove illegal characters: <>:"/\|?*
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            name = name.replace(char, '_')
        
        # Remove control characters
        name = ''.join(char for char in name if ord(char) >= 32)
        
        # Trim spaces and dots
        name = name.strip('. ')
        
        # Ensure not empty
        if not name:
            name = "file"
        
        # Limit length (250 - extension length)
        max_length = 250 - len(ext)
        if len(name) > max_length:
            name = name[:max_length]
        
        return name + ext
    
    @api.model
    def create_client(self, config):
        """Create and return an authenticated OneDrive client"""
        if not config:
            raise UserError(_('OneDrive configuration not found.'))
        
        # Check if token is valid
        if config.access_token and config.token_expiry:
            if datetime.now() < config.token_expiry:
                return self  # Token still valid
        
        # Need to get new token
        self._refresh_token(config)
        return self
    
    def _refresh_token(self, config):
        """Get or refresh access token using client credentials flow"""
        url = f"{self.AUTHORITY}/{config.tenant_id}/oauth2/v2.0/token"
        
        data = {
            'client_id': config.client_id,
            'client_secret': config.client_secret,
            'scope': ' '.join(self.SCOPE),
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(url, data=data, timeout=30)
            
            # Log detailed error if authentication fails
            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_desc = error_data.get('error_description', 'Unknown error')
                error_code = error_data.get('error', 'unknown')
                
                _logger.error(f"Token request failed: {error_code} - {error_desc}")
                
                # Provide helpful error messages
                if 'AADSTS700016' in error_desc or 'application with identifier' in error_desc:
                    raise UserError(_('Invalid Client ID. Verify you copied the correct Application (client) ID from Azure AD.'))
                elif 'AADSTS7000215' in error_desc or 'Invalid client secret' in error_desc:
                    raise UserError(_('Invalid Client Secret. The secret may be expired or incorrect. Create a new secret in Azure AD and update the configuration.'))
                elif 'AADSTS90002' in error_desc or 'AADSTS900023' in error_desc:
                    raise UserError(_('Invalid Tenant ID. Verify you copied the correct Directory (tenant) ID from Azure AD.'))
                else:
                    raise UserError(_('Authentication failed: %s') % error_desc)
            
            response.raise_for_status()
            token_data = response.json()
            
            # Calculate expiry time (subtract 5 minutes for safety)
            expiry_time = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600) - 300)
            
            config.write({
                'access_token': token_data.get('access_token'),
                'token_expiry': expiry_time,
            })
            
            _logger.info("OneDrive token refreshed successfully")
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to refresh OneDrive token: {str(e)}")
            raise UserError(_('Failed to authenticate with OneDrive: %s') % str(e))
    
    def _get_headers(self, config):
        """Get authorization headers for API requests"""
        return {
            'Authorization': f'Bearer {config.access_token}',
            'Content-Type': 'application/json'
        }
    
    @api.model
    def get_me(self):
        """Test connection by accessing SharePoint root site"""
        config = self.env['onedrive.config'].get_config()
        
        # Ensure we have a valid token
        self.create_client(config)
        
        # For Application permissions, test by accessing SharePoint site
        url = f"{self.GRAPH_API}/sites/root"
        headers = self._get_headers(config)
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            site_data = response.json()
            
            # Also verify we can access the drive
            site_id = site_data.get('id')
            drive_url = f"{self.GRAPH_API}/sites/{site_id}/drive"
            drive_response = requests.get(drive_url, headers=headers, timeout=30)
            drive_response.raise_for_status()
            
            return site_data
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if '403' in error_msg or 'Forbidden' in error_msg:
                error_msg = "Access denied. Ensure your Azure AD app has 'Sites.ReadWrite.All' permission and admin consent has been granted."
            elif '401' in error_msg or 'Unauthorized' in error_msg:
                error_msg = "Authentication failed. Verify your Tenant ID, Client ID, and Client Secret are correct."
            _logger.error(f"Failed to test connection: {error_msg}")
            raise UserError(_('Failed to connect to OneDrive: %s') % error_msg)
    
    def _get_drive_root(self, config):
        """Get the drive root endpoint"""
        if config.drive_id:
            return f"{self.GRAPH_API}/drives/{config.drive_id}"
        else:
            # For Application permissions, get the root site's default drive
            return self._get_default_drive(config)
    
    def _get_default_drive(self, config):
        """Get the default SharePoint drive for Application permissions"""
        headers = self._get_headers(config)
        
        try:
            # Get the root SharePoint site
            site_url = f"{self.GRAPH_API}/sites/root"
            response = requests.get(site_url, headers=headers, timeout=30)
            response.raise_for_status()
            site_data = response.json()
            
            site_id = site_data.get('id')
            
            # Get the default drive for this site
            drive_url = f"{self.GRAPH_API}/sites/{site_id}/drive"
            drive_response = requests.get(drive_url, headers=headers, timeout=30)
            drive_response.raise_for_status()
            drive_data = drive_response.json()
            
            drive_id = drive_data.get('id')
            
            # Save drive_id for future use
            config.write({'drive_id': drive_id})
            
            _logger.info(f"Using default SharePoint drive: {drive_id}")
            return f"{self.GRAPH_API}/drives/{drive_id}"
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to get default drive: {str(e)}")
            raise UserError(_("Failed to access SharePoint drive. Ensure your Azure AD app has Sites.ReadWrite.All permissions and admin consent has been granted. Error: %s") % str(e))
    
    def _ensure_folder_exists(self, config, folder_path):
        """Ensure folder exists in OneDrive, create if not"""
        drive_root = self._get_drive_root(config)
        headers = self._get_headers(config)
        
        # Split path into parts and skip empty
        parts = [p for p in folder_path.split('/') if p]
        
        if not parts:
            _logger.info("No folder path specified, using root")
            return ''
        
        current_path = ''
        for part in parts:
            current_path = f"{current_path}/{part}" if current_path else part
            
            # URL encode the path for checking
            encoded_check_path = quote(current_path)
            check_url = f"{drive_root}/root:/{encoded_check_path}"
            
            try:
                response = requests.get(check_url, headers=headers, timeout=30)
                
                if response.status_code == 404:
                    # Folder doesn't exist, create it
                    _logger.info(f"Folder not found, creating: {current_path}")
                    
                    if '/' in current_path:
                        # Nested folder - need parent path
                        parent_path = '/'.join(current_path.split('/')[:-1])
                        encoded_parent = quote(parent_path)
                        create_url = f"{drive_root}/root:/{encoded_parent}:/children"
                    else:
                        # Root level folder
                        create_url = f"{drive_root}/root/children"
                    
                    folder_data = {
                        'name': part,
                        'folder': {},
                        '@microsoft.graph.conflictBehavior': 'rename'
                    }
                    
                    create_response = requests.post(
                        create_url,
                        headers=headers,
                        json=folder_data,
                        timeout=30
                    )
                    
                    if create_response.status_code not in [200, 201]:
                        _logger.error(f"Folder creation failed with status {create_response.status_code}: {create_response.text}")
                    
                    create_response.raise_for_status()
                    _logger.info(f"Successfully created folder: {current_path}")
                elif response.status_code == 200:
                    _logger.info(f"Folder already exists: {current_path}")
                else:
                    _logger.warning(f"Unexpected status {response.status_code} when checking folder: {current_path}")
                    
            except requests.exceptions.RequestException as e:
                _logger.error(f"Failed to ensure folder exists {current_path}: {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    _logger.error(f"Response body: {e.response.text}")
                raise
        
        return current_path
    
    @api.model
    def upload_file(self, file_content, filename, model=None, res_id=None, company_id=None):
        """
        Upload file to OneDrive
        Args:
            file_content: Binary file content
            filename: Name of the file
            model: Odoo model name (optional)
            res_id: Record ID (optional)
            company_id: Company ID (optional)
        
        Returns:
            dict: OneDrive file metadata including download URL
        """
        config = self.env['onedrive.config'].get_config(company_id)
        
        if not config or not config.active:
            raise UserError(_('OneDrive storage is not configured or enabled.'))
        
        # Sanitize filename to prevent API errors
        original_filename = filename
        filename = self._sanitize_filename(filename)
        if filename != original_filename:
            _logger.info(f"Sanitized filename: '{original_filename}' -> '{filename}'")
        
        # Ensure token is valid
        self.create_client(config)
        
        # Build folder path (strip leading/trailing slashes from root folder)
        root_folder = config.root_folder.strip('/')
        folder_parts = [root_folder] if root_folder else []
        
        if config.use_company_folders and company_id:
            company = self.env['res.company'].browse(company_id)
            folder_parts.append(company.name)
        
        if config.use_model_folders and model:
            folder_parts.append(model)
        
        if config.use_record_folders and res_id:
            folder_parts.append(str(res_id))
        
        folder_path = '/'.join(folder_parts)
        
        # Ensure folder exists
        self._ensure_folder_exists(config, folder_path)
        
        # Upload file
        drive_root = self._get_drive_root(config)
        file_path = f"{folder_path}/{filename}"
        
        # Choose upload method based on file size
        file_size = len(file_content)
        
        if file_size < 4 * 1024 * 1024:  # Less than 4MB - simple upload
            return self._simple_upload(config, drive_root, file_path, file_content)
        else:  # Large file - resumable upload
            return self._resumable_upload(config, drive_root, file_path, file_content)
    
    def _simple_upload(self, config, drive_root, file_path, file_content):
        """Simple upload for small files (< 4MB)"""
        # URL encode the path properly
        encoded_path = quote(file_path)
        url = f"{drive_root}/root:/{encoded_path}:/content"
        headers = {
            'Authorization': f'Bearer {config.access_token}',
            'Content-Type': 'application/octet-stream'
        }
        
        try:
            response = requests.put(url, headers=headers, data=file_content, timeout=300)
            response.raise_for_status()
            
            file_metadata = response.json()
            _logger.info(f"Uploaded file to OneDrive: {file_path}")
            
            return {
                'id': file_metadata.get('id'),
                'name': file_metadata.get('name'),
                'size': file_metadata.get('size'),
                'web_url': file_metadata.get('webUrl'),
                'download_url': file_metadata.get('@microsoft.graph.downloadUrl'),
                'path': file_path
            }
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to upload file: {str(e)}")
            raise UserError(_('Failed to upload file to OneDrive: %s') % str(e))
    
    def _resumable_upload(self, config, drive_root, file_path, file_content):
        """Resumable upload for large files (>= 4MB)"""
        # Create upload session with proper URL encoding
        encoded_path = quote(file_path)
        url = f"{drive_root}/root:/{encoded_path}:/createUploadSession"
        headers = self._get_headers(config)
        
        session_data = {
            'item': {
                '@microsoft.graph.conflictBehavior': 'rename'
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=session_data, timeout=30)
            response.raise_for_status()
            upload_url = response.json().get('uploadUrl')
            
            # Upload in chunks
            chunk_size = 320 * 1024 * 10  # 3.2 MB chunks
            file_size = len(file_content)
            offset = 0
            
            while offset < file_size:
                chunk_end = min(offset + chunk_size, file_size)
                chunk = file_content[offset:chunk_end]
                
                chunk_headers = {
                    'Content-Length': str(len(chunk)),
                    'Content-Range': f'bytes {offset}-{chunk_end - 1}/{file_size}'
                }
                
                chunk_response = requests.put(
                    upload_url,
                    headers=chunk_headers,
                    data=chunk,
                    timeout=300
                )
                chunk_response.raise_for_status()
                
                offset = chunk_end
                _logger.info(f"Uploaded {offset}/{file_size} bytes")
            
            file_metadata = chunk_response.json()
            _logger.info(f"Completed upload of large file: {file_path}")
            
            return {
                'id': file_metadata.get('id'),
                'name': file_metadata.get('name'),
                'size': file_metadata.get('size'),
                'web_url': file_metadata.get('webUrl'),
                'download_url': file_metadata.get('@microsoft.graph.downloadUrl'),
                'path': file_path
            }
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to upload large file: {str(e)}")
            raise UserError(_('Failed to upload large file to OneDrive: %s') % str(e))
    
    @api.model
    def delete_file(self, file_id=None, file_path=None, company_id=None):
        """
        Delete file from OneDrive
        
        Args:
            file_id: OneDrive file ID
            file_path: Full path to file (alternative to file_id)
            company_id: Company ID
        """
        config = self.env['onedrive.config'].get_config(company_id)
        
        if not config or not config.active:
            return  # Silently skip if OneDrive not configured
        
        # Ensure token is valid
        self.create_client(config)
        
        drive_root = self._get_drive_root(config)
        headers = self._get_headers(config)
        
        # Determine delete URL
        if file_id:
            url = f"{drive_root}/items/{file_id}"
        elif file_path:
            url = f"{drive_root}/root:{file_path}"
        else:
            _logger.warning("No file_id or file_path provided for deletion")
            return
        
        try:
            response = requests.delete(url, headers=headers, timeout=30)
            
            if response.status_code == 204:
                _logger.info(f"Deleted file from OneDrive: {file_id or file_path}")
            elif response.status_code == 404:
                _logger.warning(f"File not found in OneDrive: {file_id or file_path}")
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to delete file from OneDrive: {str(e)}")
            # Don't raise error on deletion failures
    
    @api.model
    def get_download_url(self, file_id=None, file_path=None, company_id=None):
        """
        Get download URL for a file
        
        Args:
            file_id: OneDrive file ID
            file_path: Full path to file (alternative to file_id)
            company_id: Company ID
        
        Returns:
            str: Download URL
        """
        config = self.env['onedrive.config'].get_config(company_id)
        
        if not config or not config.active:
            raise UserError(_('OneDrive storage is not configured or enabled.'))
        
        # Ensure token is valid
        self.create_client(config)
        
        drive_root = self._get_drive_root(config)
        headers = self._get_headers(config)
        
        # Determine metadata URL
        if file_id:
            url = f"{drive_root}/items/{file_id}"
        elif file_path:
            url = f"{drive_root}/root:{file_path}"
        else:
            raise UserError(_('No file identifier provided'))
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            file_metadata = response.json()
            download_url = file_metadata.get('@microsoft.graph.downloadUrl')
            
            if not download_url:
                raise UserError(_('Download URL not available'))
            
            return download_url
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Failed to get download URL: {str(e)}")
            raise UserError(_('Failed to get download URL: %s') % str(e))
