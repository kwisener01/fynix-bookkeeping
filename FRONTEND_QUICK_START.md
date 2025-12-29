# Frontend Quick Start Guide

## Step-by-Step Setup (5 Minutes)

### Step 1: Create Next.js App (2 min)

Open terminal/command prompt and run:

```bash
cd C:\Projects\contractor_bookkeeping
npx create-next-app@latest fynix-frontend
```

**Answer the prompts:**
- ✅ TypeScript? → **Yes**
- ✅ ESLint? → **Yes**
- ✅ Tailwind CSS? → **Yes**
- ❌ `src/` directory? → **No**
- ✅ App Router? → **Yes**
- ❌ Customize import alias? → **No**

Wait for installation to complete (~1-2 minutes)

### Step 2: Run Automated Setup (1 min)

```bash
cd fynix-frontend
```

Copy the setup script:
```bash
copy ..\fynix_bookkeeping\frontend\setup-frontend.bat .
```

Run it:
```bash
setup-frontend.bat
```

This will install all dependencies automatically.

### Step 3: Copy Frontend Files (1 min)

Run the copy script:
```bash
..\fynix_bookkeeping\frontend\copy-files.bat "%CD%"
```

Or manually copy these folders:
- `fynix_bookkeeping/frontend/types/` → `fynix-frontend/types/`
- `fynix_bookkeeping/frontend/lib/` → `fynix-frontend/lib/`
- `fynix_bookkeeping/frontend/components/` → `fynix-frontend/components/`
- `fynix_bookkeeping/frontend/app/dashboard/` → `fynix-frontend/app/dashboard/`

### Step 4: Create Environment File (1 min)

Create file: `fynix-frontend/.env.local`

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
NEXT_PUBLIC_API_URL=http://localhost:3000
```

Replace with your actual Supabase values from Settings → API

### Step 5: Run Development Server

```bash
npm run dev
```

Open browser to: **http://localhost:3000**

You should see the Next.js welcome page!

---

## What's Next?

1. **Test locally**: Upload a receipt and verify it works
2. **Deploy to Vercel**: `vercel deploy`
3. **Update API URL**: Change to your Railway API URL in production

---

## Troubleshooting

### "Module not found" errors
Run: `npm install` again

### Port 3000 already in use
Your backend is using port 3000. The frontend will auto-switch to port 3001.

### Supabase connection errors
- Check your `.env.local` file
- Verify Supabase URL and key are correct
- Make sure there are no quotes around the values

---

## File Structure

After setup, your project should look like:

```
fynix-frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx          ← Dashboard page
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   └── ReceiptUpload.tsx     ← Upload component
├── lib/
│   ├── supabase.ts           ← Supabase client
│   └── api.ts                ← API client
├── types/
│   └── index.ts              ← TypeScript types
├── .env.local                ← Environment variables
└── package.json
```

---

## Quick Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Deploy to Vercel
vercel
```

---

You're ready to build! 🚀
