# Issue #9: Apply Tailwind CSS globally via base layout

This task list tracks the work needed to centralize Tailwind CSS (and Alpine.js) includes in a shared base template
and refactor existing pages to extend it.

**GitHub Issue:** https://github.com/drgittest/test01/issues/9

## Tasks

1. [x] **Create `base.html`**:
   - [x] Add `templates/base.html` containing:
     - [x] HTML `<head>` with Tailwind CDN (or link to built CSS)
     - [x] Alpine.js include
     - [x] Meta viewport and charset tags
     - [x] Global navigation bar and layout wrappers
     - [x] `{% block title %}` and `{% block content %}` placeholders

2. [x] **Refactor page templates**:
   - [x] Update `index.html`, `register.html`, `login.html`, `orders.html`,
     `order_create.html`, `order_edit.html`, `order_detail.html` to:
     - [x] Use `{% extends "base.html" %}`
     - [x] Populate `block title` and `block content`
     - [x] Remove individual `<head>`, Tailwind/Alpine `<script>` tags, and redundant nav markup

3. [x] **(Optional) Local Tailwind build setup**:
   - [x] Install Tailwind, PostCSS, autoprefixer via npm
   - [x] Create `tailwind.config.js` with proper `content` paths
   - [x] Add `assets/tailwind.css` with `@tailwind` directives
   - [x] Add npm `build:css` script to generate `static/css/tailwind.css`

4. [x] **Serve static assets**:
   - [x] Mount `/static` in `main.py` via `app.mount()` and `StaticFiles`
   - [x] Ensure `static/css/tailwind.css` is generated and accessible

5. [x] **Update `base.html` for production CSS**:
   - [x] Reference `/static/css/tailwind.css` instead of CDN when using the local build

6. [x] **Verify styling & run tests**:
   - [x] Confirm all pages render Tailwind styles correctly
   - [x] Run existing unit, integration, and visual tests to catch regressions
   - [x] Commit changes, push branch, and update Issue #9 with status
