# Fynix Frontend Setup Guide

## Quick Start

### 1. Create Next.js App

```bash
cd C:\Projects\contractor_bookkeeping
npx create-next-app@latest fynix-frontend --typescript --tailwind --app --no-src-dir
cd fynix-frontend
```

Answer the prompts:
- ✅ TypeScript
- ✅ ESLint
- ✅ Tailwind CSS
- ✅ App Router
- ❌ src/ directory (select No)
- ✅ Import alias (@/*)

### 2. Install Dependencies

```bash
npm install @supabase/supabase-js
npm install lucide-react
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-toast
npm install class-variance-authority clsx tailwind-merge
npm install react-dropzone
npm install date-fns
npm install recharts  # For charts/graphs
```

### 3. Set Up Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
NEXT_PUBLIC_API_URL=http://localhost:3000
```

For production:
```env
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
NEXT_PUBLIC_API_URL=https://your-api.railway.app
```

### 4. Copy Frontend Files

I've created the following structure for you:

```
fynix-frontend/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── signup/
│   │       └── page.tsx
│   ├── (dashboard)/
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── receipts/
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   ├── jobs/
│   │   │   └── page.tsx
│   │   └── settings/
│   │       └── page.tsx
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/          # Reusable UI components
│   ├── ReceiptUpload.tsx
│   ├── ReceiptCard.tsx
│   ├── JobMatchCard.tsx
│   └── Navigation.tsx
├── lib/
│   ├── supabase.ts  # Supabase client
│   └── api.ts       # API calls to your backend
└── types/
    └── index.ts     # TypeScript types
```

### 5. Run Development Server

```bash
npm run dev
```

Open http://localhost:3000

### 6. Build for Production

```bash
npm run build
npm start
```

## Next Steps

1. Deploy frontend to Vercel (recommended) or Netlify
2. Update NEXT_PUBLIC_API_URL to your Railway API URL
3. Configure custom domain
4. Test end-to-end flow

## Deployment

### Deploy to Vercel (Recommended)

```bash
npm install -g vercel
vercel login
vercel
```

Follow prompts and add environment variables in Vercel dashboard.

### Deploy to Netlify

```bash
npm install -g netlify-cli
netlify login
netlify deploy
```
