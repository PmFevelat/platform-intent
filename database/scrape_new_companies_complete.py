#!/usr/bin/env python3
"""
Script MAÎTRE pour scraper 17 nouvelles entreprises
Enchaîne automatiquement :
1. Scraping des jobs (Mantiks API)
2. Analyse des jobs (OpenAI GPT-4o)
3. Company news (Perplexity + OpenAI)
4. Management interviews (Perplexity + OpenAI)
5. Mise à jour du frontend
"""

import json
import os
import asyncio
import aiohttp
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional

# Charger les variables d'environnement
load_dotenv()

# Configuration
MANTIKS_API_KEY = os.environ.get("MANTIKS_API_KEY")
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not MANTIKS_API_KEY:
    raise ValueError("MANTIKS_API_KEY environment variable is required")
if not PERPLEXITY_API_KEY:
    raise ValueError("PERPLEXITY_API_KEY environment variable is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

MANTIKS_API_URL = "https://api.mantiks.io/company/jobs"
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Mots-clés pour Mantiks
JOB_KEYWORDS = [
    "digital strategy", "digital experience", "group design", "art",
    "graphic design", "sales", "revenue", "digital marketing",
    "international marketing", "product marketing", "group marketing",
    "brand marketing", "strategic marketing", "marketing",
    "ecommerce", "e-commerce", "digital", "creative",
    "group creative", "global creative"
]

# Nouvelles entreprises
NEW_COMPANIES = [
    "Millerknoll", "Palliser Furniture Ltd.", "Rooms to Go", "Article",
    "American Leather", "Serena & Lily", "Anthropologie Home", "Rowe Furniture",
    "Room & Board", "Bassett Furniture", "Living Spaces", "Jonathan Louis",
    "Theodore Alexander", "Kimball International", "Ballard Designs",
    "Design Within Reach", "Saks Global"
]


def print_header(text):
    """Affiche un en-tête stylisé"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def clean_url(url):
    """Nettoie l'URL pour l'API"""
    if not url:
        return url
    for suffix in ['/fr/', '/en/', '/de/', '/es/', '/it/']:
        if url.endswith(suffix):
            url = url[:-len(suffix)] + '/'
    return url


# ============================================================================
# ÉTAPE 1 : SCRAPING DES JOBS (MANTIKS)
# ============================================================================

def fetch_jobs_for_company(company: Dict) -> Dict:
    """Récupère les jobs via Mantiks API"""
    headers = {
        'accept': 'application/json',
        'x-api-key': MANTIKS_API_KEY
    }
    
    website = clean_url(company['website'])
    
    params = [
        ('website', website),
        ('age_in_days', 365)
    ]
    
    for kw in JOB_KEYWORDS:
        params.append(('keyword', kw))
    
    if company.get('linkedin'):
        params.append(('linkedin_url', company['linkedin']))
    
    try:
        response = requests.get(MANTIKS_API_URL, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'jobs': data.get('jobs', []),
                'nb_jobs': data.get('nb_jobs', 0),
                'credits_remaining': data.get('credits_remaining'),
                'credits_cost': data.get('credits_cost', 0)
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}",
                'jobs': [],
                'nb_jobs': 0
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'jobs': [],
            'nb_jobs': 0
        }


def scrape_jobs_for_new_companies():
    """Scrape les jobs pour les nouvelles entreprises uniquement"""
    print_header("ÉTAPE 1/5 : SCRAPING DES JOBS (MANTIKS API)")
    
    # Charger jobs_data.json
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filtrer uniquement les nouvelles entreprises
    companies_to_scrape = []
    for company_entry in data['companies']:
        company_name = company_entry.get('company', {}).get('name', '')
        if company_name in NEW_COMPANIES:
            companies_to_scrape.append(company_entry)
    
    print(f"🔍 {len(companies_to_scrape)} entreprises à scraper\n")
    
    updated_count = 0
    total_jobs = 0
    
    for i, company_entry in enumerate(companies_to_scrape, 1):
        company = company_entry['company']
        company_name = company['name']
        
        print(f"[{i}/{len(companies_to_scrape)}] {company_name}...", end=" ")
        
        result = fetch_jobs_for_company(company)
        
        # Mettre à jour l'entrée dans data
        for entry in data['companies']:
            if entry.get('company', {}).get('name') == company_name:
                entry['success'] = result['success']
                entry['jobs'] = result['jobs']
                entry['nb_jobs'] = result['nb_jobs']
                if 'credits_remaining' in result:
                    entry['credits_remaining'] = result['credits_remaining']
                if 'credits_cost' in result:
                    entry['credits_cost'] = result['credits_cost']
                if 'error' in result:
                    entry['error'] = result['error']
                break
        
        if result['success']:
            nb_jobs = result['nb_jobs']
            total_jobs += nb_jobs
            if nb_jobs > 0:
                updated_count += 1
            print(f"✅ {nb_jobs} jobs trouvés")
        else:
            print(f"❌ Erreur: {result.get('error', 'Unknown')[:50]}")
        
        time.sleep(0.5)
    
    # Sauvegarder
    with open('jobs_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Jobs scrapés : {total_jobs} jobs trouvés pour {updated_count} entreprises")
    print(f"💾 Sauvegardé dans jobs_data.json")


# ============================================================================
# ÉTAPE 2 : ANALYSE DES JOBS (OpenAI)
# ============================================================================

async def analyze_job_with_openai(job: Dict, company_name: str) -> Optional[Dict]:
    """Analyse un job avec OpenAI GPT-4o"""
    
    system_prompt = """You are an expert analyst specialized in identifying buying signals for AI visual content generation services.

Analyze this job posting and extract structured information about:
1. Relevance score (1-10) for an AI company that generates product lifestyle images
2. Team structure and decision makers
3. Tools ecosystem (design, 3D, ecommerce platforms)
4. Strategic priorities
5. Budget indicators

Be thorough and precise."""

    user_prompt = f"""Analyze this job from {company_name}:

TITLE: {job.get('job_title', 'N/A')}
LOCATION: {job.get('location', 'N/A')}
DESCRIPTION:
{job.get('description', 'N/A')[:4000]}

Return JSON with this structure:
{{
  "relevance_score": <1-10>,
  "relevance_reason": "Why relevant for AI visual content company",
  "team_structure": {{
    "decision_makers": [
      {{"role": "title", "seniority": "C-level/VP/Director/Manager"}}
    ],
    "team_size_indicators": []
  }},
  "tools_ecosystem": {{
    "design_tools": [{{"tool": "name", "proficiency": "expert/advanced/basic"}}],
    "3d_tools": [{{"tool": "name"}}],
    "ecommerce_platforms": [{{"platform": "name"}}]
  }},
  "strategic_priorities": [
    {{"priority": "name", "urgency": "high/medium/low"}}
  ],
  "budget_indicators": {{
    "salary_range": "range if mentioned",
    "team_expansion": "yes/no/maybe",
    "investment_signals": []
  }}
}}"""

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
        
        content = response.choices[0].message.content
        analysis = json.loads(content)
        return analysis
    
    except Exception as e:
        print(f"❌ Erreur analyse: {e}")
        return None


async def analyze_jobs_for_company(company_entry: Dict) -> int:
    """Analyse tous les jobs d'une entreprise"""
    jobs = company_entry.get('jobs', [])
    if not jobs:
        return 0
    
    company_name = company_entry.get('company', {}).get('name', 'Unknown')
    analyzed_count = 0
    
    for job in jobs:
        # Skip si déjà analysé
        if job.get('analysis'):
            continue
        
        analysis = await analyze_job_with_openai(job, company_name)
        if analysis:
            job['analysis'] = analysis
            analyzed_count += 1
    
    return analyzed_count


async def analyze_all_jobs():
    """Analyse tous les jobs des nouvelles entreprises"""
    print_header("ÉTAPE 2/5 : ANALYSE DES JOBS (OpenAI GPT-4o)")
    
    # Charger jobs_data.json
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filtrer les nouvelles entreprises avec des jobs
    companies_to_analyze = []
    for company_entry in data['companies']:
        company_name = company_entry.get('company', {}).get('name', '')
        if company_name in NEW_COMPANIES and company_entry.get('nb_jobs', 0) > 0:
            companies_to_analyze.append(company_entry)
    
    print(f"🔍 {len(companies_to_analyze)} entreprises avec des jobs à analyser\n")
    
    total_analyzed = 0
    
    for i, company_entry in enumerate(companies_to_analyze, 1):
        company_name = company_entry.get('company', {}).get('name')
        nb_jobs = company_entry.get('nb_jobs', 0)
        
        print(f"[{i}/{len(companies_to_analyze)}] {company_name} ({nb_jobs} jobs)...", end=" ")
        
        analyzed = await analyze_jobs_for_company(company_entry)
        total_analyzed += analyzed
        
        print(f"✅ {analyzed} jobs analysés")
        
        # Sauvegarder après chaque entreprise
        with open('jobs_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Total : {total_analyzed} jobs analysés")


# ============================================================================
# ÉTAPE 3 & 4 : COMPANY NEWS & MANAGEMENT INTERVIEWS
# ============================================================================

async def search_with_perplexity(
    session: aiohttp.ClientSession,
    company_name: str,
    company_website: str,
    search_type: str
) -> Optional[Dict[str, Any]]:
    """Recherche avec Perplexity"""
    
    if search_type == "news":
        print(f"📰 {company_name} - Recherche news...")
        prompt = f"""Search the web for recent news articles about {company_name} from 2024-2026.

TOPICS: E-commerce growth, digital transformation, product catalog, AI adoption, 
visualization tech, product photography, customization, marketing campaigns.

Find 10-15 articles with REAL URLs. List each with:
- Title
- Source
- Complete URL
- Date
- Brief summary"""
    else:  # interviews
        print(f"🎤 {company_name} - Recherche interviews...")
        prompt = f"""Search for executive interviews from {company_name} (2024-2026).

TARGET: CEO, CMO, CTO, VP Ecommerce, VP Digital, VP Marketing

Find 8-12 interviews with REAL URLs. List each with:
- Title
- Source
- Complete URL
- Date
- Executive name and title
- Key insights"""

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "You are a research expert. Provide detailed information with real URLs."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4000,
        "temperature": 0.2,
        "return_citations": True
    }
    
    try:
        async with session.post(PERPLEXITY_URL, headers=headers, json=payload, timeout=90) as response:
            if response.status != 200:
                print(f"❌ Erreur Perplexity (status {response.status})")
                return None
            
            result = await response.json()
            
            if 'choices' not in result or len(result['choices']) == 0:
                return None
            
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            return {
                "raw_content": content,
                "citations": citations,
                "company_name": company_name
            }
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


async def structure_with_openai(perplexity_data: Dict, search_type: str) -> Optional[List]:
    """Structure les données avec OpenAI"""
    
    company_name = perplexity_data['company_name']
    raw_content = perplexity_data['raw_content']
    citations = perplexity_data['citations']
    
    if search_type == "news":
        system_prompt = """Extract and structure news articles into JSON.

Output format:
{
  "articles": [
    {
      "title": "title",
      "source": "publication",
      "url": "url",
      "published_date": "Month DD, YYYY",
      "date": "YYYY-MM-DD",
      "summary": "2-3 sentences",
      "presti_score": <1-10>,
      "relevance_reason": "why relevant",
      "key_insights": ["insight 1", "insight 2"],
      "category": "technology_innovation|ecommerce_growth|..."
    }
  ]
}"""
    else:
        system_prompt = """Extract and structure executive interviews into JSON.

Output format:
{
  "interviews": [
    {
      "title": "title",
      "source": "publication",
      "url": "url",
      "published_date": "Month DD, YYYY",
      "date": "YYYY-MM-DD",
      "executive": "Name and Title",
      "summary": "2-3 sentences",
      "key_insights": ["insight 1", "insight 2"],
      "presti_score": <1-10>
    }
  ]
}"""

    user_prompt = f"""Extract ALL items about {company_name}.

CONTENT:
{raw_content}

CITATIONS:
{json.dumps(citations, indent=2)}

Return ONLY JSON."""

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
        
        content = response.choices[0].message.content
        structured_data = json.loads(content)
        
        if search_type == "news":
            return structured_data.get('articles', [])
        else:
            return structured_data.get('interviews', [])
    
    except Exception as e:
        print(f"❌ Erreur OpenAI: {e}")
        return None


async def scrape_company_data(company_entry: Dict, search_type: str):
    """Scrape news ou interviews pour une entreprise"""
    company = company_entry['company']
    company_name = company['name']
    company_website = company['website']
    
    async with aiohttp.ClientSession() as session:
        # Étape 1 : Perplexity
        perplexity_result = await search_with_perplexity(
            session, company_name, company_website, search_type
        )
        
        if not perplexity_result:
            return None
        
        # Étape 2 : OpenAI
        structured_data = await structure_with_openai(perplexity_result, search_type)
        
        if not structured_data:
            return None
        
        return {
            "company_name": company_name,
            "items": structured_data,
            "search_date": datetime.now().isoformat(),
            "success": True,
            "count": len(structured_data)
        }


async def scrape_news_and_interviews():
    """Scrape news et interviews pour toutes les nouvelles entreprises"""
    print_header("ÉTAPE 3/5 : COMPANY NEWS (Perplexity + OpenAI)")
    
    # Charger jobs_data.json
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filtrer les nouvelles entreprises
    companies_to_scrape = []
    for company_entry in data['companies']:
        company_name = company_entry.get('company', {}).get('name', '')
        if company_name in NEW_COMPANIES:
            companies_to_scrape.append(company_entry)
    
    print(f"🔍 {len(companies_to_scrape)} entreprises à scraper\n")
    
    # Charger ou créer company_news.json
    news_path = 'company_news.json'
    if os.path.exists(news_path):
        with open(news_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    else:
        news_data = {}
    
    # Charger ou créer management_interviews.json
    interviews_path = 'management_interviews.json'
    if os.path.exists(interviews_path):
        with open(interviews_path, 'r', encoding='utf-8') as f:
            interviews_data = json.load(f)
    else:
        interviews_data = {}
    
    # Scraper chaque entreprise
    for i, company_entry in enumerate(companies_to_scrape, 1):
        company_name = company_entry.get('company', {}).get('name')
        
        print(f"\n[{i}/{len(companies_to_scrape)}] {company_name}")
        
        # Company News
        news_result = await scrape_company_data(company_entry, "news")
        if news_result:
            news_data[company_name] = {
                "company_name": company_name,
                "news_items": news_result['items'],
                "search_date": news_result['search_date'],
                "scrape_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "search_engine": "perplexity-sonar",
                    "structuring_model": "gpt-4o",
                    "success": True,
                    "articles_found": news_result['count']
                }
            }
            print(f"  ✅ News: {news_result['count']} articles")
            
            # Sauvegarder après chaque entreprise
            with open(news_path, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
        
        await asyncio.sleep(2)  # Pause entre requêtes
        
        # Management Interviews
        print_header("ÉTAPE 4/5 : MANAGEMENT INTERVIEWS (Perplexity + OpenAI)")
        interviews_result = await scrape_company_data(company_entry, "interviews")
        if interviews_result:
            interviews_data[company_name] = {
                "company_name": company_name,
                "interviews": interviews_result['items'],
                "search_date": interviews_result['search_date'],
                "scrape_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "search_engine": "perplexity-sonar",
                    "structuring_model": "gpt-4o",
                    "success": True,
                    "interviews_found": interviews_result['count']
                }
            }
            print(f"  ✅ Interviews: {interviews_result['count']} interviews")
            
            # Sauvegarder après chaque entreprise
            with open(interviews_path, 'w', encoding='utf-8') as f:
                json.dump(interviews_data, f, ensure_ascii=False, indent=2)
        
        await asyncio.sleep(2)  # Pause entre requêtes
    
    print(f"\n✅ News et interviews scrapées pour toutes les entreprises")


# ============================================================================
# ÉTAPE 5 : MISE À JOUR FRONTEND
# ============================================================================

def update_frontend():
    """Met à jour les fichiers du frontend"""
    print_header("ÉTAPE 5/5 : MISE À JOUR DU FRONTEND")
    
    # Copier company_news.json vers public/news_data.json
    if os.path.exists('company_news.json'):
        with open('company_news.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        with open('../public/news_data.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        print(f"✅ news_data.json mis à jour ({len(news_data)} entreprises)")
    
    # Copier management_interviews.json vers public/
    if os.path.exists('management_interviews.json'):
        with open('management_interviews.json', 'r', encoding='utf-8') as f:
            interviews_data = json.load(f)
        with open('../public/management_interviews.json', 'w', encoding='utf-8') as f:
            json.dump(interviews_data, f, ensure_ascii=False, indent=2)
        print(f"✅ management_interviews.json mis à jour ({len(interviews_data)} entreprises)")
    
    # Convertir jobs_data.json vers public/data.json (jobs_analysis.json)
    print("🔄 Conversion des jobs pour le frontend...")
    
    # Charger jobs_data.json
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)
    
    # Créer la structure pour le frontend
    frontend_companies = {}
    
    for company_entry in jobs_data['companies']:
        company = company_entry.get('company', {})
        company_name = company.get('name', '')
        
        # Normaliser le nom (lowercase)
        company_key = company_name.lower()
        
        frontend_companies[company_key] = {
            "name": company_name,
            "website": company.get('website', ''),
            "linkedin": company.get('linkedin', ''),
            "industry": company.get('industry', 'Furniture'),
            "employees": company.get('employees', ''),
            "jobs": company_entry.get('jobs', []),
            "total_jobs": company_entry.get('nb_jobs', 0)
        }
    
    # Sauvegarder dans public/jobs_analysis.json
    frontend_data = {"companies": frontend_companies}
    with open('../public/jobs_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(frontend_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ jobs_analysis.json mis à jour ({len(frontend_companies)} entreprises)")
    
    print("\n" + "="*80)
    print("✅ FRONTEND MIS À JOUR")
    print("="*80)


# ============================================================================
# MAIN
# ============================================================================

async def main():
    start_time = datetime.now()
    
    print("\n" + "="*80)
    print("🚀 SCRAPING COMPLET - 17 NOUVELLES ENTREPRISES")
    print("="*80)
    print(f"🕒 Démarrage : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # ÉTAPE 1 : Scraping des jobs
    try:
        scrape_jobs_for_new_companies()
    except Exception as e:
        print(f"❌ Erreur étape 1: {e}")
        return
    
    # ÉTAPE 2 : Analyse des jobs
    try:
        await analyze_all_jobs()
    except Exception as e:
        print(f"❌ Erreur étape 2: {e}")
        return
    
    # ÉTAPES 3 & 4 : News et Interviews
    try:
        await scrape_news_and_interviews()
    except Exception as e:
        print(f"❌ Erreur étapes 3-4: {e}")
        return
    
    # ÉTAPE 5 : Mise à jour frontend
    try:
        update_frontend()
    except Exception as e:
        print(f"❌ Erreur étape 5: {e}")
        return
    
    # Résumé final
    elapsed_time = datetime.now() - start_time
    print("\n" + "="*80)
    print("✅ PROCESSUS COMPLET TERMINÉ")
    print("="*80)
    print(f"⏱️  Durée totale : {elapsed_time}")
    print("\n📁 Fichiers générés/mis à jour :")
    print("   ✓ database/jobs_data.json")
    print("   ✓ database/company_news.json")
    print("   ✓ database/management_interviews.json")
    print("   ✓ public/jobs_analysis.json")
    print("   ✓ public/news_data.json")
    print("   ✓ public/management_interviews.json")
    print("\n🎨 Prochaine étape :")
    print("   → Relancez l'application Next.js pour voir les nouvelles données")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

