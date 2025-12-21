# Site Customization Guide

## Overview

The Site Customization system allows administrators to fully customize the appearance, content, and behavior of the website through a comprehensive admin panel with built-in code editors.

## Features

### 1. Site Identity
- **Site Name**: The name displayed in the browser title and header
- **Site Tagline**: A short descriptive tagline
- **Site Description**: Detailed description for SEO and about pages

### 2. Page Content Editing
Customize the content of key pages using CodeMirror HTML editors:
- **Welcome Page**: The home page content (HTML)
- **About Page**: The about page content (HTML)
- **Footer**: Custom footer content (HTML)

### 3. Custom Styling
- **Custom CSS**: Site-wide CSS injected into all pages
- **Custom JavaScript**: Site-wide JS injected into all pages

### 4. SEO & Meta Tags
- **Meta Keywords**: Comma-separated keywords for search engines
- **Meta Description**: Page description for search results
- **Social Media Links**:
  - Twitter handle
  - GitHub URL
  - Contact email

### 5. Feature Toggles
Enable or disable site features:
- **Comments**: Allow users to comment on articles
- **Likes**: Allow users to like articles
- **Newsletter**: Display newsletter subscription form
- **Social Sharing**: Show social media share buttons

### 6. Appearance
- **Primary Color**: Main theme color (with color picker)
- **Secondary Color**: Accent color (with color picker)
- **Logo**: Upload site logo (PNG, JPG, GIF, SVG)
- **Favicon**: Upload favicon (ICO, PNG)

## Access

### Requirements
- Must be logged in as an administrator
- Navigate to Admin Dashboard → **⚙️ Customize Site** button

### URL
```
http://your-domain.com/admin/customize-site
```

## Using the Code Editors

### CodeMirror Features
The customization panel uses CodeMirror editors with:
- **Syntax highlighting** for HTML, CSS, and JavaScript
- **Line numbers** for easy reference
- **Dracula theme** for comfortable editing
- **Auto-closing brackets** and tags
- **Code folding** for large blocks

### HTML Editors
Used for:
- Welcome page content
- About page content
- Footer content

**Tips:**
- Use semantic HTML5 tags (`<section>`, `<article>`, `<header>`)
- Maintain Bootstrap class compatibility
- Test with responsive layouts
- Use relative URLs for internal links

### CSS Editor
Add custom styles that apply site-wide.

**Example:**
```css
/* Custom button style */
.custom-button {
    background: linear-gradient(135deg, var(--purple), var(--cyan));
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.custom-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

/* Custom article card */
.article-card {
    border-left: 4px solid var(--purple);
}
```

### JavaScript Editor
Add custom functionality site-wide.

**Example:**
```javascript
// Track article views
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.article-content')) {
        console.log('Article viewed');
        // Add your tracking code here
    }
});

// Custom navigation behavior
const navLinks = document.querySelectorAll('.nav-link');
navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        console.log('Navigation clicked:', this.textContent);
    });
});
```

## File Uploads

### Logo
- **Supported formats**: PNG, JPG, GIF, SVG
- **Recommended size**: 200x60px (or aspect ratio)
- **Location**: Displayed in site header/navigation
- **Storage**: `app/static/uploads/site/logo_[timestamp].[ext]`

### Favicon
- **Supported formats**: ICO, PNG
- **Recommended size**: 32x32px or 16x16px
- **Location**: Browser tab icon
- **Storage**: `app/static/uploads/site/favicon_[timestamp].[ext]`

**Note**: Old files are automatically deleted when uploading new ones.

## Database Schema

### SiteSettings Model
```python
class SiteSettings(db.Model):
    id                      Integer (Primary Key)
    site_name               String(100)
    site_tagline            String(200)
    site_description        Text
    welcome_page_content    Text (HTML)
    about_page_content      Text (HTML)
    footer_content          Text (HTML)
    custom_css              Text
    custom_js               Text
    meta_keywords           String(500)
    meta_description        String(500)
    site_twitter            String(100)
    site_github             String(200)
    site_email              String(100)
    primary_color           String(7) [#RRGGBB]
    secondary_color         String(7) [#RRGGBB]
    logo_path               String(255)
    favicon_path            String(255)
    enable_comments         Boolean
    enable_likes            Boolean
    enable_newsletter       Boolean
    enable_social_sharing   Boolean
    created_at              DateTime
    updated_at              DateTime
```

### Migration
```bash
# Migration already applied: ae7eec2f994b_add_site_settings_table.py
alembic upgrade head
```

## Template Integration

### Accessing Settings in Templates
Settings are automatically available in all templates via context processor:

```jinja
{% set site_settings = get_site_settings() %}

<title>{{ site_settings.site_name }} - My Page</title>

<meta name="description" content="{{ site_settings.meta_description }}">
<meta name="keywords" content="{{ site_settings.meta_keywords }}">

{% if site_settings.enable_comments %}
    <!-- Comment section -->
{% endif %}
```

### Pre-integrated Templates
The following templates automatically use site settings:
- `components/_head.jinja` - Site name, meta tags, custom CSS/JS, favicon
- `components/_footer.jinja` - Custom footer content, newsletter toggle
- `public/welcome_page.jinja` - Custom welcome content
- `public/about_page.jinja` - Custom about content
- `public/article.jinja` - Feature toggles (comments, likes, sharing)

## Security Considerations

### Custom Code Injection
⚠️ **Warning**: Custom CSS and JavaScript are injected into all pages without sanitization.

