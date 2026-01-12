# ⚡ Quick Start Guide (5 Minutes)

Get OneDrive storage running in 5 minutes or less!

## Prerequisites
- ✅ Odoo 17 installed and running
- ✅ Microsoft 365 or OneDrive for Business account
- ✅ Azure AD admin access

---

## Step 1: Azure Setup (2 minutes)

### 1.1 Create App
1. Go to https://portal.azure.com
2. Search for "App registrations"
3. Click **New registration**
4. Name: `Odoo OneDrive`
5. Click **Register**

### 1.2 Copy IDs
From the Overview page, copy:
- **Tenant ID**: `____-____-____-____`
- **Client ID**: `____-____-____-____`

### 1.3 Create Secret
1. Click **Certificates & secrets**
2. Click **New client secret**
3. Description: `Odoo`
4. Expires: `24 months`
5. Click **Add**
6. **COPY THE VALUE NOW!** (you can't see it again)

### 1.4 Add Permissions
1. Click **API permissions**
2. **Add a permission** → **Microsoft Graph** → **Application permissions**
3. Search and add: `Files.ReadWrite.All`
4. Click **Grant admin consent** → **Yes**

✅ Azure setup complete!

---

## Step 2: Install Module (1 minute)

### Option A: Via UI
1. Copy module to: `/path/to/odoo/addons/`
2. Restart Odoo
3. Go to **Apps** → **Update Apps List**
4. Search: `onedrive`
5. Click **Install**

### Option B: Command Line
```bash
cp -r onedrive_attachment_storage /path/to/odoo/addons/
/path/to/odoo-bin -c /etc/odoo/odoo.conf -u onedrive_attachment_storage
```

✅ Module installed!

---

## Step 3: Configure (2 minutes)

1. Go to: **Settings** → **Technical** → **OneDrive Storage**

2. Fill the form:
   ```
   Enable OneDrive Storage: ✅
   Tenant ID: [paste from Step 1.2]
   Client ID: [paste from Step 1.2]
   Client Secret: [paste from Step 1.3]
   Root Folder: /Odoo/Attachments
   Organize by Model: ✅
   ```

3. Click **Save**

4. Click **Test Connection**

5. You should see: ✅ **"Successfully connected!"**

✅ Configuration complete!

---

## Step 4: Test (30 seconds)

1. Go to **Contacts**
2. Open any contact
3. Click **📎 Attachments**
4. Upload a file
5. Wait for upload

✅ File is now in OneDrive!

**Verify**: 
- Settings → Technical → OneDrive Storage → OneDrive Files
- Should show your uploaded file

---

## Step 5: Migrate Existing Files (Optional)

If you have existing attachments:

1. Settings → Technical → OneDrive Storage
2. Click **Sync Existing Attachments**
3. Confirm
4. Background job created ✅

Files will migrate automatically in batches.

---

## 🎉 Done!

You're now storing all Odoo attachments in OneDrive!

### What happens now?
- ✅ All new uploads go to OneDrive automatically
- ✅ No files stored on your Odoo server
- ✅ Downloads come directly from OneDrive
- ✅ Everything works exactly as before for users

---

## Quick Troubleshooting

### ❌ Connection Test Failed

**Problem**: "Failed to authenticate"

**Fix**:
1. Check all IDs are correct (no extra spaces)
2. Verify admin consent granted
3. Wait 2-3 minutes for Azure to propagate changes
4. Try test connection again

---

### ❌ Upload Failed

**Problem**: File didn't upload to OneDrive

**Check**:
```bash
tail -f /var/log/odoo/odoo.log | grep -i onedrive
```

**Common Fixes**:
- OneDrive storage full → Free up space
- Network issue → Check connectivity
- Token expired → Click Test Connection to refresh

---

### ❌ Can't Find Configuration Menu

**Fix**:
1. Enable Developer Mode:
   - Settings → Scroll to bottom
   - Click "Activate the developer mode"
2. Now go to: Settings → Technical → OneDrive Storage

---

## Need More Help?

📖 **Full Documentation**: See [README.md](README.md)

📝 **Detailed Installation**: See [INSTALL.md](INSTALL.md)

🧪 **Testing Guide**: See [TESTING.md](TESTING.md)

📧 **Support**: support@yourcompany.com

---

## Advanced Options (Optional)

### Enable Automatic Migration
```
Settings → Technical → Scheduled Actions
Search: "OneDrive: Migrate"
Set Active: ✅
Save
```

### Change Folder Structure
```
Settings → Technical → OneDrive Storage
Edit your configuration:
- Organize by Company: ✅
- Organize by Model: ✅
- Organize by Record ID: ✅
Save
```

### View Statistics
```
Settings → Technical → OneDrive Storage
See dashboard:
- Total Files: [count]
- Total Size: [MB]
- Last Sync: [date]
```

---

## Security Notes

🔒 **Secure by default**:
- OAuth2 authentication
- Encrypted token storage
- Automatic token refresh
- Respects Odoo access rights
- Multi-company isolated

⚠️ **Important**:
- Keep client secret secure
- Don't share in version control
- Rotate secrets periodically
- Monitor Azure AD logs

---

## Performance Tips

🚀 **For best performance**:

1. **Large files**: Automatically chunked (nothing to configure)
2. **Many files**: Use scheduled migration with batch size 50-100
3. **Concurrent uploads**: Module handles automatically
4. **Downloads**: Direct from OneDrive (fast!)

---

## What's Next?

### Recommended Actions:
1. ✅ Test with different file types
2. ✅ Test download functionality
3. ✅ Enable migration for existing files
4. ✅ Train users (they won't notice any difference!)
5. ✅ Monitor for a week
6. ✅ Clean up old filestore (after confirming all migrated)

### Optional Enhancements:
- Configure by department (custom)
- Set up date-based folders (custom)
- Integrate with SharePoint (use Drive ID)
- Add regional storage (multi-drive setup)

---

## Success Checklist

- [x] Azure AD app created
- [x] Permissions granted
- [x] Module installed
- [x] Configuration saved
- [x] Connection tested ✅
- [x] Test file uploaded ✅
- [x] File appears in OneDrive ✅
- [x] Download works ✅

**If all checked: You're done! 🎉**

---

## Pro Tips

💡 **Tip 1**: Monitor the first week
```bash
# Watch uploads in real-time
tail -f /var/log/odoo/odoo.log | grep -i onedrive
```

💡 **Tip 2**: Set up alerts
Configure Azure AD to alert you on:
- High API usage
- Authentication failures
- Storage quota warnings

💡 **Tip 3**: Document your setup
Save your configuration details securely:
- Tenant ID
- Client ID
- Secret expiry date (set calendar reminder!)
- Drive ID (if using specific drive)

💡 **Tip 4**: Plan for secret rotation
Client secrets expire! Set a reminder for:
- 30 days before expiry
- Create new secret
- Update in Odoo
- Delete old secret

---

**Time to complete**: ⏱️ 5 minutes

**Difficulty**: ⭐ Easy

**Support**: 📧 Available

---

Happy cloud storage! ☁️
