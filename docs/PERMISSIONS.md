# User Permission System

This application implements a 4-tier user permission system with clearly defined capabilities for each user type.

---

## 🎭 User Types & Permissions

### 1. 👑 **Admin** (Super User)
**Database:** `is_admin = 1`

**Full System Access:**
- ✅ View all articles (published & unpublished)
- ✅ Create, edit, and delete ANY article
- ✅ Like, comment, and share articles
- ✅ Manage all users (view, delete, grant/revoke permissions)
- ✅ Manage newsletter subscribers
- ✅ Access admin dashboard (`/admin`)
- ✅ Customize their profile page (colors, fonts)
- ✅ Grant/revoke article writing permissions
- ✅ Grant/revoke admin privileges

**Navigation:**
- "Admin" button visible in header
- Full admin dashboard access

---

### 2. ✍️ **Writer** (Article Creator)
**Database:** `can_write_articles = 1` (is_admin = 0)

**Content Creation & Engagement:**
- ✅ View all published articles
- ✅ Create new articles
- ✅ Edit ONLY their own articles
- ✅ Delete ONLY their own articles
- ✅ Like, comment, and share articles
- ✅ Customize their profile page (colors, fonts)
- ✅ Access article management dashboard (`/admin`)
- ✅ Full profile management

**Restrictions:**
- ❌ Cannot edit/delete other users' articles
- ❌ Cannot manage users
- ❌ Cannot manage newsletter subscribers
- ❌ Cannot grant permissions to others

**Navigation:**
- "My Articles" button visible in header (cyan colored)
- Article dashboard shows only their articles (admins see all)

**How to Grant:**
Admin goes to `/admin/users` → Click pencil icon next to user

---

### 3. 👤 **Regular User** (Registered Account)
**Database:** `can_write_articles = 0`, `is_admin = 0`

**Engagement Only:**
- ✅ View all published articles
- ✅ Like articles
- ✅ Comment on articles (with emojis! 😊)
- ✅ Share articles (social media, copy link)
- ✅ Full profile management (bio, avatar, social links)
- ✅ Change password

**Restrictions:**
- ❌ Cannot create articles
- ❌ Cannot customize page appearance
- ❌ Cannot access admin/article dashboard
- ❌ Cannot manage users or settings

**Navigation:**
- "Profile" button visible
- NO admin/article management button

**How to Create:**
Click "Create New Account" on login page → Register

---

### 4. 👁️ **Guest** (Not Logged In)
**Database:** No account

**View-Only Access:**
- ✅ View all published articles
- ✅ Share articles (social media, copy link)
- ✅ Browse article list
- ✅ Read article content

**Restrictions:**
- ❌ Cannot like articles
- ❌ Cannot comment on articles
- ❌ Cannot create account features (profile, etc.)
- ❌ No access to any management features

**Navigation:**
- "Login" button visible
- Prompted to login when attempting to like/comment

---

## 📊 Permission Matrix

| Feature | Guest | Regular User | Writer | Admin |
|---------|:-----:|:------------:|:------:|:-----:|
| View published articles | ✅ | ✅ | ✅ | ✅ |
| Share articles | ✅ | ✅ | ✅ | ✅ |
| Like articles | ❌ | ✅ | ✅ | ✅ |
| Comment on articles | ❌ | ✅ | ✅ | ✅ |
| Create articles | ❌ | ❌ | ✅ | ✅ |
| Edit own articles | ❌ | ❌ | ✅ | ✅ |
| Edit any article | ❌ | ❌ | ❌ | ✅ |
| Delete own articles | ❌ | ❌ | ✅ | ✅ |
| Delete any article | ❌ | ❌ | ❌ | ✅ |
| Customize page | ❌ | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ❌ | ✅ |
| Grant permissions | ❌ | ❌ | ❌ | ✅ |
| Profile management | ❌ | ✅ | ✅ | ✅ |

---

## 🔐 Implementation Details

### Session Variables
When a user logs in, the following session variables are set:
```python
session['logged_in'] = True
session['user_id'] = user.id
session['username'] = user.username
session['is_admin'] = bool(user.is_admin)
session['can_write_articles'] = bool(user.can_write_articles)
```

### Database Fields (User Model)
```python
is_admin = db.Column(db.Integer, nullable=False, default=0)
can_write_articles = db.Column(db.Integer, nullable=False, default=0)
```

### Permission Checks in Code

**Admin-only routes:**
```python
def require_login():
    """Check if user is logged in and is admin."""
    if not user.is_admin:
        abort(403)
```

