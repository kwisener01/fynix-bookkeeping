# Fynix Bookkeeping - Complete MVP Deployment Guide

## 🎯 Goal
Deploy a fully functional MVP that customers can use to upload receipts, see intelligent categorization, and get job matching suggestions.

## 📋 Prerequisites

- [ ] GitHub account
- [ ] Credit card (for services, most have free tiers)
- [ ] Domain name (optional but recommended)

## 🚀 Deployment Steps

---

## PHASE 1: Set Up Supabase (Database + Auth + Storage)

### 1.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Create a new organization (your business name)
4. Create a new project:
   - **Name**: fynix-bookkeeping
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to your target customers
   - **Plan**: Free tier is fine to start

### 1.2 Run Database Schema

1. Wait for project to finish setting up (~2 minutes)
2. Go to **SQL Editor** in left sidebar
3. Click "+ New query"
4. Copy contents of `database/schema.sql`
5. Paste into query editor
6. Click **Run** button
7. Verify: Go to "Table Editor" - you should see all tables

### 1.3 Set Up Storage

1. Go to **Storage** in left sidebar
2. Click "+ New bucket"
3. Name: `receipts`
4. Public bucket: **Yes** (for image viewing)
5. Click "Create bucket"

6. Set storage policies:
   - Click on `receipts` bucket
   - Go to "Policies" tab
   - Add policy:
     ```sql
     CREATE POLICY "Users can upload their own receipts"
     ON storage.objects FOR INSERT
     TO authenticated
     WITH CHECK (bucket_id = 'receipts' AND auth.uid()::text = (storage.foldername(name))[1]);

     CREATE POLICY "Users can view their own receipts"
     ON storage.objects FOR SELECT
     TO authenticated
     USING (bucket_id = 'receipts' AND auth.uid()::text = (storage.foldername(name))[1]);
     ```

### 1.4 Get API Keys

