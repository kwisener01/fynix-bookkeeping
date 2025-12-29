# Deployment Guide: Railway + Vercel

Follow these steps to deploy your Fynix PWA to production.

---

## Prerequisites Checklist

Before you begin, make sure you have:

- [ ] GitHub account and repository
- [ ] Railway account (sign up at https://railway.app)
- [ ] Vercel account (sign up at https://vercel.com)
- [ ] Anthropic API key (for Claude Vision)
- [ ] Supabase account with project created (optional, for production data storage)

---

## Step 1: Prepare Git Repository

### 1.1 Check Git Status

```bash
cd C:\Projects\contractor_bookkeeping\fynix_bookkeeping

# Check if this is a git repo
git status
```

### 1.2 Initialize Git (if needed)

If not a git repo yet:
```bash
git init
git add .
git commit -m "Initial commit: PWA mobile receipt capture with offline support"
```

### 1.3 Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., `fynix-bookkeeping`)
3. **Don't** initialize with README (we already have code)

### 1.4 Push to GitHub

```bash
# Add your GitHub repo as remote
git remote add origin https://github.com/YOUR_USERNAME/fynix-bookkeeping.git

# Push code
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy Backend to Railway

### 2.1 Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize GitHub if prompted
5. Select your `fynix-bookkeeping` repository
6. Railway will auto-detect Python and use the `Procfile`

### 2.2 Configure Environment Variables

In Railway dashboard:

1. Click on your service
2. Go to "Variables" tab
3. Add these variables:

```
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
ENVIRONMENT=production
PORT=8000
```

**Optional (if using Supabase):**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
```

### 2.3 Deploy

Railway will automatically deploy after you add variables.

### 2.4 Get Your Railway URL

1. In Railway dashboard, look for the generated URL
2. It will be something like: `https://fynix-bookkeeping-production.up.railway.app`
3. **Copy this URL** - you'll need it for the frontend

### 2.5 Test Backend

Open in browser:
```
https://your-railway-url.railway.app/health
```

Should see:
```json
{
  "status": "healthy",
  "agents": { ... }
}
```

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Install Vercel CLI

```bash
npm install -g vercel
```

### 3.2 Login to Vercel

```bash
vercel login
```

Follow the prompts to authenticate.

### 3.3 Deploy Frontend

```bash
cd frontend
vercel
```

**Answer the prompts:**
- Setup and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name? `fynix-receipt-capture` (or your choice)
- In which directory is your code? **./` (current directory)
- Want to override settings? **N**

Vercel will build and deploy.

### 3.4 Get Your Vercel URLs

After deployment, you'll see:
- **Preview URL**: `https://fynix-receipt-capture-xxx.vercel.app`
- **Production URL**: Will be shown when you run `vercel --prod`

---

## Step 4: Configure Frontend Environment Variables

### 4.1 Add Environment Variables in Vercel

1. Go to https://vercel.com/dashboard
2. Select your project (`fynix-receipt-capture`)
3. Go to "Settings" → "Environment Variables"
4. Add these variables:

```
Name: NEXT_PUBLIC_API_URL
Value: https://your-railway-url.railway.app

Name: NEXT_PUBLIC_SUPABASE_URL
Value: https://your-project.supabase.co

Name: NEXT_PUBLIC_SUPABASE_ANON_KEY
Value: your-supabase-anon-key

Name: NEXT_PUBLIC_DEMO_MODE
Value: true
```

**Important:** Set these for **All** environments (Production, Preview, Development)

### 4.2 Redeploy to Apply Variables

```bash
vercel --prod
```

This creates a production deployment with environment variables applied.

---

## Step 5: Update CORS on Backend

Your Railway backend needs to allow requests from your Vercel URL.

### 5.1 Update server.py CORS settings

Edit `api/server.py` line 47-49:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fynix-receipt-capture.vercel.app",
        "https://fynix-receipt-capture-*.vercel.app",  # Preview deployments
        "http://localhost:3000"  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Replace `fynix-receipt-capture` with your actual Vercel project name.

### 5.2 Push Changes

```bash
git add api/server.py
git commit -m "Update CORS for production"
git push
```

Railway will automatically redeploy.

---

## Step 6: Test Production Deployment

### 6.1 Desktop Testing

1. Open your Vercel URL: `https://fynix-receipt-capture.vercel.app`
2. Click "Try Demo - No Login Required"
3. Test file upload (drag & drop a receipt)
4. Verify OCR extraction works
5. Check job matching suggestions appear

### 6.2 Mobile Testing

**On your phone:**

1. Open Safari (iOS) or Chrome (Android)
2. Navigate to your Vercel URL
3. Test camera capture
4. Install PWA to home screen:
   - **iOS**: Tap Share → "Add to Home Screen"
   - **Android**: Tap menu → "Install app" or "Add to Home Screen"

### 6.3 PWA Testing

After installing:

1. Launch app from home screen
2. Verify it opens in standalone mode (no browser chrome)
3. Test camera capture
4. Test offline mode:
   - Enable airplane mode
   - Capture a receipt
   - Check it queues (should see "1 receipt queued")
   - Disable airplane mode
   - Verify auto-sync uploads the receipt

---

## Step 7: Verify Everything Works

Use this checklist:

- [ ] Backend health check responds at `/health`
- [ ] Frontend landing page loads
- [ ] Demo session creates successfully
- [ ] File upload works
- [ ] Camera capture works on mobile
- [ ] OCR extraction returns data
- [ ] Job matching shows suggestions
- [ ] Result page displays correctly
- [ ] PWA installs on home screen
- [ ] Service worker registers
- [ ] Offline queuing works
- [ ] Auto-sync uploads when back online
- [ ] No CORS errors in console

---

## Troubleshooting

### CORS Errors

**Problem:** Console shows CORS policy errors

**Solution:**
1. Check Railway backend CORS settings include your Vercel URL
2. Ensure frontend `NEXT_PUBLIC_API_URL` points to Railway URL
3. Redeploy both services

### Service Worker Not Registering

**Problem:** PWA features don't work

**Solution:**
1. Vercel serves over HTTPS by default (required for SW)
2. Check browser console for SW errors
3. Clear cache and hard reload (Ctrl+Shift+R)
4. Check that `sw.js` is in `frontend/public/` folder

### Environment Variables Not Working

**Problem:** Backend can't reach Claude API or frontend can't reach backend

**Solution:**
1. Verify all env vars are set in Railway and Vercel dashboards
2. Make sure vars are set for "Production" environment
3. Redeploy after adding variables

### Camera Not Working

**Problem:** Camera button doesn't open camera

**Solution:**
1. Camera API requires HTTPS (Vercel provides this)
2. Check browser permissions
3. Try a different browser
4. Ensure device has a camera

---

## Production Checklist

Before announcing to users:

- [ ] Test on multiple devices (iOS, Android)
- [ ] Test on multiple browsers (Safari, Chrome, Firefox)
- [ ] Verify offline mode works correctly
- [ ] Check receipt OCR accuracy
- [ ] Monitor Railway logs for errors
- [ ] Set up error tracking (optional: Sentry)
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring/alerts

---

## Custom Domain (Optional)

### For Vercel:

1. Go to Vercel dashboard → Your project → Settings → Domains
2. Add your domain (e.g., `receipts.fynix.com`)
3. Follow DNS configuration instructions
4. Update Railway CORS to include custom domain

### For Railway:

1. Go to Railway dashboard → Your service → Settings
2. Click "Generate Domain" or add custom domain
3. Update frontend `NEXT_PUBLIC_API_URL` to custom domain
4. Redeploy frontend

---

## Monitoring & Maintenance

### Railway Logs

View logs in Railway dashboard to monitor:
- Receipt processing requests
- OCR extraction success/failures
- API errors

### Vercel Analytics

Enable in Vercel dashboard:
- Project → Analytics
- See deployment performance
- Track user traffic

---

## Cost Estimates

**Free Tier:**
- Railway: 500 hours/month, $5 credit
- Vercel: Unlimited deployments, 100GB bandwidth
- Supabase: 500MB database, 1GB file storage

**Estimated monthly cost:** $0-10 for low traffic demo

---

## Next Steps After Deployment

1. Share your demo URL with users
2. Gather feedback on mobile UX
3. Monitor error rates
4. Consider adding:
   - User authentication (beyond demo mode)
   - Database persistence for receipts
   - Email notifications
   - Analytics dashboard

---

## Support

If you encounter issues:

1. Check Railway logs for backend errors
2. Check Vercel deployment logs
3. Inspect browser console for frontend errors
4. Verify all environment variables are set correctly

Your PWA is ready for the world! 🚀
