# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OneDriveConfig(models.Model):
    _name = 'onedrive.config'
    _description = 'OneDrive Storage Configuration'
    _rec_name = 'company_id'

    # Basic Configuration
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        ondelete='cascade'
    )
    
    active = fields.Boolean(
        string='Enable OneDrive Storage',
        default=False,
        help='Enable automatic upload of attachments to OneDrive'
    )
    
    # OAuth2 Configuration
    client_id = fields.Char(
        string='Client ID',
        required=True,
        help='Azure AD Application Client ID'
    )
    
    client_secret = fields.Char(
        string='Client Secret',
        required=True,
        help='Azure AD Application Client Secret'
    )
    
    tenant_id = fields.Char(
        string='Tenant ID',
        required=True,
        help='Azure AD Tenant ID'
    )
    
    drive_id = fields.Char(
        string='Drive ID',
        help='Specific OneDrive/SharePoint Drive ID (optional, uses default if empty)'
    )
    
    # Token Storage (encrypted)
    access_token = fields.Char(
        string='Access Token',
        readonly=True,
        groups='base.group_system'
    )
    
    refresh_token = fields.Char(
        string='Refresh Token',
        readonly=True,
        groups='base.group_system'
    )
    
    token_expiry = fields.Datetime(
        string='Token Expiry',
        readonly=True
    )
    
    # Folder Configuration
    root_folder = fields.Char(
        string='Root Folder',
        default='/Odoo/Attachments',
        required=True,
        help='Root folder path in OneDrive'
    )
    
    use_model_folders = fields.Boolean(
        string='Organize by Model',
        default=True,
        help='Create subfolders for each Odoo model (e.g., sale.order, res.partner)'
    )
    
    use_record_folders = fields.Boolean(
        string='Organize by Record ID',
        default=True,
        help='Create subfolders for each record ID'
    )
    
    use_company_folders = fields.Boolean(
        string='Organize by Company',
        default=False,
        help='Create subfolders for each company (multi-company mode)'
    )
    
    # Status
    last_sync_date = fields.Datetime(
        string='Last Sync Date',
        readonly=True
    )
    
    connection_status = fields.Selection([
        ('not_tested', 'Not Tested'),
        ('connected', 'Connected'),
        ('error', 'Connection Error')
    ], string='Connection Status', default='not_tested', readonly=True)
    
    connection_message = fields.Text(
        string='Connection Message',
        readonly=True
    )
    
    # Statistics
    total_files = fields.Integer(
        string='Total Files in OneDrive',
        compute='_compute_statistics',
        store=False
    )
    
    _sql_constraints = [
        ('company_unique', 'unique(company_id)', 'Only one configuration per company is allowed!')
    ]
    
    @api.model
    def get_config(self, company_id=None):
        """Get OneDrive configuration for a company"""
        if not company_id:
            company_id = self.env.company.id
        
        config = self.search([('company_id', '=', company_id)], limit=1)
        return config
    
    def _compute_statistics(self):
        """Compute statistics about stored files"""
        for record in self:
            attachments = self.env['ir.attachment'].search([
                ('company_id', '=', record.company_id.id),
                ('is_onedrive', '=', True)
            ])
            record.total_files = len(attachments)
    
    def action_test_connection(self):
        """Test OneDrive connection"""
        self.ensure_one()
        
        try:
            client = self.env['onedrive.client'].create_client(self)
            
            # Try to get user info to test connection
            user_info = client.get_me()
            
            self.write({
                'connection_status': 'connected',
                'connection_message': f"Successfully connected as: {user_info.get('displayName', 'Unknown')}"
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('OneDrive connection successful!'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"OneDrive connection test failed: {str(e)}")
            self.write({
                'connection_status': 'error',
                'connection_message': str(e)
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error'),
                    'message': _('Connection failed: %s') % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }
    
    def action_sync_attachments(self):
        """Start background migration of ALL attachments - returns immediately"""
        self.ensure_one()
        
        if not self.active:
            raise UserError(_('Please enable OneDrive storage first.'))
        
        # Count ONLY binary attachments NOT yet in OneDrive
        domain = [
            ('is_onedrive', '=', False),
            ('type', '=', 'binary'),
            ('company_id', '=', self.company_id.id),
        ]
        total_count = self.env['ir.attachment'].search_count(domain)
        
        if total_count == 0:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('All Done!'),
                    'message': _('All attachments are already in OneDrive.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        
        # Set flag to indicate migration in progress
        self.write({'last_sync_date': fields.Datetime.now()})
        
        # Activate the cron and schedule it to run immediately
        cron = self.env.ref('onedrive_attachment_storage.ir_cron_onedrive_migration')
        cron.sudo().write({
            'active': True,
            'nextcall': fields.Datetime.now()
        })
        
        _logger.info(f"="*80)
        _logger.info(f"BACKGROUND MIGRATION STARTED: {total_count} attachments to migrate")
        _logger.info(f"Cron activated and scheduled to run immediately")
        _logger.info(f"="*80)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Migration Started!'),
                'message': _('Background migration of %s attachments started. Check logs for progress: tail -f ~/logs/odoo.log') % total_count,
                'type': 'success',
                'sticky': True,
            }
        }
    
    def cron_migrate_attachments_batch(self):
        """Cron job that processes multiple batches and reschedules itself"""
        for config in self.search([('active', '=', True)]):
            domain = [
                ('is_onedrive', '=', False),
                ('type', '=', 'binary'),
                ('company_id', '=', config.company_id.id),
            ]
            
            total_remaining = self.env['ir.attachment'].search_count(domain)
            
            if total_remaining == 0:
                _logger.info(f"✓ All attachments migrated for company {config.company_id.name}")
                continue
            
            # Process 2 batches per cron run to avoid timeout (200 files ~= 30 seconds)
            batches_per_run = 2
            batch_size = 100
            total_migrated = 0
            total_failed = 0
            
            _logger.info(f"Processing {batches_per_run} batches ({batches_per_run * batch_size} files) from {total_remaining} remaining...")
            
            for batch_num in range(1, batches_per_run + 1):
                # Check if more files exist
                remaining = self.env['ir.attachment'].search_count(domain)
                if remaining == 0:
                    _logger.info(f"✓ MIGRATION COMPLETE: All files migrated!")
                    return
                
                # Get batch
                attachments = self.env['ir.attachment'].search(domain, limit=batch_size)
                if not attachments:
                    break
                
                # Process batch
                batch_migrated = 0
                batch_failed = 0
                
                for att in attachments:
                    try:
                        att.migrate_to_onedrive()
                        batch_migrated += 1
                        total_migrated += 1
                    except Exception as e:
                        _logger.error(f"Failed to migrate {att.id} ({att.name}): {str(e)}")
                        batch_failed += 1
                        total_failed += 1
                
                # Commit after each batch
                self.env.cr.commit()
                
                _logger.info(f"Batch {batch_num}/{batches_per_run}: {batch_migrated} OK, {batch_failed} failed | Total progress: {total_migrated} migrated")
            
            # Check if more files remain
            remaining_after = self.env['ir.attachment'].search_count(domain)
            
            if remaining_after > 0:
                # Reschedule immediately to continue
                _logger.info(f"→ {remaining_after} files remaining. Rescheduling cron...")
                cron = self.env.ref('onedrive_attachment_storage.ir_cron_onedrive_migration')
                cron.sudo().write({'nextcall': fields.Datetime.now()})
            else:
                _logger.info(f"="*80)
                _logger.info(f"✓ MIGRATION COMPLETE: {total_migrated} total migrated, {total_failed} total failed")
                _logger.info(f"="*80)
    
    def action_open_settings(self):
        """Open OneDrive settings form"""
        config = self.get_config()
        
        if not config:
            config = self.create({
                'company_id': self.env.company.id,
            })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('OneDrive Storage Settings'),
            'res_model': 'onedrive.config',
            'res_id': config.id,
            'view_mode': 'form',
            'target': 'current',
        }
