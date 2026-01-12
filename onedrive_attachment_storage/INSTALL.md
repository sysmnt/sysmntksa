# OneDrive Attachment Storage - Installation Guide

## Quick Start

### Prerequisites
```bash
# Ensure you have Python 3.10+ and pip
python --version

# Verify requests library is installed (usually comes with Odoo)
pip show requests
```

### Installation Steps

#### 1. Install the Module

**Option A: Copy to Odoo addons directory**
```bash
# Copy the entire module folder
cp -r onedrive_attachment_storage /path/to/odoo/addons/

# Or use symbolic link
ln -s /path/to/onedrive_attachment_storage /path/to/odoo/addons/
```

**Option B: Add custom addons path**
```bash
# Edit your Odoo configuration file
nano /etc/odoo/odoo.conf

# Add or update the addons_path line:
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/path/to/custom/addons

# Restart Odoo
sudo systemctl restart odoo
```

#### 2. Update App List in Odoo

1. Log in to Odoo as Administrator
2. Go to **Apps**
3. Click **Update Apps List** (may need to activate Developer Mode first)
4. Click **Update** in the confirmation dialog

#### 3. Install the Module

1. In the Apps menu, search for "OneDrive"
2. Find **OneDrive Attachment Storage**
3. Click **Install**

#### 4. Configure Azure AD

##### 4.1. Create Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Enter:
   - **Name**: Odoo OneDrive Integration
   - **Supported account types**: Single tenant
   - **Redirect URI**: (leave empty for now)
5. Click **Register**

##### 4.2. Note the Application Details

From the Overview page, copy:
- **Application (client) ID**: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- **Directory (tenant) ID**: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

