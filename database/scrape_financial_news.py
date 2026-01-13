#!/usr/bin/env python3
"""
Script de scraping pour les données financières des entreprises
- Earning calls & transcripts
- Financial reports (10-K, 10-Q)
- Quarterly/Annual results
- Financial press releases
- Analyst coverage & ratings
"""

import json
import os
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any
import argparse
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
if not PERPLEXITY_API_KEY:
    raise ValueError("PERPLEXITY_API_KEY environment variable is required")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


def normalize_date_for_sorting(date_str: str) -> str:
    """
    Convertir la date en format YYYY-MM-DD pour le tri chronologique.
    
    Args:
        date_str: Date au format "December 2025", "2025-12-15", "Q4 2025", etc.
    
    Returns:
        Date normalisée au format YYYY-MM-DD
    """
    if not date_str or date_str == "N/A":
        return "2025-01-01"
    
    # Déjà au format YYYY-MM-DD
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str
    
    # Format "Month YYYY" (ex: "December 2025")
    months = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    
    for month_name, month_num in months.items():
        if month_name.lower() in date_str.lower():
            parts = date_str.split()
            year = parts[-1] if len(parts) > 0 else "2025"
            return f"{year}-{month_num}-01"
    
    # Format "Q1 2025", "Q2 2024", etc.
    if 'q1' in date_str.lower():
        year = date_str.split()[-1] if len(date_str.split()) > 1 else "2025"
        return f"{year}-01-01"
    elif 'q2' in date_str.lower():
        year = date_str.split()[-1] if len(date_str.split()) > 1 else "2025"
        return f"{year}-04-01"
    elif 'q3' in date_str.lower():
        year = date_str.split()[-1] if len(date_str.split()) > 1 else "2025"
        return f"{year}-07-01"
    elif 'q4' in date_str.lower():
        year = date_str.split()[-1] if len(date_str.split()) > 1 else "2025"
        return f"{year}-10-01"
    
    # Juste une année "2025"
    if len(date_str) == 4 and date_str.isdigit():
        return f"{date_str}-01-01"
    
    # Fallback
    return "2025-01-01"


async def search_perplexity_financial_theme(
    session: aiohttp.ClientSession,
    company_name: str,
    theme: str
) -> Dict[str, Any]:
    """
    Recherche ciblée sur un thème financier spécifique
    """
    
    # Définition des thèmes financiers
    financial_themes = {
        "earnings_calls": {
            "keywords": "earnings call, earnings transcript, quarterly earnings, investor call, conference call transcript",
            "description": "Earnings Calls & Transcripts"
        },
        "financial_reports": {
            "keywords": "10-K, 10-Q, annual report, quarterly report, SEC filing, financial statements, investor presentation",
            "description": "Financial Reports & SEC Filings"
        },
        "quarterly_results": {
            "keywords": "Q1 results, Q2 results, Q3 results, Q4 results, quarterly results, earnings results, financial performance",
            "description": "Quarterly Results"
        },
        "financial_press": {
            "keywords": "financial press release, earnings announcement, revenue announcement, profit announcement, fiscal results",
            "description": "Financial Press Releases"
        },
        "analyst_coverage": {
            "keywords": "analyst rating, price target, analyst coverage, investment analysis, stock analysis, analyst report",
            "description": "Analyst Coverage & Ratings"
        }
    }
    
    theme_data = financial_themes.get(theme, financial_themes["earnings_calls"])
    print(f"  💰 Recherche thématique: {theme_data['description']}")
    
    prompt = f"""Search for recent financial information about {company_name} (2023-2026, prioritize 2024-2025) focused on: {theme_data['keywords']}.

CRITICAL: For EACH item found, you MUST identify and include the EXACT publication date or filing date.

Find 4-6 relevant financial items and for EACH provide:
- Title (exact)
- Source (publication name or "SEC Edgar" for filings, "Yahoo Finance", etc.)
- URL (complete, direct link to the document or article)
- **Publication/Filing date (EXACT date, format: "Month DD, YYYY" or "YYYY-MM-DD" or "Q1 2025")**
- Brief description of the content
- For earnings calls: Quarter reported (e.g., "Q4 2024", "Q3 2025")
- For financial reports: Report type (e.g., "10-K Annual", "10-Q Quarterly")

When listing each item, start with: "Published on [EXACT DATE]:" then provide the details.

Focus on: {theme_data['keywords']}

Sources to prioritize:
- Company investor relations website
- SEC Edgar (sec.gov) for official filings
- Yahoo Finance for earnings summaries
- SeekingAlpha for transcripts
- Major financial news outlets (Reuters, Bloomberg, WSJ)"""
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a financial research expert. Search the web and provide detailed financial information with real URLs to earnings calls, SEC filings, and financial reports."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 3000,
        "temperature": 0.2,
        "return_citations": True
    }
    
    try:
        async with session.post(PERPLEXITY_URL, headers=headers, json=payload, timeout=90) as response:
            if response.status != 200:
                print(f"    ⚠️ Erreur {response.status} pour thème {theme}")
                return {"theme": theme, "content": "", "citations": []}
            
            result = await response.json()
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            print(f"    ✓ {len(citations)} citations trouvées")
            
            return {
                "theme": theme,
                "content": content,
                "citations": citations
            }
    
    except Exception as e:
        print(f"    ❌ Erreur pour thème {theme}: {e}")
        return {"theme": theme, "content": "", "citations": []}


