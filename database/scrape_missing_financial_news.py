#!/usr/bin/env python3
"""
Script pour scraper les Financial News des entreprises de Jerrica's accounts qui en manquent
"""

import json
import os
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement
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

# Configuration des workers
MAX_CONCURRENT_COMPANIES = 4


def normalize_date_for_sorting(date_str: str) -> str:
    """Convertir la date en format YYYY-MM-DD pour le tri"""
    if not date_str or date_str == "N/A":
        return "2025-01-01"
    
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str
    
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
    
    if len(date_str) == 4 and date_str.isdigit():
        return f"{date_str}-01-01"
    
    return "2025-01-01"


async def search_perplexity_financial(
    session: aiohttp.ClientSession,
    company_name: str
) -> Dict[str, Any]:
    """Recherche de données financières via Perplexity"""
    
    prompt = f"""Search for recent financial information about {company_name} (2023-2026).

Find 5-7 key financial documents and for EACH provide:
- Title (exact)
- Source (company IR website, SEC Edgar, Yahoo Finance, etc.)
- URL (complete, direct link)
- Publication date (EXACT date: "YYYY-MM-DD" or "Q1 2025")
- Brief summary (2-3 sentences with key metrics)
- Quarter/period if applicable (Q1 2024, FY 2024, etc.)

Focus on:
- Earnings calls and transcripts
- 10-K and 10-Q SEC filings
- Quarterly earnings announcements
- Financial press releases
- Annual reports

Prioritize official sources:
- Company investor relations website
- SEC Edgar (sec.gov)
- Yahoo Finance
- SeekingAlpha

For each item, start with "Published on [DATE]:" followed by details."""
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a financial research expert. Search the web and provide detailed financial information with real URLs."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.2,
        "return_citations": True
    }
    
    try:
        async with session.post(PERPLEXITY_URL, headers=headers, json=payload, timeout=90) as response:
            if response.status != 200:
                return {"content": "", "citations": []}
            
            result = await response.json()
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            return {
                "content": content,
                "citations": citations
            }
    
    except Exception as e:
        print(f"    ❌ Erreur Perplexity: {e}")
        return {"content": "", "citations": []}


async def scrape_company_financial_news(company_name: str) -> Dict[str, Any]:
    """Scrape financial news pour une entreprise"""
    
    print(f"💰 {company_name}...", end=" ", flush=True)
    
    async with aiohttp.ClientSession() as session:
        search_result = await search_perplexity_financial(session, company_name)
        
        if not search_result['content']:
            print(f"❌ Échec")
            return None
        
        # Structurer avec OpenAI
        system_prompt = """You are an expert at extracting and structuring financial data.

Extract financial information and structure it as JSON.

IMPORTANT:
- Extract 5-10 unique financial items (2023-2026 only)
- Write 2-3 sentence summaries with specific numbers
- Extract key metrics as array
- All text in ENGLISH

Output format:
{
  "financial_items": [
    {
      "title": "Exact title",
      "source": "Source name",
      "url": "Complete URL",
      "period": "Q4 2024 or FY 2024",
      "document_type": "Press Release|SEC Filing|Earnings Report|Annual Report|Quarterly Results",
      "summary": "2-3 sentences with key financial highlights",
      "key_metrics": ["Revenue: $X billion", "Growth: +Y%"],
      "strategic_highlights": ["Key development 1", "Key development 2"],
      "published_date": "YYYY-MM-DD or Q1 2024",
      "category": "earnings",
      "relevance_score": 7
    }
  ]
}"""
        
        user_prompt = f"""Extract and structure financial information about {company_name}.

SEARCH RESULTS:
{search_result['content']}

CITATIONS:
{json.dumps(search_result['citations'], indent=2)}

INSTRUCTIONS:
1. Extract 5-10 unique financial items
2. Use ONLY URLs from citations
3. Write summaries with specific metrics
4. Remove duplicates
5. Extract exact dates

Return ONLY valid JSON."""
        
        try:
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
            
            # Post-processing
            for item in financial_items:
                original_date = item.get('published_date', '')
                item['date'] = normalize_date_for_sorting(original_date)
            
            print(f"✅ {len(financial_items)} items")
            
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
                    "themes_searched": ["earnings", "quarterly_results", "sec_filings"]
                }
            }
        
        except Exception as e:
            print(f"❌ Erreur OpenAI: {e}")
            return None


def normalize_name(name):
    """Normalise le nom de l'entreprise"""
    return name.lower().replace(',', '').replace('.', '').replace('-', ' ').replace('&', 'and').strip()


async def process_missing_companies():
    """Traite les entreprises manquantes"""
    
    # Charger les données existantes
    with open('../public/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Charger financial_news existant
    try:
        with open('../public/financial_news.json', 'r', encoding='utf-8') as f:
            financial_data = json.load(f)
    except FileNotFoundError:
        financial_data = {}
    
    # Liste des entreprises de Jerrica's accounts
    jerrica_accounts = [
        "La-Z-Boy", "Williams Sonoma", "Millerknoll", "Palliser Furniture Ltd.",
        "Rooms to Go", "Article", "American Leather", "Serena & Lily",
        "Anthropologie Home", "Rowe Furniture", "Room & Board", "Bassett Furniture",
        "Living Spaces", "Jonathan Louis", "Theodore Alexander", "Kimball International",
        "Ballard Designs", "Design Within Reach", "Saks Global", "Costco"
    ]
    
    # Identifier les entreprises manquantes
    companies_normalized = {normalize_name(name): name for name in data['companies'].keys()}
    financial_normalized = {normalize_name(name): name for name in financial_data.keys()}
    
    missing_companies = []
    for company in jerrica_accounts:
        norm_name = normalize_name(company)
        data_name = companies_normalized.get(norm_name)
        
        if data_name:
            jobs_count = len(data['companies'][data_name]['jobs'])
            has_financial = norm_name in financial_normalized
            
            if jobs_count > 0 and not has_financial:
                missing_companies.append(company)
    
    print(f"\n{'='*80}")
    print(f"🚀 SCRAPING FINANCIAL NEWS - ENTREPRISES MANQUANTES")
    print(f"{'='*80}")
    print(f"📊 {len(missing_companies)} entreprises à traiter")
    print(f"{'='*80}\n")
    
    # Créer un semaphore pour limiter les requêtes simultanées
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_COMPANIES)
    
    async def process_with_semaphore(company_name: str):
        async with semaphore:
            try:
                company_financial = await scrape_company_financial_news(company_name)
                return company_name, company_financial
            except Exception as e:
                print(f"❌ Erreur pour {company_name}: {e}")
                return company_name, None
    
    # Lancer toutes les tâches
    tasks = [process_with_semaphore(company) for company in missing_companies]
    
    for coro in asyncio.as_completed(tasks):
        try:
            company_name, company_financial = await coro
            if company_financial:
                financial_data[company_name] = company_financial
                
                # Sauvegarde incrémentale
                with open('../public/financial_news.json', 'w', encoding='utf-8') as f:
                    json.dump(financial_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
    
    print("\n✅ Scraping terminé!")
    print(f"📁 Résultats sauvegardés dans ../public/financial_news.json")
    
    # Statistiques
    new_companies = len([c for c in missing_companies if c in financial_data])
    print(f"\n📈 Statistiques:")
    print(f"   - Entreprises traitées avec succès: {new_companies}/{len(missing_companies)}")
    print(f"   - Total entreprises dans financial_news.json: {len(financial_data)}")


if __name__ == "__main__":
    asyncio.run(process_missing_companies())
