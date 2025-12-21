# Quick Start Guide - Testing New Features

## Starting the Application

```bash
# Navigate to project directory
cd C:\Users\frank_bu9unws\Desktop\Flaskstuff

# Activate virtual environment (if not already active)
.venv\Scripts\activate

# Run the application
python run.py
```

The application will start at `http://127.0.0.1:5000`

---

## Testing Profile Management

### 1. View Your Profile

1. Log in with admin credentials
2. Click **"Profile"** in the navigation bar
3. You'll see your profile page with:
   - Default gradient avatar (since no picture uploaded yet)
   - Empty fields (display name, bio, etc.)
   - "Edit Profile" button
   - "Change Password" button

### 2. Edit Your Profile

1. Click **"Edit Profile"**
2. Fill in the form:
   - **Display Name**: Your preferred name
   - **Email**: Your email address
   - **Bio**: A short description about yourself
   - **Location**: Where you're located
   - **Website**: Your personal website URL
   - **Twitter**: Your Twitter handle (without @)
   - **GitHub**: Your GitHub username

3. **Upload a Profile Picture**:
   - Click "Choose File"
   - Select an image (PNG, JPG, JPEG, or GIF)
   - The file will be uploaded when you submit

4. Click **"Update Profile"**
5. You'll be redirected to your profile page showing the updates

### 3. View Another User's Profile

1. If other users exist, navigate to `/profile/<their-username>`
2. You'll see their public profile (read-only)
3. No "Edit Profile" button will appear (not your profile)

---

## Testing Email Templates

### 1. Test Welcome Email

**Option A: Subscribe through the website**
1. Go to the homepage
2. Enter an email in the newsletter subscription form
3. Click "Subscribe"
4. Check that email inbox for the welcome email

**Option B: Test directly (requires Python shell)**
```python
# Run Python shell in project context
python

# Import and test
from app.core.tasks import send_welcome_email_sync
send_welcome_email_sync('your-test-email@example.com')
```

**What to verify**:
- ✅ Email arrives in inbox
- ✅ Header has purple-cyan gradient
- ✅ Welcome message displays correctly
- ✅ Benefits list shows with checkmarks
- ✅ "Browse All Articles" button is clickable
- ✅ "Visit Homepage" button is clickable
- ✅ Footer links work
- ✅ Unsubscribe link works
- ✅ Email looks good on mobile

### 2. Test Article Notification Email

**Steps**:
1. Make sure you're subscribed to the newsletter
2. Log in as admin
3. Go to `/admin/`
4. Click "Create Article"
5. Fill in:
   - **Title**: Test Article
   - **Slug**: test-article
   - **Summary**: This is a test article summary
   - **Content**: Any content you want
   - **Published**: ✓ (checked)
6. Click "Submit"
7. Check subscriber email inbox

**What to verify**:
- ✅ Email arrives with article details
- ✅ Article title displays correctly
- ✅ Article summary shows
- ✅ "Read Full Article →" button works
- ✅ Takes you to the correct article page
- ✅ "Browse All Articles" button works
- ✅ Footer links functional
- ✅ Unsubscribe link works
- ✅ Mobile responsive design

---

## Testing Button Functionality in Emails

### Welcome Email Buttons

Test each button by clicking:

1. **"Browse All Articles"** 
   - Should go to: `http://yourdomain.com/articles/`
   - Shows all published articles

2. **"Visit Homepage"**
   - Should go to: `http://yourdomain.com/`
   - Shows the main landing page

3. **"Unsubscribe here"**
   - Should go to: `http://yourdomain.com/newsletter/unsubscribe?email=...`
   - Unsubscribes the email from future notifications

### Article Notification Buttons

1. **"Read Full Article →"**
   - Should go to the specific article page
   - Example: `http://yourdomain.com/article/test-article`

2. **"Browse All Articles"**
   - Same as welcome email
   - Goes to articles list page

3. **Footer links** (Website, Articles, About)
   - All should be clickable
   - Navigate to respective pages

4. **"Unsubscribe here"**
   - Same functionality as welcome email

---

## Checking Email Appearance

### Gmail
- Check regular inbox view
- Check mobile Gmail app
- Verify images load
- Verify buttons are styled correctly

### Outlook
- Desktop Outlook (if available)
- Outlook.com web interface
- Check MSO-specific styles render

### Mobile Devices
- iPhone Mail app
- Android Gmail app
- Check responsive breakpoints work
- Verify buttons stack vertically

---

## Common Issues & Solutions

### Profile Picture Not Showing

**Problem**: Uploaded picture doesn't display

**Solutions**:
- Check file was actually uploaded to `app/static/uploads/profiles/`
- Verify file has correct permissions
- Check browser console for 404 errors
- Try hard refresh (Ctrl+F5)

### Email Buttons Not Working

**Problem**: Clicking buttons does nothing

**Solutions**:
- Check email client (some block external links)
- Verify Flask app is generating correct URLs
- Check `_external=True` is set in `url_for()`
- Test with different email client

### Email Styling Broken

**Problem**: Email looks plain or unstyled

**Solutions**:
- Some email clients strip CSS
- Gmail clips large emails (check if truncated)
- Try viewing in different client
- Check HTML source to verify styles are inline

### Database Errors

**Problem**: "No such column" errors

**Solutions**:
```bash
# Re-run migration
python -m alembic upgrade head

# Or start fresh (WARNING: deletes all data)
rm instance/blog.db
python -m alembic upgrade head
python run.py  # Will recreate with seed data
```

---

## Advanced Testing

### Load Testing Profile Uploads

```python
# Test multiple file types
test_files = ['test.png', 'test.jpg', 'test.jpeg', 'test.gif']

# Test invalid extensions (should be rejected)
invalid_files = ['test.txt', 'test.exe', 'test.php']

# Test large files (adjust Flask config for limits)
# MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

### Email HTML Validation

1. Send test email to yourself
2. View raw email source
3. Copy HTML content
4. Validate at: https://www.htmlemailcheck.com/
5. Test rendering at: https://litmus.com/

### Responsive Design Testing

Use browser dev tools:
1. Open email in browser (save as .html)
2. Press F12 (Developer Tools)
3. Click mobile device icon
4. Test various screen sizes:
   - 320px (iPhone SE)
   - 375px (iPhone 12)
   - 414px (iPhone 12 Pro Max)
   - 768px (iPad)

---

## Success Criteria

✅ **Profile System**:
- Can view own profile
- Can edit all profile fields
- Can upload profile picture
- Can view other users' profiles
- Navigation shows profile link when logged in

✅ **Email Templates**:
- Welcome email delivers within 1 minute
- Article notification delivers within 1 minute
- All buttons are clickable
- All buttons navigate to correct pages
- Emails look professional
- Mobile layout works correctly
- Unsubscribe works

✅ **Overall**:
- No Python errors in console
- No browser console errors
- Smooth user experience
- Fast page loads
- Secure file uploads

---

## Need Help?

If you encounter issues:

1. Check Flask console for error messages
2. Check browser console (F12) for JavaScript errors
3. Review [UPDATES.md](UPDATES.md) for implementation details
4. Verify all migrations are applied: `python -m alembic current`
5. Check file permissions on upload directory

Happy testing! 🚀