**Writer or Admin routes:**
```python
def require_writer_or_admin():
    """Check if user can write articles (writer or admin)."""
    if not user.can_write_articles and not user.is_admin:
        abort(403)
```

**Article ownership check (writers):**
```python
# Writers can only edit their own articles
if not user.is_admin and article.author_id != user_id:
    flash('You can only edit your own articles.', 'error')
    abort(403)
```

### Template Permission Checks

**Navigation (show/hide buttons):**
```jinja2
{% if session.get('is_admin') or session.get('can_write_articles') %}
  <a href="{{ url_for('admin.dashboard') }}">
    {% if session.get('is_admin') %}Admin{% else %}My Articles{% endif %}
  </a>
{% endif %}
```

**Comment/Like forms:**
```jinja2
{% if session.logged_in %}
  <!-- Show comment form and like button -->
{% else %}
  <!-- Show login prompt -->
{% endif %}
```

**Customization button:**
```jinja2
{% if can_customize %}  <!-- user.can_write_articles or user.is_admin -->
  <a href="{{ url_for('profile.customize_page') }}">🎨 Customize Page</a>
{% endif %}
```

---

## 🚀 Upgrading Users

### Regular User → Writer
1. Admin logs in
2. Navigate to `/admin/users`
3. Find the user
4. Click green pencil icon (Grant Writer)
5. User badge changes to show "Writer" in green
6. User can now create articles and customize their page

### Writer → Admin
1. Admin logs in
2. Navigate to `/admin/users`
3. Find the user
4. Click yellow shield icon (Grant Admin)
5. User badge changes to show "Admin" in red
6. User gets full system access

### Downgrade Permissions
Same process - click the icon again to revoke:
- Shield icon toggles admin status
- Pencil icon toggles writer status

---

## 🎨 Customization Access

Only **Writers** and **Admins** can customize their profile pages.

**Customizable Settings:**
- Background color
- Text color
- Accent color (links, borders)
- Font size
- Font family

**Access:**
- Profile page shows "🎨 Customize Page" button
- Route: `/profile/customize`
- Live preview of changes
- Applies to profile page automatically

**Regular Users:**
- See message: "You do not have permission to customize your page. Contact an admin for article writing access."

---

## 📋 User Management (Admin Only)

**Location:** `/admin/users`

**Features:**
- View all users with stats (articles, comments, likes)
- See permission badges (Admin, Writer)
- View detailed activity per user
- Toggle admin privileges
- Toggle writer permissions
- Delete users (cannot delete self)

**Badges:**
- 🔴 **Admin** - Red badge (is_admin=1)
- 🟢 **Writer** - Green badge (can_write_articles=1)
- ⚪ **User** - Gray badge (no special permissions)

---

## ⚠️ Security Notes

1. **Password Changes:** New admins must change password on first login
2. **Session Management:** Permissions loaded from database on each login
3. **Route Protection:** All sensitive routes check permissions server-side
4. **Ownership Validation:** Writers can only modify their own content
5. **CSRF Protection:** All forms use CSRF tokens
6. **SQL Injection:** Using SQLAlchemy ORM for safe queries

---

## 🔄 Permission Flow Examples

### Example 1: New User Journey
1. Guest visits site → Can view and share articles
2. Clicks "Create New Account" → Becomes Regular User
3. Can now like and comment on articles
4. Admin grants Writer permission
5. Can now create articles and customize page
6. Admin grants Admin permission (if needed)
7. Can now manage entire system

### Example 2: Comment Attempt
```
Guest → Tries to comment
  ↓
System → Redirects to login with "You must be logged in to comment"
  ↓
User logs in → Returns to article
  ↓
User posts comment successfully ✅
```

### Example 3: Article Creation Attempt
```
Regular User → Navigates to /admin/new
  ↓
System → Checks can_write_articles = 0
  ↓
System → Returns 403 Forbidden + "You do not have permission to create articles"
  ↓
User contacts admin → Admin grants Writer permission
  ↓
User navigates to /admin/new → Access granted ✅
```

---

## 📞 Support

**Default Admin Credentials** (if using seed data):
- Username: `admin`
- Password: `admin`

**Granting Permissions:**
- Contact your site administrator
- Email: [configured in .env]

**Technical Issues:**
- Check logs in `/logs` directory
- Review error messages in application
- Verify database migrations are up to date: `alembic current`

---

*Last updated: December 21, 2025*
