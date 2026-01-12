# -*- coding: utf-8 -*-
import logging
import base64
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    # OneDrive specific fields
    onedrive_file_id = fields.Char(
        string='OneDrive File ID',
        readonly=True,
        help='OneDrive unique file identifier'
    )
    
    onedrive_path = fields.Char(
        string='OneDrive Path',
        readonly=True,
        help='Full path of file in OneDrive'
    )
    
    onedrive_web_url = fields.Char(
        string='OneDrive Web URL',
        readonly=True,
        help='Web URL to view file in OneDrive'
    )
    
    is_onedrive = fields.Boolean(
        string='Stored in OneDrive',
        compute='_compute_is_onedrive',
        store=True,
        help='Indicates if this attachment is stored in OneDrive'
    )
    
    @api.depends('type', 'url', 'onedrive_file_id')
    def _compute_is_onedrive(self):
        """Check if attachment is stored in OneDrive"""
        for attachment in self:
            attachment.is_onedrive = bool(
                attachment.type == 'url' and 
                attachment.onedrive_file_id
            )
    
    @api.model
    def _get_onedrive_config(self, company_id=None):
        """Get OneDrive configuration"""
        if not company_id:
            company_id = self.env.company.id
        
        config = self.env['onedrive.config'].get_config(company_id)
        
        if config and config.active:
            return config
        
        return None
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to upload files to OneDrive"""
        processed_vals = []
        
        for vals in vals_list:
            company_id = vals.get('company_id') or self.env.company.id
            config = self._get_onedrive_config(company_id)
            
            # Check if we should upload to OneDrive
            if config and config.active and vals.get('datas'):
                try:
                    # Extract file data
                    file_content = base64.b64decode(vals['datas'])
                    filename = vals.get('name', 'unknown')
                    model = vals.get('res_model')
                    res_id = vals.get('res_id')
                    
                    # Upload to OneDrive
                    _logger.info(f"Uploading attachment to OneDrive: {filename}")
                    
                    client = self.env['onedrive.client']
                    file_metadata = client.upload_file(
                        file_content=file_content,
                        filename=filename,
                        model=model,
                        res_id=res_id,
                        company_id=company_id
                    )
                    
                    # Update vals to store URL instead of binary
                    vals.update({
                        'type': 'url',
                        'url': file_metadata['download_url'],
                        'datas': False,  # Remove binary data
                        'db_datas': False,
                        'store_fname': False,
                        'onedrive_file_id': file_metadata['id'],
                        'onedrive_path': file_metadata['path'],
                        'onedrive_web_url': file_metadata['web_url'],
                    })
                    
                    # Store file_size separately - will be set after creation
                    vals['_onedrive_file_size'] = file_metadata['size']
                    
                    _logger.info(f"Successfully uploaded to OneDrive: {filename}")
                    
                except Exception as e:
                    _logger.error(f"Failed to upload to OneDrive: {str(e)}")
                    
                    # Fallback: store locally if OneDrive fails
                    _logger.warning(f"Falling back to local storage for: {vals.get('name')}")
                    # Keep original vals (will store locally)
            
            processed_vals.append(vals)
        
        # Create all attachment records at once
        attachments = super(IrAttachment, self).create(processed_vals)
        
        # Set file_size for OneDrive attachments (must be done after creation)
        for i, attachment in enumerate(attachments):
            if processed_vals[i].get('_onedrive_file_size'):
                attachment.sudo().write({
                    'file_size': processed_vals[i]['_onedrive_file_size']
                })
        
        return attachments
    
    def unlink(self):
        """Override unlink to delete files from OneDrive"""
        for attachment in self:
            if attachment.is_onedrive and attachment.onedrive_file_id:
                try:
                    _logger.info(f"Deleting from OneDrive: {attachment.name}")
                    
                    client = self.env['onedrive.client']
                    client.delete_file(
                        file_id=attachment.onedrive_file_id,
                        company_id=attachment.company_id.id if attachment.company_id else None
                    )
                    
                    _logger.info(f"Successfully deleted from OneDrive: {attachment.name}")
                    
                except Exception as e:
                    _logger.error(f"Failed to delete from OneDrive: {str(e)}")
                    # Continue with Odoo deletion even if OneDrive deletion fails
        
        return super(IrAttachment, self).unlink()
    
    def _get_datas(self):
        """Override to fetch data from OneDrive when needed"""
        self.ensure_one()
        
        if self.is_onedrive and self.url:
            try:
                # Fetch file content from OneDrive
                _logger.info(f"Fetching file from OneDrive: {self.name}")
                
                response = requests.get(self.url, timeout=60)
                response.raise_for_status()
                
                return base64.b64encode(response.content)
                
            except Exception as e:
                _logger.error(f"Failed to fetch from OneDrive: {str(e)}")
                raise UserError(_('Failed to download file from OneDrive: %s') % str(e))
        
        return super(IrAttachment, self)._get_datas()
    
    def action_download(self):
        """Redirect to OneDrive download URL"""
        self.ensure_one()
        
        if self.is_onedrive and self.url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.url,
                'target': 'new',
            }
        
        return super(IrAttachment, self).action_download()
    
    @api.model
    def migrate_to_onedrive(self, company_id=None, batch_size=50):
        """
        Migrate existing binary attachments to OneDrive
        
        Args:
            company_id: Specific company ID to migrate (None for current company)
            batch_size: Number of files to process in one batch
        """
        if not company_id:
            company_id = self.env.company.id
        
        config = self._get_onedrive_config(company_id)
        
        if not config or not config.active:
            _logger.warning(f"OneDrive not configured for company {company_id}")
            return
        
        # Find binary attachments that need migration
        domain = [
            ('company_id', '=', company_id),
            ('type', '=', 'binary'),
            ('datas', '!=', False),
        ]
        
        attachments = self.search(domain, limit=batch_size)
        
        if not attachments:
            _logger.info("No attachments to migrate")
            return
        
        _logger.info(f"Starting migration of {len(attachments)} attachments to OneDrive")
        
        success_count = 0
        error_count = 0
        
        for attachment in attachments:
            try:
                _logger.info(f"Migrating attachment: {attachment.name} (ID: {attachment.id})")
                
                # Get binary data
                file_content = base64.b64decode(attachment.datas)
                
                # Upload to OneDrive
                client = self.env['onedrive.client']
                file_metadata = client.upload_file(
                    file_content=file_content,
                    filename=attachment.name,
                    model=attachment.res_model,
                    res_id=attachment.res_id,
                    company_id=company_id
                )
                
                # Update attachment record - clear binary data first
                attachment.write({
                    'type': 'url',
                    'url': file_metadata['download_url'],
                    'datas': False,
                    'db_datas': False,
                    'store_fname': False,
                    'onedrive_file_id': file_metadata['id'],
                    'onedrive_path': file_metadata['path'],
                    'onedrive_web_url': file_metadata['web_url'],
                })
                
                # Write file_size separately with sudo to bypass computed field protection
                attachment.sudo().write({
                    'file_size': file_metadata['size'],
                })
                
                # Commit after each successful migration
                self.env.cr.commit()
                
                success_count += 1
                _logger.info(f"Successfully migrated: {attachment.name}")
                
            except Exception as e:
                error_count += 1
                _logger.error(f"Failed to migrate attachment {attachment.name}: {str(e)}")
                
                # Log error but continue with next attachment
                self.env.cr.rollback()
                continue
        
        _logger.info(f"Migration completed: {success_count} successful, {error_count} failed")
        
        # Update last sync date
        config.write({'last_sync_date': fields.Datetime.now()})
        
        # If there are more attachments, schedule another run
        remaining = self.search_count(domain)
        if remaining > 0:
            _logger.info(f"{remaining} attachments remaining to migrate")
        else:
            _logger.info("All attachments have been migrated to OneDrive!")
            # Disable the cron job since migration is complete
            cron = self.env.ref('onedrive_attachment_storage.ir_cron_onedrive_migration', raise_if_not_found=False)
            if cron:
                cron.active = False