**Best Practices:**
1. Only allow trusted administrators access
2. Test all custom code thoroughly before saving
3. Avoid inline event handlers (`onclick`, etc.)
4. Use CSP-compatible code
5. Validate external resource URLs

### File Uploads
- Files are saved with secure filenames (timestamp-based)
- Only specified extensions are allowed
- Old files are automatically cleaned up
- Files are served from `static/uploads/site/` directory

### XSS Protection
- HTML content is rendered with `| safe` filter
- Ensure admins don't inject malicious content
- Consider implementing CSP headers
- Regular security audits recommended

## Troubleshooting

### Changes Not Appearing
1. **Clear browser cache**: Press Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
2. **Check console**: Look for JavaScript errors in browser DevTools
3. **Verify save**: Check database for updated values
4. **Restart app**: Sometimes Flask caching needs refresh

### Code Editor Not Working
1. **Check browser console**: Look for CodeMirror errors
2. **Verify libraries loaded**: Check Network tab in DevTools
3. **Disable extensions**: Some browser extensions block editors
4. **Try different browser**: Test in Chrome/Firefox/Edge

### File Upload Failures
1. **Check file size**: Ensure within Flask's max upload size
2. **Check permissions**: Verify `app/static/uploads/site/` is writable
3. **Check file format**: Only supported extensions work
4. **Check disk space**: Ensure sufficient storage available

### Feature Toggles Not Working
1. **Verify template**: Check if template uses conditional blocks
2. **Clear cache**: Browser and server-side caches
3. **Check database**: Verify boolean values saved correctly
4. **Restart server**: Reload to pick up changes

## Advanced Usage

### Custom Variables in CSS
Use CSS custom properties for consistency:

```css
:root {
    --primary: {{ site_settings.primary_color }};
    --secondary: {{ site_settings.secondary_color }};
}

.button {
    background: var(--primary);
}
```

### JavaScript API Integration
Add analytics or third-party services:

```javascript
// Google Analytics
(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-XXXXX-Y', 'auto');
ga('send', 'pageview');
```

### Dynamic Content Loading
Use AJAX to load content:

```javascript
// Load latest articles dynamically
fetch('/api/articles/latest')
    .then(response => response.json())
    .then(data => {
        const container = document.getElementById('latest-articles');
        data.forEach(article => {
            const div = document.createElement('div');
            div.innerHTML = `<h3>${article.title}</h3>`;
            container.appendChild(div);
        });
    });
```

## Best Practices

### Content Management
1. **Backup before changes**: Export content before major edits
2. **Test in staging**: Use development environment first
3. **Version control**: Keep track of HTML/CSS/JS changes
4. **Documentation**: Comment complex code sections
5. **Responsive design**: Test on mobile devices

### Performance
1. **Minify CSS/JS**: Use online tools to compress code
2. **Optimize images**: Compress logo/favicon files
3. **Lazy load**: Use lazy loading for images in custom HTML
4. **Cache headers**: Set appropriate cache durations
5. **CDN**: Consider using CDN for large assets

### SEO
1. **Unique meta descriptions**: Write compelling descriptions
2. **Relevant keywords**: Choose 5-10 targeted keywords
3. **Semantic HTML**: Use proper heading hierarchy
4. **Alt text**: Add alt attributes to all images
5. **Schema markup**: Consider adding structured data

## Examples

### Welcome Page Template
```html
<div class="hero-section text-center py-5">
    <h1 class="display-3 fw-bold mb-4">Welcome to Our Blog</h1>
    <p class="lead mb-5">Discover insightful articles and stories</p>
    <a href="/articles" class="btn btn-primary btn-lg">Explore Articles</a>
</div>

<div class="features-section py-5">
    <div class="row">
        <div class="col-md-4 text-center">
            <i class="bi bi-pen fs-1 text-primary"></i>
            <h3 class="mt-3">Quality Content</h3>
            <p>Well-researched and engaging articles</p>
        </div>
        <div class="col-md-4 text-center">
            <i class="bi bi-people fs-1 text-primary"></i>
            <h3 class="mt-3">Community</h3>
            <p>Join our growing community of readers</p>
        </div>
        <div class="col-md-4 text-center">
            <i class="bi bi-lightning fs-1 text-primary"></i>
            <h3 class="mt-3">Regular Updates</h3>
            <p>New articles published weekly</p>
        </div>
    </div>
</div>
```

### Custom Theme CSS
```css
/* Dark mode toggle */
body.dark-mode {
    background-color: #1a1a1a;
    color: #e0e0e0;
}

body.dark-mode .card {
    background-color: #2a2a2a;
    border-color: #3a3a3a;
}

/* Animated gradient header */
.header {
    background: linear-gradient(
        -45deg,
        var(--purple),
        var(--cyan),
        var(--purple-light),
        var(--cyan-light)
    );
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: var(--primary);
    border-radius: 6px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--secondary);
}
```

## Support

For issues or questions:
1. Check console for error messages
2. Review this documentation
3. Check [SECURITY.md](SECURITY.md) for security concerns
4. Open an issue on GitHub

## Future Enhancements

Planned features:
- [ ] Theme presets (Light, Dark, High Contrast)
- [ ] Custom page builder with drag-and-drop
- [ ] Revision history for content changes
- [ ] A/B testing for content variations
- [ ] Custom email templates
- [ ] Widget system for sidebar content
- [ ] Multi-language support

---

**Last Updated**: January 2025  
**Version**: 1.0.0
