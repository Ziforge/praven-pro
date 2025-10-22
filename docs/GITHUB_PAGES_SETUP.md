# GitHub Pages Setup for Praven Pro

This guide shows how to enable the Praven Pro website on GitHub Pages.

---

## What is GitHub Pages?

GitHub Pages hosts a **static website** directly from your GitHub repository. The website will be available at:

```
https://ziforge.github.io/praven-pro
```

**Note:** This hosts a **landing page** with project information, documentation, and installation instructions. The actual validation web app (Flask) needs to run locally or be deployed to a cloud service.

---

## Setup Instructions

### Step 1: Push to GitHub

Make sure your repository is on GitHub:

```bash
# If not already a git repository
git init
git add .
git commit -m "Add GitHub Pages website"

# Add remote (replace with your GitHub username)
git remote add origin https://github.com/Ziforge/praven-pro.git

# Push to GitHub
git push -u origin main
```

---

### Step 2: Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/Ziforge/praven-pro`

2. Click **Settings** (top menu)

3. Scroll down to **Pages** (left sidebar)

4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/docs`

5. Click **Save**

6. Wait 2-3 minutes for GitHub to build the site

7. Your site will be live at: `https://ziforge.github.io/praven-pro`

---

## Website Structure

```
docs/
├── index.html              # Main landing page (auto-served)
├── _config.yml             # GitHub Pages configuration
├── images/                 # Screenshots (when captured)
├── README.md               # Documentation index (not shown on site)
├── DIAGRAMS.md             # Mermaid diagrams
├── SCREENSHOTS.md          # Screenshot guide
└── ...                     # Other documentation files
```

**GitHub Pages serves:** `docs/index.html` as the main page

**GitHub serves separately:** All the .md files as documentation (accessible via GitHub, not the Pages site)

---

## What's Included on the Website

✅ **Landing Page** (`docs/index.html`)
- Project overview
- Key features
- Statistics (100% precision, 4,000+ species, etc.)
- How it works (4-step process)
- Installation instructions (PyPI, source, web interface)
- Links to GitHub repository

**Auto-Detection Features Highlighted:**
- Automatic habitat detection from GPS
- Automatic weather fetching from GPS + date
- Smart review (97% workload reduction)
- Temporal/habitat/geographic validation

---

## What's NOT on GitHub Pages

The following require Python/server-side processing and cannot run on GitHub Pages:

❌ **Flask Web App** (`web_app.py`)
- Needs Python server to run validation
- Users must run locally or deploy to cloud

❌ **Validation Processing**
- Requires Python libraries (pandas, requests, etc.)
- Cannot run in browser

**Solution:** Users download/install Praven Pro and run locally or deploy to:
- Heroku (free tier)
- Railway
- PythonAnywhere
- AWS/GCP/Azure

---

## Customization

### Update Website Content

Edit `docs/index.html` to change:
- Hero text
- Feature descriptions
- Statistics
- Installation instructions
- Color scheme

### Change Colors

The current color scheme is purple gradient (`#667eea` → `#764ba2`).

To change, edit in `docs/index.html`:

```css
/* Hero gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Button color */
color: #667eea;

/* Step numbers */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Add Screenshots

1. Capture screenshots following `docs/SCREENSHOT_INSTRUCTIONS.md`
2. Save to `docs/images/`
3. Add to `index.html`:

```html
<section class="screenshots">
    <h2>Screenshots</h2>
    <img src="images/web_interface_landing.png" alt="Web Interface">
    <img src="images/cli_auto_detection.png" alt="CLI">
</section>
```

---

## Testing Locally

Before pushing to GitHub, test the website locally:

### Option 1: Simple Python Server

```bash
cd docs
python3 -m http.server 8000
# Open: http://localhost:8000
```

### Option 2: Jekyll (if you want GitHub's exact build)

```bash
gem install bundler jekyll
cd docs
jekyll serve
# Open: http://localhost:4000/praven-pro
```

---

## Deployment Options for Web App

While the landing page can be on GitHub Pages, the actual validation web app needs a server. Options:

### Option 1: Heroku (Free Tier)

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create praven-pro

# Deploy
git push heroku main

# Open
heroku open
```

**Files needed:**
- `Procfile`: `web: gunicorn web_app:app`
- `runtime.txt`: `python-3.12`
- `requirements.txt`: Already exists

### Option 2: Railway

1. Go to railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select `praven-pro` repository
4. Railway auto-detects Python and deploys
5. Get public URL

### Option 3: PythonAnywhere

1. Sign up at pythonanywhere.com
2. Upload code
3. Configure WSGI file
4. Get public URL at `username.pythonanywhere.com`

### Option 4: Run Locally

```bash
python web_app.py
# Share with ngrok: ngrok http 5001
```

---

## Custom Domain (Optional)

To use a custom domain like `praven.com`:

1. Buy domain from registrar
2. Add CNAME record pointing to `ziforge.github.io`
3. In GitHub Pages settings, add custom domain
4. Wait for DNS propagation (24-48 hours)

---

## Troubleshooting

### Site Not Showing

- Wait 2-3 minutes after enabling
- Check branch is `main` and folder is `/docs`
- Check `index.html` exists in `/docs`
- Check GitHub Pages section shows green checkmark

### 404 Error

- Ensure branch and folder are set correctly
- Check file is named `index.html` (not `Index.html`)
- Clear browser cache

### Styling Not Working

- Check CSS is inline in `<style>` tags (external CSS needs to be in `/docs/assets/`)
- Verify no browser console errors

---

## Updating the Website

After making changes:

```bash
# Edit docs/index.html
nano docs/index.html

# Commit and push
git add docs/index.html
git commit -m "Update website content"
git push origin main

# GitHub Pages auto-rebuilds in 2-3 minutes
```

---

## Summary

✅ **GitHub Pages hosts:** Static landing page with project info, docs, screenshots
✅ **Users can:** Learn about Praven Pro, see features, download/install
✅ **Website URL:** https://ziforge.github.io/praven-pro (after setup)

❌ **GitHub Pages cannot:** Run Python validation (needs separate deployment)
❌ **For validation web app:** Users run locally or deploy to Heroku/Railway/etc.

**Best of both worlds:**
- Landing page on GitHub Pages (free, always available)
- Web app runs locally or deployed to cloud (for actual validation)

---

## Contact

Questions about GitHub Pages setup?
- Email: ghredpath@hotmail.com
- GitHub Issues: https://github.com/Ziforge/praven-pro/issues