async def scrape_financial_news(
    company_name: str
) -> Dict[str, Any]:
    """
    Scrape financial news avec PLUSIEURS recherches thématiques
    """
    
    print(f"\n{'='*80}")
    print(f"💰 SCRAPING MULTI-THÉMATIQUE : Financial News pour {company_name}")
    print(f"{'='*80}")
    
    async with aiohttp.ClientSession() as session:
        # Lancer 5 recherches en parallèle
        themes = ["earnings_calls", "financial_reports", "quarterly_results", "financial_press", "analyst_coverage"]
        
        print(f"\n🔍 Lancement de {len(themes)} recherches parallèles...")
        tasks = [
            search_perplexity_financial_theme(session, company_name, theme)
            for theme in themes
        ]
        
        all_results = await asyncio.gather(*tasks)
        
        # Combiner tous les contenus et citations
        combined_content = "\n\n---THEME SEPARATOR---\n\n".join([
            f"THEME: {r['theme']}\n{r['content']}"
            for r in all_results if r['content']
        ])
        
        all_citations = []
        for r in all_results:
            all_citations.extend(r['citations'])
        
        print(f"\n✅ {len(all_results)} recherches terminées")
        print(f"📊 Total: {len(combined_content)} caractères, {len(all_citations)} citations")
        
        # Structurer avec OpenAI
        print(f"\n📊 [OpenAI] Structuration de toutes les données financières...")
        
        system_prompt = """You are an expert at extracting and structuring financial data for business analysis.

CONTEXT: We need to track financial performance, earnings reports, and financial communications for furniture and home goods companies.

WHAT TO EXTRACT:
1. Earnings Calls & Transcripts (priorité haute)
2. SEC Filings (10-K Annual Reports, 10-Q Quarterly Reports)
3. Quarterly/Annual Results Announcements
4. Financial Press Releases
5. Analyst Reports & Ratings

CRITICAL FIELDS TO EXTRACT:
- Exact title of document/article
- Source (Company IR site, SEC Edgar, Yahoo Finance, SeekingAlpha, etc.)
- Complete URL (direct link to document/transcript)
- Publication/Filing date (EXACT date: "YYYY-MM-DD" or "Q1 2024")
- Quarter/Period (for earnings: "Q1 2024", "Q4 2023", "FY 2024")
- Document type: "earnings_call" | "sec_filing" | "quarterly_results" | "press_release" | "analyst_report"
- Key financial metrics discussed (revenue, profit, margins, guidance, etc.)
- Strategic highlights (expansions, investments, challenges, opportunities)

DATE PARSING RULES:
- Look for dates near title: "December 15, 2024", "Dec 15, 2024"
- For quarterly items without exact date: "Q4 2024" → "2024-10-01", "Q1 2025" → "2025-01-01"
- Prefer filing/publication date over reporting period
- If NO date found, use "2024" as fallback

SUMMARY REQUIREMENTS:
- Write 3-4 sentences summarizing key financial highlights
- Include specific numbers (revenue, profit, growth %)
- Mention strategic initiatives or guidance
- Note any significant changes or trends

SCORING (1-10):
- 9-10: Detailed earnings transcripts, comprehensive financial reports with strategic insights
- 7-8: Quarterly results, financial press releases with metrics and guidance
- 5-6: Analyst reports, summaries, financial news articles
- 3-4: Brief mentions, limited financial details
- 1-2: Irrelevant or outdated

IMPORTANT RULES:
1. Extract 15-20 unique financial items (prioritize last 2 years)
2. Remove duplicates (same title or URL)
3. INCLUDE items from 2023-2026 only
4. Write detailed 3-4 sentence summaries with specific numbers
5. Extract key financial metrics as array
6. ALL text must be in ENGLISH

Output format:
{
  "financial_items": [
    {
      "title": "Exact title",
      "source": "Source name",
      "url": "Complete URL",
      "published_date": "YYYY-MM-DD or Q1 2024",
      "date": "YYYY-MM-DD",
      "period": "Q4 2024 or FY 2024",
      "document_type": "earnings_call|sec_filing|quarterly_results|press_release|analyst_report",
      "summary": "3-4 sentences with key financial highlights and strategic insights",
      "key_metrics": [
        "Revenue: $X billion (+Y% YoY)",
        "Net income: $X million",
        "Gross margin: X%",
        "Guidance: ...",
        "Other key metrics"
      ],
      "strategic_highlights": [
        "Key initiative or development 1",
        "Key initiative or development 2",
        "Key initiative or development 3"
      ],
      "relevance_score": 8,
      "category": "earnings|financial_performance|guidance|sec_filing|analyst_coverage"
    }
  ]
}"""
        
        user_prompt = f"""Extract and structure financial information about {company_name} from these search results.

COMBINED SEARCH RESULTS:
{combined_content}

ALL CITATIONS:
{json.dumps(list(set(all_citations)), indent=2)}

CRITICAL INSTRUCTIONS:
1. Extract unique financial items (aim for 15-20 items from 2023-2026)
2. PRIORITIZE:
   ✅ Earnings call transcripts
   ✅ 10-K and 10-Q SEC filings
   ✅ Quarterly earnings announcements
   ✅ Financial press releases with metrics
   ✅ Analyst reports with detailed analysis
3. For each item, extract:
   - Exact title and source
   - Complete URL (must be from citations)
   - Exact date (publication or filing date)
   - Quarter/period (Q1 2024, Q4 2023, FY 2024)
   - Document type (earnings_call, sec_filing, etc.)
   - Key financial metrics with specific numbers
   - Strategic highlights and guidance
4. Write 3-4 sentence summaries including:
   - Main financial results (revenue, profit, growth %)
   - Key strategic developments
   - Future guidance or outlook
5. Remove duplicates (same title/URL)
6. Use ONLY URLs from citations
7. DATE EXTRACTION:
   - Look for ANY date near title or in content
   - For quarterly items: "Q4 2024" → "2024-10-01"
   - Extract the MOST SPECIFIC date mentioned
   - Fallback if NO date: "2024"
8. Score based on: depth of financial details (9-10), earnings/reports (7-8), news articles (5-6)

EXAMPLES:
✅ "Q4 2024 Earnings Call Transcript" - earnings_call, detailed metrics, strategic discussion
✅ "MillerKnoll 10-K Annual Report 2024" - sec_filing, comprehensive financial statements
✅ "MillerKnoll Reports Strong Q3 2025 Results" - quarterly_results, revenue and profit data
✅ "Analyst Report: MillerKnoll Upgrade to Buy" - analyst_report, price targets and analysis

Return ONLY the JSON object with the exact structure specified."""
        
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        structured_data = json.loads(response.choices[0].message.content)
        financial_items = structured_data.get('financial_items', [])
        
        # Post-processing: Ajouter champ "date" normalisé pour le tri
        for item in financial_items:
            original_date = item.get('published_date', '')
            item['date'] = normalize_date_for_sorting(original_date)
        
        print(f"✅ {len(financial_items)} items financiers structurés")
        
        return {
            "company_name": company_name,
            "financial_items": financial_items,
            "search_date": datetime.now().isoformat(),
            "scrape_metadata": {
                "timestamp": datetime.now().isoformat(),
                "search_engine": "perplexity-sonar",
                "structuring_model": "gpt-4o",
                "success": True,
                "items_found": len(financial_items),
                "themes_searched": themes
            }
        }