##### 4.3. Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Enter description: "Odoo Integration"
4. Select expiry: 24 months (or your preference)
5. Click **Add**
6. **IMMEDIATELY COPY** the Value (you won't see it again!)

##### 4.4. Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Select **Application permissions** (NOT Delegated)
5. Add these permissions:
   - `Files.ReadWrite.All`
   - `Sites.ReadWrite.All` (optional, for SharePoint)
6. Click **Add permissions**
7. Click **Grant admin consent for [Your Organization]**
8. Confirm by clicking **Yes**

#### 5. Configure Module in Odoo

1. Go to **Settings** → **Technical** → **OneDrive Storage**
2. Click **Create** (if no configuration exists)
3. Fill in the form:
   - **Enable OneDrive Storage**: ✅ Check
   - **Tenant ID**: Paste from Azure (step 4.2)
   - **Client ID**: Paste from Azure (step 4.2)
   - **Client Secret**: Paste from Azure (step 4.3)
   - **Root Folder**: `/Odoo/Attachments` (or your preference)
   - **Organize by Company**: ✅ (optional)
   - **Organize by Model**: ✅ (optional)
   - **Organize by Record ID**: ✅ (optional)
4. Click **Save**

#### 6. Test Connection

1. In the same form, click **Test Connection** button
2. You should see: ✅ "OneDrive connection successful!"
3. Connection Status should show: **Connected**

If you see an error:
- Verify all IDs and secret are correct (no extra spaces)
- Ensure API permissions are granted and consented
- Check Azure AD application is not disabled

#### 7. Migrate Existing Attachments (Optional)

If you have existing attachments in Odoo filestore:

**Option A: Manual Trigger**
1. In the configuration form, click **Sync Existing Attachments**
2. Confirm the action
3. A background job will be created

**Option B: Enable Scheduled Job**
1. Go to **Settings** → **Technical** → **Scheduled Actions**
2. Search for "OneDrive: Migrate Attachments"
3. Click on it to open
4. Set **Active**: ✅
5. Configure interval (e.g., every 1 hour)
6. Click **Save**

Migration will process 50 files per run. Monitor progress in logs:
```bash
tail -f /var/log/odoo/odoo.log | grep -i onedrive
```

## Post-Installation

### Verify Installation

1. Create a test attachment:
   - Go to any module (e.g., Contacts)
   - Open a record
   - Click on **Attachments** (📎 icon)
   - Upload a file
   
2. Check the attachment was uploaded:
   - Go to **Settings** → **Technical** → **OneDrive Storage** → **OneDrive Files**
   - You should see your file listed with OneDrive metadata
   
3. Verify in OneDrive:
   - Open your OneDrive account in browser
   - Navigate to the configured root folder
   - You should see the uploaded file

### Enable Developer Mode (Optional)

For advanced configuration and debugging:

1. Go to **Settings**
2. Scroll to bottom and click **Activate the developer mode**
3. This enables technical menus and features

### Monitor Cron Jobs

1. Go to **Settings** → **Technical** → **Scheduled Actions**
2. Filter by "OneDrive" to see all related jobs:
   - **OneDrive: Migrate Attachments (Batch)**: Disabled by default
   - **OneDrive: Refresh Access Token**: Active (runs every 6 hours)
   - **OneDrive: Cleanup Failed Uploads**: Disabled by default

## Troubleshooting

### Module Not Appearing in Apps

```bash
# Ensure module is in addons path
ls -la /path/to/odoo/addons/onedrive_attachment_storage

# Check Odoo logs for errors
tail -f /var/log/odoo/odoo.log

# Restart Odoo
sudo systemctl restart odoo

# Update apps list again
```

### Connection Test Fails

**Error: "Failed to authenticate with OneDrive"**

Check:
1. Tenant ID, Client ID, Client Secret are correct
2. No extra spaces or line breaks in credentials
3. Client secret hasn't expired
4. API permissions are granted with admin consent
5. Application is enabled in Azure AD

**Error: "Insufficient privileges"**

- Grant **Application permissions** (not Delegated permissions)
- Ensure admin consent is given
- Wait a few minutes for permissions to propagate

### Files Not Uploading

**Check logs:**
```bash
grep -i "onedrive" /var/log/odoo/odoo.log | tail -50
```

**Common issues:**
1. OneDrive storage quota full
2. Network connectivity issues
3. Configuration not enabled (Active checkbox)
4. Token expired (should auto-refresh)

**Fallback behavior:**
- If upload fails, file is stored locally
- Check if files exist in filestore but not OneDrive

### Migration Not Working

**Check scheduled action:**
```bash
# Via Odoo UI
Settings → Technical → Scheduled Actions → "OneDrive: Migrate Attachments"
- Ensure it's Active
- Check Next Execution Date
- Review Last Run and Last Error
```

**Manual trigger:**
```python
# In Odoo shell or developer console
env['ir.attachment'].migrate_to_onedrive(batch_size=10)
```

**Check for attachments to migrate:**
```python
# Count binary attachments
env['ir.attachment'].search_count([
    ('type', '=', 'binary'),
    ('datas', '!=', False)
])
```

## Upgrading

### To upgrade the module:

```bash
# Stop Odoo
sudo systemctl stop odoo

# Backup database
pg_dump odoo_db > backup_$(date +%Y%m%d).sql

# Update module files
cp -r onedrive_attachment_storage /path/to/odoo/addons/

# Start Odoo with update
/path/to/odoo-bin -c /etc/odoo/odoo.conf -u onedrive_attachment_storage

# Or restart and update via UI
sudo systemctl start odoo
# Then: Apps → OneDrive Attachment Storage → Upgrade
```

## Uninstalling

### To safely uninstall:

⚠️ **WARNING**: This will not delete files from OneDrive!

1. **Disable OneDrive storage** first:
   - Settings → Technical → OneDrive Storage
   - Uncheck **Enable OneDrive Storage**
   - Save

2. **Uninstall module**:
   - Apps → OneDrive Attachment Storage
   - Click **Uninstall**
   - Confirm

3. **Clean up OneDrive** (optional):
   - Manually delete files from OneDrive if needed
   - Or keep them as backup

## Performance Tuning

### For large installations:

**Increase batch size:**
Edit `models/ir_attachment.py`:
```python
def migrate_to_onedrive(self, company_id=None, batch_size=100):  # Was 50
```

**Increase cron frequency:**
Settings → Technical → Scheduled Actions → OneDrive: Migrate Attachments
- Change Interval Number to 30
- Change Interval Type to Minutes

**Use dedicated worker:**
For high-volume uploads, consider dedicating an Odoo worker:
```ini
# In odoo.conf
workers = 4
max_cron_threads = 2
```

## Support

### Getting Help

1. **Check logs first:**
   ```bash
   tail -f /var/log/odoo/odoo.log | grep -i onedrive
   ```

2. **Enable verbose logging:**
   ```ini
   # In odoo.conf
   log_level = debug
   ```

3. **Test components individually:**
   ```python
   # Test config
   config = env['onedrive.config'].get_config()
   
   # Test client
   client = env['onedrive.client'].create_client(config)
   
   # Test upload
   client.upload_file(b'test', 'test.txt')
   ```

### Contact Support

- GitHub Issues: [Your Repository URL]
- Email: support@yourcompany.com
- Documentation: [Your Docs URL]

## Additional Resources

- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [Azure AD App Registration Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)
- [Odoo Developer Documentation](https://www.odoo.com/documentation/17.0/developer.html)

---

**Installation support available!**
Contact us if you need help with setup or customization.
