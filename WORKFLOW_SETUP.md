# Two-Party Signature Workflow for Contract DocType

## Overview

This document describes the complete setup and usage of the Two-Party Signature Workflow implemented in the `corex_contract` Frappe app. This workflow enables a structured process for contract signing between your company and a second party (customer, supplier, or employee).

## Table of Contents

- [Architecture](#architecture)
- [Installation Instructions](#installation-instructions)
- [Fresh Bench Installation](#fresh-bench-installation)
- [Existing Site Installation](#existing-site-installation)
- [Workflow Process](#workflow-process)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Files Reference](#files-reference)

---

## Architecture

### Workflow States

```
Draft → Pending Party Signature → Signed by Party → Active
         ↑                              ↓
         └──────────── Reject ──────────┘
```

1. **Draft** (docstatus=0)
   - HR Manager creates and prepares contract
   - Party details are filled (party_name, party_user)
   - Action: "Send for Signature"

2. **Pending Party Signature** (docstatus=0)
   - Party receives email notification with signing link
   - Party accesses web form to sign
   - Action: "Sign Contract"

3. **Signed by Party** (docstatus=0)
   - HR Manager receives notification
   - HR Manager reviews and adds company signature
   - Action: "Approve and Submit" or "Reject"

4. **Active** (docstatus=1)
   - Contract is submitted and finalized
   - Both signatures are permanently recorded

### Custom Fields Added

| Field Name | Type | Description |
|------------|------|-------------|
| `party_signature` | Signature | Captures the second party's signature via web form |
| `party_signed_on` | Datetime | Auto-populated timestamp when party signs |

### Components

- **Workflow**: Contract Two-Party Signature
- **Web Form**: sign-contract (route: `/sign-contract`)
- **Notifications**: 2 email alerts for state changes
- **Client Script**: Copy signature link button
- **Server Hook**: Auto-timestamp functionality

---

## Installation Instructions

### Prerequisites

- Frappe/ERPNext instance running
- `corex_contract` app added to bench
- Site access with Administrator privileges

---

## Fresh Bench Installation

If you're installing the `corex_contract` app on a **new bench** (fresh setup):

### Step 1: Get the App

```bash
cd /path/to/your/bench
bench get-app https://github.com/your-org/corex_contract.git
```

*Note: Replace with your actual repository URL*

### Step 2: Create a New Site (if needed)

```bash
bench new-site your-site-name.local
```

### Step 3: Install Required Apps

```bash
# Install ERPNext first (required dependency)
bench --site your-site-name.local install-app erpnext

# Install corex_contract
bench --site your-site-name.local install-app corex_contract
```

### Step 4: Run the Workflow Installation Script

```bash
bench --site your-site-name.local execute "corex_contract.install_workflow.install_workflow"
```

### Step 5: Restart Bench

```bash
bench restart
```

### Step 6: Clear Cache and Build Assets

```bash
bench --site your-site-name.local clear-cache
bench build
```

---

## Existing Site Installation

If the `corex_contract` app is **already installed** on your site:

### Step 1: Pull Latest Code

```bash
cd /path/to/your/bench/apps/corex_contract
git pull origin main
```

### Step 2: Run Migrate (Optional - if using fixtures)

```bash
bench --site your-site-name.local migrate
```

*Note: Fixtures-based installation may have issues. Use the script method below instead.*

### Step 3: Run the Workflow Installation Script

```bash
bench --site your-site-name.local execute "corex_contract.install_workflow.install_workflow"
```

**Expected Output:**
```
=== Installing Contract Two-Party Signature Workflow ===

Step 1: Creating Custom Fields...
Created Custom Field: party_signature
Created Custom Field: party_signed_on

Step 2: Creating Workflow States...
Created Workflow State: Draft
Created Workflow State: Pending Party Signature
Created Workflow State: Signed by Party
Created Workflow State: Active

Step 3: Creating Workflow Actions...
Created Workflow Action: Send for Signature
Created Workflow Action: Sign Contract
Created Workflow Action: Approve and Submit
Created Workflow Action: Reject

Step 4: Creating Workflow...
Created Workflow: Contract Two-Party Signature

Step 5: Creating Web Form...
Created Web Form: sign-contract

Step 6: Creating Notifications...
Created Notification: Contract - Party Signature Required
Created Notification: Contract - Party Signed

=== Installation Complete! ===
```

### Step 4: Restart and Clear Cache

```bash
bench restart
bench --site your-site-name.local clear-cache
bench build
```

### Step 5: Verify Installation

1. Login to your site as Administrator
2. Go to: **Workflow** List
3. Verify "Contract Two-Party Signature" workflow exists and is Active
4. Go to: **Custom Field** List
5. Search for "Contract-party_signature" and "Contract-party_signed_on"
6. Go to: **Web Form** List
7. Verify "sign-contract" web form exists

---

## Workflow Process

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    HR Manager Actions                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                        [1. Create Contract]
                        - Fill party details
                        - Set party_user email
                        - Add contract terms
                              │
                              ▼
                    [2. Send for Signature]
                    (Workflow Action Button)
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Email Sent to Party   │
                  │ with Signing Link     │
                  └───────────────────────┘
                              │
┌─────────────────────────────┴─────────────────────────────┐
│                    Party Actions (Portal)                 │
└───────────────────────────────────────────────────────────┘
                              │
                              ▼
                    [3. Party Receives Email]
                    Click link to access web form
                              │
                              ▼
                    [4. Party Reviews Contract]
                    - Read contract terms
                    - View start/end dates
                              │
                              ▼
                    [5. Party Signs Contract]
                    Draw signature in signature pad
                              │
                              ▼
                    [6. Submit Web Form]
                    (Auto-updates workflow state)
                              │
                              ▼
                  ┌───────────────────────┐
                  │ Email Sent to HR      │
                  │ "Party Signed"        │
                  └───────────────────────┘
                              │
┌─────────────────────────────┴─────────────────────────────┐
│                HR Manager Final Actions                    │
└───────────────────────────────────────────────────────────┘
                              │
                              ▼
                    [7. HR Reviews Signature]
                    Verify party signature is valid
                              │
                              ▼
                    [8. HR Adds Company Signature]
                    Fill "Signee Company" field
                              │
                              ▼
                    [9. Approve and Submit]
                    (Workflow Action Button)
                              │
                              ▼
                    ┌─────────────────┐
                    │ Contract Active │
                    │  docstatus = 1  │
                    └─────────────────┘
```

---

## Configuration

### 1. Email Configuration (Required for Notifications)

#### Configure SMTP Settings

1. Go to: **Email Account** List
2. Create/Edit your default email account
3. Fill in SMTP settings:
   - Email ID: your-email@company.com
   - SMTP Server: smtp.gmail.com (for Gmail)
   - Use TLS: Yes
   - Port: 587
   - Login ID: your-email@company.com
   - Password: Your app password (not regular password)

4. Enable:
   - [x] Enable Outgoing
   - [x] Default Outgoing

5. Save and test by clicking "Send Test Email"

#### Verify Notification Settings

1. Go to: **Notification** List
2. Find: "Contract - Party Signature Required"
3. Ensure:
   - Enabled: ✓
   - Channel: Email
   - Event: Value Change
   - Value Changed: workflow_state
4. Repeat for "Contract - Party Signed"

### 2. Create Portal Users (Required)

Portal users are needed for parties to sign contracts.

#### Create Portal User Manually

1. Go to: **User** List
2. Click: **New**
3. Fill:
   - Email: party@example.com
   - First Name: Party
   - Last Name: Name
   - **User Type: Website User** (Important!)
4. Add Roles:
   - Customer (or Supplier/Employee as appropriate)
5. Save

#### Create Portal User via Console

```bash
bench --site your-site-name.local console
```

```python
# In console:
user = frappe.get_doc({
    "doctype": "User",
    "email": "party@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "Website User"
})
user.insert()
user.add_roles("Customer")
frappe.db.commit()
```

### 3. Role Permissions

Ensure the following roles have proper permissions:

#### HR Manager Role
- Can create, read, update, submit Contracts
- Can execute workflow actions: Send for Signature, Approve and Submit, Reject

#### Customer Role (Portal)
- Can read their own contracts (where party_user = their email)
- Can update party_signature field
- Can execute workflow action: Sign Contract

#### Verify Permissions

1. Go to: **Role Permissions Manager**
2. Select: **Contract**
3. Verify roles have appropriate access

---

## Usage Guide

### For HR Manager

#### Step 1: Create New Contract

1. Go to: **Contract** List
2. Click: **New**
3. Fill Required Fields:
   ```
   Party Type: Customer
   Party Name: [Select Customer]
   Party User: [Portal user email - e.g., john@example.com]

   Contract Template: [Optional]
   Contract Terms: [Enter terms or use template]

   Start Date: 2025-01-01
   End Date: 2025-12-31

   Signed By Company: [Your name/user]
   ```
4. Save Contract
5. **Workflow State**: Draft

#### Step 2: Send for Signature

1. Open the saved contract
2. Click: **Send for Signature** (workflow action button)
3. System validates:
   - ✓ party_user field is filled
4. **Workflow State** changes to: Pending Party Signature
5. **Email sent to**: party_user email with signing link

#### Step 3: Copy Signature Link (Optional)

- Click: **Copy Signature Link** button (custom button added by script)
- Share link manually via WhatsApp, SMS, etc.
- Link format: `https://your-site.com/sign-contract?name=CON-2025-00001`

#### Step 4: Wait for Party to Sign

- Monitor email for "Contract [X] - Party Signature Received"
- Or check Contract list for workflow_state = "Signed by Party"

#### Step 5: Review Party Signature

1. Open contract with workflow_state = "Signed by Party"
2. Scroll to **Party Signature** field
3. Verify signature is present
4. Check **Party Signed On** timestamp

#### Step 6: Add Company Signature

1. Scroll to **Signee Company** field (existing ERPNext field)
2. Draw company signature in signature pad
3. Save contract

#### Step 7: Approve and Submit

1. Click: **Approve and Submit** (workflow action button)
2. System validates:
   - ✓ party_signature is filled
   - ✓ signee_company is filled
3. **Workflow State** changes to: Active
4. **docstatus** changes to: 1 (Submitted)
5. Contract is now finalized and immutable

#### Alternative: Reject Contract

If party signature is invalid or contract needs changes:

1. Click: **Reject** (workflow action button)
2. **Workflow State** returns to: Draft
3. Make necessary changes
4. Repeat process from Step 2

---

### For Party User (Portal)

#### Step 1: Receive Email Notification

You'll receive an email with subject:
```
Action Required: Sign Contract CON-2025-00001
```

Email contains:
- Contract number
- Start date and end date
- Clickable link to sign contract

#### Step 2: Access Signing Form

1. Click link in email (or paste manually in browser)
2. URL: `https://your-site.com/sign-contract?name=CON-2025-00001`
3. **Login Required**: Enter your portal user credentials

#### Step 3: Review Contract Details

Web form displays (read-only):
- Party Name
- Contract Terms (full text)
- Start Date
- End Date

#### Step 4: Sign Contract

1. Scroll to **Your Signature** section
2. Use mouse/touchscreen to draw signature in signature pad
3. Signature is required (cannot submit without it)

#### Step 5: Submit Signature

1. Click: **Submit Signature** button
2. Success message appears:
   ```
   Contract Signed Successfully

   Thank you for signing the contract.
   The company will review and finalize it.
   ```
3. **Workflow State** automatically changes to: Signed by Party
4. **party_signed_on** timestamp is auto-recorded

---

## Testing

### Test Scenario: Complete Workflow

#### Prerequisites
- SMTP configured
- Portal user created: test@example.com
- HR Manager user: admin@yoursite.com

#### Test Steps

1. **Login as HR Manager** (admin@yoursite.com)
   ```
   ✓ Create new Contract
   ✓ Party User: test@example.com
   ✓ Fill contract terms
   ✓ Save
   ✓ Verify workflow_state = "Draft"
   ```

2. **Send for Signature**
   ```
   ✓ Click "Send for Signature"
   ✓ Verify workflow_state = "Pending Party Signature"
   ✓ Check email sent to test@example.com
   ```

3. **Login as Portal User** (test@example.com)
   ```
   ✓ Open email
   ✓ Click signature link
   ✓ Login to portal
   ✓ Web form loads with contract details
   ✓ All fields are read-only except signature
   ```

4. **Sign Contract**
   ```
   ✓ Draw signature in signature pad
   ✓ Click "Submit Signature"
   ✓ Success message appears
   ✓ Verify workflow_state = "Signed by Party"
   ✓ Verify party_signed_on has timestamp
   ```

5. **Login as HR Manager** (admin@yoursite.com)
   ```
   ✓ Check email: "Contract [X] - Party Signature Received"
   ✓ Open contract
   ✓ Verify party_signature field is filled
   ✓ Add company signature (signee_company field)
   ✓ Save
   ```

6. **Approve and Submit**
   ```
   ✓ Click "Approve and Submit"
   ✓ Verify workflow_state = "Active"
   ✓ Verify docstatus = 1
   ✓ Verify status = "Active"
   ✓ Contract is now read-only (submitted)
   ```

### Test Scenario: Rejection Flow

1. **After party signs** (Step 4 above)
2. **Login as HR Manager**
   ```
   ✓ Open contract with workflow_state = "Signed by Party"
   ✓ Click "Reject"
   ✓ Verify workflow_state returns to "Draft"
   ✓ Make changes to contract terms
   ✓ Save
   ✓ Click "Send for Signature" again
   ✓ Party can sign again
   ```

---

## Troubleshooting

### Issue 1: Workflow Not Appearing

**Symptoms:**
- Workflow action buttons not showing in Contract form
- workflow_state field not visible

**Solutions:**
1. Verify workflow is active:
   ```bash
   bench --site your-site.local execute "
   frappe.db.set_value('Workflow', 'Contract Two-Party Signature', 'is_active', 1)
   frappe.db.commit()
   "
   ```

2. Clear cache:
   ```bash
   bench --site your-site.local clear-cache
   bench restart
   ```

3. Check workflow assignment:
   - Go to: Workflow List
   - Open: "Contract Two-Party Signature"
   - Verify: Document Type = "Contract"
   - Verify: Is Active = ✓

### Issue 2: Email Not Sending

**Symptoms:**
- Party doesn't receive signature request email
- HR doesn't receive party signed notification

**Solutions:**
1. Verify SMTP configuration:
   ```bash
   bench --site your-site.local console
   ```
   ```python
   frappe.sendmail(
       recipients=["test@example.com"],
       subject="Test Email",
       message="Test message"
   )
   ```

2. Check Email Account:
   - Go to: Email Account List
   - Verify: Enable Outgoing = ✓
   - Test: Click "Send Test Email"

3. Check Notification:
   - Go to: Notification List
   - Find: "Contract - Party Signature Required"
   - Verify: Enabled = ✓
   - Verify: Channel = "Email"

4. Check Email Queue:
   - Go to: Email Queue List
   - Check for failed emails
   - View error messages

### Issue 3: Web Form Shows "Not Permitted"

**Symptoms:**
- Party clicks link but sees "Not Permitted" error
- Cannot access contract signing form

**Solutions:**
1. Verify party_user email matches logged-in user:
   - Contract's party_user field must exactly match portal user email

2. Verify workflow state:
   - Web form only works when workflow_state = "Pending Party Signature"

3. Verify user type:
   - Go to: User List
   - Find party user
   - Verify: User Type = "Website User" (NOT System User)

4. Verify role:
   - User must have "Customer" role (or Supplier/Employee)

5. Check web form settings:
   - Go to: Web Form List
   - Open: "sign-contract"
   - Verify: Published = ✓
   - Verify: Login Required = ✓
   - Verify: Apply Document Permissions = ✓

### Issue 4: Signature Field Not Visible

**Symptoms:**
- party_signature field not showing in Contract form
- Custom fields missing

**Solutions:**
1. Verify custom field exists:
   ```bash
   bench --site your-site.local console
   ```
   ```python
   frappe.db.exists("Custom Field", "Contract-party_signature")
   # Should return: Contract-party_signature
   ```

2. Re-run installation:
   ```bash
   bench --site your-site.local execute "corex_contract.install_workflow.install_workflow"
   ```

3. Clear cache:
   ```bash
   bench --site your-site.local clear-cache
   bench restart
   ```

4. Check field dependencies:
   - Custom field has depends_on condition
   - Field only shows when workflow_state is in specific states

### Issue 5: Workflow Action Button Not Showing

**Symptoms:**
- Cannot see "Send for Signature" button
- Cannot see "Sign Contract" or "Approve and Submit" buttons

**Solutions:**
1. Verify user has correct role:
   - HR Manager: See all buttons in Draft and Signed by Party states
   - Customer: See "Sign Contract" button in Pending Party Signature state

2. Check transition conditions:
   - "Send for Signature" requires party_user field filled
   - "Approve and Submit" requires both party_signature and signee_company filled

3. Reload page:
   - Press Ctrl+F5 (hard refresh)
   - Clear browser cache

### Issue 6: Auto-Timestamp Not Working

**Symptoms:**
- party_signed_on field remains empty after signing
- Timestamp not recorded

**Solutions:**
1. Verify document event hook:
   ```bash
   bench --site your-site.local console
   ```
   ```python
   from corex_contract import hooks
   print(hooks.doc_events)
   # Should show Contract: on_update hook
   ```

2. Manually trigger:
   ```python
   contract = frappe.get_doc("Contract", "CON-2025-00001")
   if contract.party_signature and not contract.party_signed_on:
       contract.db_set('party_signed_on', frappe.utils.now_datetime())
       frappe.db.commit()
   ```

3. Re-run workflow installation:
   ```bash
   bench --site your-site.local execute "corex_contract.install_workflow.install_workflow"
   bench restart
   ```

### Issue 7: Copy Link Button Not Showing

**Symptoms:**
- "Copy Signature Link" button missing from Contract form

**Solutions:**
1. Verify client script is loaded:
   - Press F12 (developer tools)
   - Check Console for errors

2. Verify hooks.py configuration:
   ```python
   # In hooks.py
   doctype_js = {"Contract": "public/js/contract.js"}
   ```

3. Build assets:
   ```bash
   bench build --app corex_contract
   bench restart
   ```

4. Clear browser cache:
   - Ctrl+F5 or Ctrl+Shift+R

---

## Files Reference

### Created Files Structure

```
corex_contract/
├── corex_contract/
│   ├── fixtures/
│   │   ├── custom_field.json           # Party signature fields
│   │   ├── workflow_state.json         # 4 workflow states
│   │   ├── workflow.json               # Main workflow definition
│   │   ├── web_form.json               # Portal signing form
│   │   └── notification.json           # Email alerts
│   │
│   ├── public/
│   │   └── js/
│   │       └── contract.js             # Client script: Copy link button
│   │
│   ├── hooks.py                        # App configuration
│   ├── contract_hooks.py               # Server hooks: Auto-timestamp
│   └── install_workflow.py            # Installation script
│
├── WORKFLOW_SETUP.md                   # This file
└── README.md
```

### Key Files Explanation

#### 1. `install_workflow.py`

**Purpose**: Programmatically creates all workflow components

**Functions**:
- `create_custom_fields()` - Adds party_signature and party_signed_on fields
- `create_workflow_states()` - Creates 4 workflow states
- `create_workflow_actions()` - Creates workflow action masters
- `create_workflow()` - Creates main workflow with transitions
- `create_web_form()` - Creates portal signing form
- `create_notifications()` - Creates email notifications
- `install_workflow()` - Main installation function

**Usage**:
```bash
bench --site your-site.local execute "corex_contract.install_workflow.install_workflow"
```

#### 2. `hooks.py`

**Purpose**: App configuration and hooks

**Key Sections**:
```python
# Fixtures configuration (for version control)
fixtures = [...]

# Client script registration
doctype_js = {"Contract": "public/js/contract.js"}

# Server-side event hooks
doc_events = {
    "Contract": {
        "on_update": "corex_contract.contract_hooks.on_contract_update"
    }
}
```

#### 3. `contract_hooks.py`

**Purpose**: Server-side business logic

**Function**: `on_contract_update(doc, method)`
- Triggered every time Contract is updated
- Auto-fills party_signed_on when party_signature is added
- Ensures timestamp is always recorded

#### 4. `public/js/contract.js`

**Purpose**: Client-side enhancements

**Features**:
- Adds "Copy Signature Link" button
- Adds "Send Reminder" button
- Shows only in "Pending Party Signature" state

#### 5. `fixtures/*.json`

**Purpose**: Configuration as code (version control)

**Note**: These fixture files are for reference and future export. The actual installation uses `install_workflow.py` script because fixtures have dependency issues.

**Export Command** (if you make UI changes):
```bash
bench --site your-site.local export-fixtures
```

This exports your UI-created configurations to JSON files.

---

## Deployment Checklist

### Pre-Deployment

- [ ] Code committed to git repository
- [ ] Repository accessible from production server
- [ ] Backup production database
- [ ] Notify users of maintenance window

### Deployment Steps

- [ ] Pull latest code: `git pull origin main`
- [ ] Run installation script
- [ ] Clear cache and restart
- [ ] Build assets
- [ ] Test workflow with sample contract
- [ ] Verify email notifications work
- [ ] Verify web form accessible

### Post-Deployment

- [ ] Create portal users for parties
- [ ] Configure SMTP (if not already done)
- [ ] Train HR staff on workflow
- [ ] Send test contract to verify end-to-end flow
- [ ] Monitor for errors in Error Log

---

## Support and Maintenance

### Checking Workflow Status

```bash
bench --site your-site.local console
```

```python
# Check if workflow exists and is active
workflow = frappe.get_doc("Workflow", "Contract Two-Party Signature")
print(f"Is Active: {workflow.is_active}")
print(f"States: {[s.state for s in workflow.states]}")

# Check custom fields
fields = frappe.get_all("Custom Field",
    filters={"dt": "Contract"},
    fields=["name", "fieldname", "label"])
print(fields)

# Check web form
web_form = frappe.get_doc("Web Form", "sign-contract")
print(f"Published: {web_form.published}")
print(f"Route: {web_form.route}")
```

### Debugging Contract Issues

```python
# Get contract and check workflow state
contract = frappe.get_doc("Contract", "CON-2025-00001")
print(f"Workflow State: {contract.workflow_state}")
print(f"Party User: {contract.party_user}")
print(f"Party Signature: {bool(contract.party_signature)}")
print(f"Party Signed On: {contract.party_signed_on}")
print(f"Doc Status: {contract.docstatus}")
```

### Re-running Installation

If workflow becomes corrupted or you need to reset:

```bash
# This will recreate all components
bench --site your-site.local execute "corex_contract.install_workflow.install_workflow"
```

**Note**: Script checks for existing records and only creates missing ones. Safe to run multiple times.

---

## Advanced Configuration

### Customizing Email Templates

1. Go to: **Notification** List
2. Open: "Contract - Party Signature Required"
3. Edit **Message** field to customize email content
4. Use Jinja templates:
   ```
   Dear {{ doc.party_name }},

   Please sign contract {{ doc.name }}
   Link: {{ frappe.utils.get_url() }}/sign-contract?name={{ doc.name }}

   Contract Period: {{ doc.start_date }} to {{ doc.end_date }}
   ```

### Adding More Workflow States

If you need additional approval stages:

1. Go to: **Workflow State** List
2. Create new state (e.g., "Legal Review")
3. Go to: **Workflow** - "Contract Two-Party Signature"
4. Add new state in **States** table
5. Add transitions to/from new state

### Customizing Web Form

1. Go to: **Web Form** List
2. Open: "sign-contract"
3. Add/remove fields in **Web Form Fields** table
4. Customize **Introduction Text** for branding
5. Modify **Success Message**

### Adding Signature Expiry

To add a deadline for signing:

1. Add Custom Field: `signature_deadline` (Date)
2. Modify notification to include deadline
3. Create scheduled job to auto-reject expired contracts

---

## Security Considerations

### Portal User Access

- Portal users can only access contracts where `party_user = their email`
- Enforced by: `apply_document_permissions = 1` in web form
- Users cannot see other parties' contracts

### Signature Integrity

- Once submitted (docstatus=1), signatures cannot be modified
- Enforced by: `allow_on_submit = 1` but workflow prevents edit after Active state
- Audit trail maintained via workflow history

### Email Security

- Use strong SMTP passwords
- Enable TLS/SSL for email transmission
- Consider using app-specific passwords (Gmail)

---

## FAQ

### Q: Can I use this for more than two signatures?

A: Current workflow supports two signatures (party + company). For multiple signatories, you would need to:
- Add more custom fields (party2_signature, party3_signature)
- Add more workflow states
- Modify workflow transitions
- Create additional web forms

### Q: Can I skip the email notification?

A: Yes. Disable notifications:
1. Go to: Notification List
2. Uncheck **Enabled** for both notifications
3. Manually share link using "Copy Signature Link" button

### Q: Can the party sign without logging in?

A: No. Current implementation requires portal login for security and audit trail. To allow anonymous signing, you would need to:
- Modify web form: `login_required = 0`
- Implement signed URL with token
- Add security measures to prevent unauthorized access

### Q: How do I change the signature link URL?

A: The web form route is set to `sign-contract`. To change:
1. Go to: Web Form - "sign-contract"
2. Change **Route** field to desired URL
3. Update notifications to use new route

### Q: Can I add custom validation before submission?

A: Yes. Edit `contract_hooks.py`:

```python
def on_contract_update(doc, method):
    # Existing code...

    # Add custom validation
    if doc.workflow_state == "Signed by Party":
        if not doc.get("custom_field"):
            frappe.throw("Custom field is required")
```

---

## License

MIT License - Part of corex_contract app

---

## Credits

- **App**: corex_contract
- **Author**: corex
- **Framework**: Frappe Framework
- **ERP**: ERPNext

---

## Changelog

### Version 1.0.0 (2025-12-08)
- Initial implementation
- Two-party signature workflow
- Web form for portal signing
- Email notifications
- Auto-timestamp functionality
- Copy link button
- Complete documentation

---

## Contact

For issues, feature requests, or support:
- Repository: https://github.com/your-org/corex_contract
- Email: dev@corex.com
- Documentation: This file (WORKFLOW_SETUP.md)

---

**END OF DOCUMENT**
