#!/usr/bin/env python3
"""Force le scraping des news/interviews/financial pour les 4 entreprises Pet Care"""

import json
import os
import asyncio
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

PET_CARE = ["Chewy", "Petco", "Petmate", "Petsmart"]

print("🐾 SCRAPING NEWS/INTERVIEWS - PET CARE")
print("="*70 + "\n")

async def search_perplexity(session, company_name, search_type):
    """Recherche avec Perplexity"""
    if search_type == "news":
        prompt = f"""Search for recent news articles about {company_name} (2024-2026).
FOCUS: ecommerce growth, digital transformation, product catalog, AI adoption, 
marketing campaigns, technology initiatives.
Find 10-15 articles with URLs."""
    elif search_type == "interviews":
        prompt = f"""Search for executive interviews from {company_name} (2024-2026).
TARGET: CEO, CMO, CTO, VP Digital, VP Marketing
Find 8-12 interviews with URLs."""
    else:  # financial
        prompt = f"""Search for {company_name} financial reports (2024-2026):
earnings calls, quarterly results, SEC filings, financial performance.
Find 8-10 documents with URLs."""
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Research expert. Provide detailed info with real URLs."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.2,
        "return_citations": True
    }
    
    try:
        async with session.post(PERPLEXITY_URL, headers=headers, json=payload, timeout=90) as response:
            if response.status != 200:
                return None
            result = await response.json()
            return {
                "raw_content": result['choices'][0]['message']['content'],
                "citations": result.get('citations', []),
                "company_name": company_name
            }
    except Exception as e:
        print(f"❌ Perplexity error: {e}")
        return None

async def structure_openai(perplexity_data, search_type):
    """Structure avec OpenAI"""
    company_name = perplexity_data['company_name']
    raw_content = perplexity_data['raw_content']
    citations = perplexity_data['citations']
    
    if search_type == "news":
        system_prompt = "Extract news articles into JSON array with: title, source, url, date, summary, relevance_score, key_insights, category"
    elif search_type == "interviews":
        system_prompt = "Extract interviews into JSON array with: title, source, url, date, executive_name, executive_title, summary, key_quotes, topics_discussed, relevance_score"
    else:
        system_prompt = "Extract financial docs into JSON array with: title, source, url, date, period, document_type, summary, key_metrics, strategic_highlights"
    
    user_prompt = f"""Extract items about {company_name}:

CONTENT: {raw_content}
CITATIONS: {json.dumps(citations)}

Return JSON: {{"items": [...]}}"""
    
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
        result = json.loads(response.choices[0].message.content)
        return result.get('items', [])
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return []

async def scrape_company(session, company_name, search_type):
    """Scrape une entreprise"""
    print(f"  {company_name}...", end=" ", flush=True)
    
    perplexity_data = await search_perplexity(session, company_name, search_type)
    if not perplexity_data:
        print("❌ Perplexity failed")
        return None
    
    items = await structure_openai(perplexity_data, search_type)
    print(f"✅ {len(items)} items")
    
    return {
        "company_name": company_name,
        "items": items,
        "count": len(items),
        "timestamp": datetime.now().isoformat()
    }

async def main():
    # 1. COMPANY NEWS
    print("📰 Company News")
    print("-"*70)
    
    news_path = 'company_news.json'
    news_data = json.load(open(news_path)) if os.path.exists(news_path) else {}
    
    async with aiohttp.ClientSession() as session:
        for company in PET_CARE:
            result = await scrape_company(session, company, "news")
            if result:
                news_data[company] = {
                    "company_name": company,
                    "news_items": result['items'],
                    "search_date": result['timestamp'],
                    "scrape_metadata": {
                        "timestamp": result['timestamp'],
                        "search_engine": "perplexity-sonar",
                        "structuring_model": "gpt-4o",
                        "success": True,
                        "items_found": result['count']
                    }
                }
            await asyncio.sleep(2)
    
    with open(news_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    with open('../public/news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    print("\n📋 Management Interviews")
    print("-"*70)
    
    interviews_path = 'management_interviews.json'
    interviews_data = json.load(open(interviews_path)) if os.path.exists(interviews_path) else {}
    
    async with aiohttp.ClientSession() as session:
        for company in PET_CARE:
            result = await scrape_company(session, company, "interviews")
            if result:
                interviews_data[company] = {
                    "company_name": company,
                    "management_items": result['items'],
                    "search_date": result['timestamp'],
                    "scrape_metadata": {
                        "timestamp": result['timestamp'],
                        "model": "gpt-4o",
                        "success": True,
                        "web_search_used": True
                    }
                }
            await asyncio.sleep(2)
    
    with open(interviews_path, 'w', encoding='utf-8') as f:
        json.dump(interviews_data, f, ensure_ascii=False, indent=2)
    
    with open('../public/management_interviews.json', 'w', encoding='utf-8') as f:
        json.dump(interviews_data, f, ensure_ascii=False, indent=2)
    
    print("\n💰 Financial News")
    print("-"*70)
    
    financial_path = 'financial_news.json'
    financial_data = json.load(open(financial_path)) if os.path.exists(financial_path) else {}
    
    async with aiohttp.ClientSession() as session:
        for company in PET_CARE:
            result = await scrape_company(session, company, "financial")
            if result:
                financial_data[company] = {
                    "company_name": company,
                    "financial_items": result['items'],
                    "search_date": result['timestamp'],
                    "scrape_metadata": {
                        "timestamp": result['timestamp'],
                        "search_engine": "perplexity-sonar",
                        "structuring_model": "gpt-4o",
                        "success": True,
                        "items_found": result['count'],
                        "themes_searched": ["earnings", "quarterly_results", "sec_filings"]
                    }
                }
            await asyncio.sleep(2)
    
    with open(financial_path, 'w', encoding='utf-8') as f:
        json.dump(financial_data, f, ensure_ascii=False, indent=2)
    
    with open('../public/financial_news.json', 'w', encoding='utf-8') as f:
        json.dump(financial_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*70)
    print("✅ SCRAPING TERMINÉ - Pet Care News/Interviews/Financial")
    print("="*70)

asyncio.run(main())