1. Go to **Settings** → **API**
2. Save these values (you'll need them later):
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (keep secret!)

3. Go to **Settings** → **Database**
4. Save **Connection string** (URI format)

---

## PHASE 2: Deploy Backend API to Railway

### 2.1 Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "+ New Project"
4. Choose "Deploy from GitHub repo"

### 2.2 Connect GitHub Repository

1. If you haven't yet, push your code to GitHub:
   ```bash
   cd C:\Projects\contractor_bookkeeping\fynix_bookkeeping
   git init
   git add .
   git commit -m "Initial commit - Fynix MVP"
   gh repo create fynix-bookkeeping --private --source=. --push
   ```

2. In Railway, authorize GitHub access
3. Select your `fynix-bookkeeping` repository
4. Railway will detect it's a Python app

### 2.3 Configure Environment Variables

1. In Railway project settings, go to **Variables** tab
2. Add all variables from `.env.example.production`:

   ```
   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-key
   DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://yourdomain.com
   ```

3. Click "Deploy"

### 2.4 Get Your API URL

1. Once deployed, go to **Settings** → **Domains**
2. Railway generates: `https://fynix-bookkeeping-production.up.railway.app`
3. (Optional) Add custom domain:
   - Click "+ Generate Domain"
   - Or add your own: `api.fynixbooks.com`

### 2.5 Test Your API

```bash
curl https://your-api.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-28T23:00:00Z"
}
```

---

## PHASE 3: Deploy Frontend to Vercel

### 3.1 Set Up Frontend Project

```bash
cd C:\Projects\contractor_bookkeeping
npx create-next-app@latest fynix-frontend --typescript --tailwind --app
cd fynix-frontend
```

### 3.2 Copy Frontend Files

1. Copy all files from `frontend/` folder to `fynix-frontend/`
2. Install dependencies:
   ```bash
   npm install
   ```

### 3.3 Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "+ New Project"
4. Import `fynix-frontend` repository

### 3.4 Configure Environment Variables

In Vercel deployment settings, add:

```
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

### 3.5 Deploy

1. Click "Deploy"
2. Wait ~2 minutes
3. Your site is live at: `https://fynix-frontend.vercel.app`

### 3.6 Add Custom Domain (Optional)

1. In Vercel project → **Settings** → **Domains**
2. Add `fynixbooks.com` and `www.fynixbooks.com`
3. Update DNS records at your domain registrar:
   ```
   A record: @ → 76.76.21.21
   CNAME: www → cname.vercel-dns.com
   ```

---

## PHASE 4: Final Configuration

### 4.1 Update CORS

In Railway, add frontend URL to `ALLOWED_ORIGINS`:
```
ALLOWED_ORIGINS=https://fynixbooks.com,https://www.fynixbooks.com
```

### 4.2 Test End-to-End

1. Visit your frontend: `https://fynixbooks.com`
2. Sign up for an account
3. Upload a test receipt
4. Verify it processes correctly

---

## 🧪 Testing Checklist

- [ ] Health check endpoint works
- [ ] User signup/login works
- [ ] Receipt upload processes successfully
- [ ] Receipt appears in dashboard
- [ ] Job matching suggestions appear (if jobs exist)
- [ ] Categorization shows correct categories

---

## 💰 Expected Costs

### Free Tier (First ~100 users):
- **Supabase**: Free (500MB database, 1GB storage)
- **Railway**: $5/month (500 hours free)
- **Vercel**: Free (100GB bandwidth)
- **Anthropic**: Pay per use (~$50-100/month with 100 users)
- **Domain**: $12/year
- **Total**: ~$60-110/month

### Paid Tier (500+ users):
- **Supabase Pro**: $25/month
- **Railway**: $20/month
- **Vercel Pro**: $20/month
- **Anthropic**: ~$200-500/month
- **Total**: ~$265-565/month

---

## 🎉 You're Live!

Your MVP is now deployed and ready for customers!

**Next Steps**:
1. Share with 3-5 beta testers
2. Collect feedback
3. Iterate on features
4. Set up Stripe for payments
5. Add email notifications
6. Improve mobile experience

---

## 📞 Support

- **Supabase Issues**: Check [supabase.com/docs](https://supabase.com/docs)
- **Railway Issues**: Check [docs.railway.app](https://docs.railway.app)
- **Vercel Issues**: Check [vercel.com/docs](https://vercel.com/docs)

---

## 🔐 Security Checklist

Before going live with real customers:

- [ ] Environment variables are set correctly
- [ ] Database RLS policies are enabled
- [ ] API rate limiting is configured
- [ ] HTTPS is enforced everywhere
- [ ] API keys are never exposed to frontend
- [ ] User data is encrypted at rest
- [ ] Backup strategy is in place

---

## 🚨 Troubleshooting

### "Failed to upload receipt"
- Check Railway logs: `railway logs`
- Verify ANTHROPIC_API_KEY is set
- Check CORS settings

### "Authentication failed"
- Verify Supabase URL and keys
- Check browser console for errors
- Try clearing cookies/cache

### Database connection errors
- Verify DATABASE_URL is correct
- Check Supabase is not paused (free tier pauses after 7 days inactivity)
- Run database migrations

---

## 📊 Monitoring

Set up monitoring:
1. **Railway**: Built-in metrics
2. **Vercel**: Analytics tab
3. **Supabase**: Database usage tab

Set up alerts for:
- API errors
- Slow database queries
- High costs
- Failed authentications

---

## 🎯 Launch Checklist

- [ ] All tests passing
- [ ] Error handling works
- [ ] Mobile responsive
- [ ] Loading states implemented
- [ ] 3-5 beta users onboarded
- [ ] Feedback collected
- [ ] Critical bugs fixed
- [ ] Pricing page ready
- [ ] Terms of service added
- [ ] Privacy policy added

**You're ready to launch!** 🚀