async def main():
    parser = argparse.ArgumentParser(description='Scraper Financial News')
    parser.add_argument('--company', type=str, required=True, help='Nom de l\'entreprise')
    parser.add_argument('--days', type=int, help='Nombre de jours (paramètre optionnel pour compatibilité API)')
    
    args = parser.parse_args()
    
    print(f"\n{'='*80}")
    print(f"🚀 SCRAPING FINANCIAL NEWS")
    print(f"{'='*80}")
    print(f"🏢 Entreprise : {args.company}")
    if args.days:
        print(f"📅 Période : {args.days} derniers jours")
    print(f"{'='*80}")
    
    # Financial News
    financial_data = await scrape_financial_news(args.company)
    
    # Sauvegarder - format pour l'API ou format standalone
    if args.days:
        # Mode API : sauvegarder dans financial_news_test.json avec structure {company: data}
        output_file = 'financial_news_test.json'
        output_data = {args.company: financial_data}
    else:
        # Mode standalone : sauvegarder dans financial_{company}_results.json
        output_file = f'financial_{args.company.replace(" ", "_")}_results.json'
        output_data = financial_data
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ Résultats sauvegardés dans {output_file}")
    print(f"{'='*80}")
    print(f"💰 Financial Items : {len(financial_data['financial_items'])} items")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())
