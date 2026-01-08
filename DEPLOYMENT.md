# 🚀 Deployment Guide - Presti Intent Platform

## Prerequisites

- Node.js 18+ and pnpm
- Python 3.9+ (for scraping scripts)
- OpenAI API Key
- Vercel account (for deployment)

## 📋 Environment Variables

### Required for Production

Create a `.env.local` file at the root with:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### For Vercel Deployment

Add environment variables in Vercel Dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add: `OPENAI_API_KEY` with your API key

## 🔧 Local Development Setup

### 1. Install Dependencies

```bash
# Install Node.js dependencies
pnpm install

# Install Python dependencies (for scraping)
cd database
python3 -m venv venv_async
source venv_async/bin/activate
pip install -r requirements.txt
cd ..
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env.local

# Edit .env.local and add your OpenAI API key
```

### 3. Run Development Server

```bash
pnpm run dev
```

Visit `http://localhost:3000`

## 🌐 Vercel Deployment

### Option 1: Via GitHub (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "feat: your commit message"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Add environment variables (OPENAI_API_KEY)
   - Deploy!

### Option 2: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

## 🔐 Security Checklist

- ✅ `.env` files are in `.gitignore`
- ✅ No hardcoded API keys in code
- ✅ Environment variables properly configured
- ✅ `database/venv/` and `database/venv_async/` ignored
- ✅ `.next/` build folder ignored

## 📊 Running Scraping Scripts

### Company News

```bash
cd database
source venv_async/bin/activate
export OPENAI_API_KEY=your_key_here

# Test single company
python scrape_company_news_async.py test "California Closets"

# Run for all companies
python scrape_company_news_async.py
```

### Management Interviews

```bash
cd database
source venv_async/bin/activate
export OPENAI_API_KEY=your_key_here

# Test single company
python scrape_management_interviews.py test "California Closets"

# Run for all companies
python scrape_management_interviews.py
```

## 🔄 Updating Data on Vercel

Data can be updated in two ways:

### 1. Via Refresh Button (Recommended)
- Use the "Refresh" button in the UI
- Scrapes data directly from the deployed app
- Requires OPENAI_API_KEY in Vercel environment variables

### 2. Manual Upload
- Run scraping scripts locally
- Update `public/news_data.json` and `public/management_interviews.json`
- Commit and push to trigger redeployment

## 📝 Build Process

```bash
# Production build
pnpm run build

# Check build output
ls -la .next/

# Test production build locally
pnpm run start
```

## 🐛 Troubleshooting

### "OPENAI_API_KEY environment variable is required"
- Make sure you've set the environment variable in Vercel
- For local: check your `.env.local` file

### "Failed to refresh data"
- Check API route logs in Vercel
- Verify OpenAI API key is valid
- Check if you have remaining API credits

### Build fails on Vercel
- Check build logs in Vercel dashboard
- Ensure all dependencies are in `package.json`
- Verify TypeScript has no errors locally

## 📚 Additional Resources

- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [OpenAI API Documentation](https://platform.openai.com/docs)



