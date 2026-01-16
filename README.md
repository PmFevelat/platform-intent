# Intent

This is a [Next.js](https://nextjs.org/) project bootstrapped with TypeScript, Tailwind CSS, and ESLint.

## Getting Started

First, install the dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `src/app/page.tsx`. The page auto-updates as you edit the file.

## Features

### 📊 Jobs Analysis
Analyse des offres d'emploi des entreprises prospects pour identifier les opportunités commerciales.

### 📰 News (Nouveau!)
Récupération et analyse automatique des actualités d'entreprises pour obtenir des insights commerciaux pertinents.

- Génération d'actualités avec OpenAI GPT-4o
- Scoring de pertinence pour Presti
- Catégorisation intelligente (IA, e-commerce, digital transformation, etc.)
- Insights pour l'approche commerciale

**Documentation complète:** Voir [FEATURE_NEWS_COMPLETE.md](FEATURE_NEWS_COMPLETE.md)

**Guide d'utilisation:** Voir [database/README_NEWS.md](database/README_NEWS.md)

## Project Structure

```
Intent/
├── src/
│   ├── app/          # App Router (Next.js 13+)
│   │   ├── jobs/     # Module Jobs
│   │   └── news/     # Module News (nouveau!)
│   ├── components/   # React components
│   └── lib/          # Utilities & types
├── database/         # Scripts Python pour le scraping
│   ├── scrape_company_news.py  # Scraping des actualités
│   ├── update_news.sh          # Helper script
│   └── README_NEWS.md          # Documentation News
├── public/           # Static assets
│   ├── data.json     # Données des jobs
│   └── news_data.json # Données des actualités (nouveau!)
└── ...
```

## Learn MoreTo learn more about Next.js, take a look at the following resources:- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
