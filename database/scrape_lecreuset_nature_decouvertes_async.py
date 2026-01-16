#!/usr/bin/env python3
"""
Script MAÎTRE OPTIMISÉ ASYNC pour scraper Le Creuset et Nature & Découvertes
Utilise des workers asynchrones pour maximiser la vitesse :
1. Scraping des jobs (Mantiks API) - Parallèle
2. Analyse des jobs (OpenAI GPT-4o) - Batch processing
3. Company news (Perplexity + OpenAI) - Parallèle
4. Management interviews (Perplexity + OpenAI) - Parallèle
5. Mise à jour du frontend
"""

import json
import os
import asyncio
import aiohttp
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import concurrent.futures
from functools import partial

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

# Configuration pour l'optimisation
MAX_CONCURRENT_REQUESTS = 5
MAX_WORKERS = 10
BATCH_SIZE = 3

# Mots-clés pour Mantiks
JOB_KEYWORDS = [
    "digital strategy", "digital experience", "group design", "art",
    "graphic design", "sales", "revenue", "digital marketing",
    "international marketing", "product marketing", "group marketing",
    "brand marketing", "strategic marketing", "marketing",
    "ecommerce", "e-commerce", "digital", "creative",
    "group creative", "global creative", "visual merchandising",
    "content creation", "social media", "brand management"
]

# Nouvelles entreprises à scraper
TARGET_COMPANIES = ["Le Creuset", "Nature & Découvertes"]

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
# ÉTAPE 1 : SCRAPING DES JOBS (MANTIKS) - ASYNC
# ============================================================================

async def fetch_jobs_for_company_async(session: aiohttp.ClientSession, company: Dict) -> Dict:
    """Récupère les jobs via Mantiks API de façon asynchrone"""
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
        async with session.get(MANTIKS_API_URL, headers=headers, params=params, timeout=30) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'success': True,
                    'jobs': data.get('jobs', []),
                    'nb_jobs': data.get('nb_jobs', 0),
                    'credits_remaining': data.get('credits_remaining'),
                    'credits_cost': data.get('credits_cost', 0),
                    'company_name': company['name']
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status}",
                    'jobs': [],
                    'nb_jobs': 0,
                    'company_name': company['name']
                }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'jobs': [],
            'nb_jobs': 0,
            'company_name': company['name']
        }

async def scrape_jobs_for_target_companies_async():
    """Scrape les jobs pour toutes les entreprises en parallèle"""
    print_header("ÉTAPE 1/5 : SCRAPING DES JOBS (MANTIKS API) - ASYNC")
    
    # Charger jobs_data.json
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filtrer les entreprises cibles
    companies_to_scrape = []
    for company_entry in data['companies']:
        company_name = company_entry.get('company', {}).get('name', '')
        if company_name in TARGET_COMPANIES:
            companies_to_scrape.append(company_entry['company'])
    
    print(f"🚀 Scraping ASYNC de {len(companies_to_scrape)} entreprises en parallèle")
    for company in companies_to_scrape:
        print(f"  • {company['name']}")
    print()
    
    # Scraping en parallèle avec limitation de concurrence
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
    timeout = aiohttp.ClientTimeout(total=60)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Créer les tâches pour toutes les entreprises
        tasks = [
            fetch_jobs_for_company_async(session, company)
            for company in companies_to_scrape
        ]
        
        print(f"⚡ Lancement de {len(tasks)} requêtes simultanées...")
        start_time = time.time()
        
        # Exécuter toutes les tâches en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        print(f"✅ Scraping terminé en {elapsed:.2f}s")
    
    # Traiter les résultats
    total_jobs = 0
    success_count = 0
    
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Erreur: {result}")
            continue
        
        company_name = result['company_name']
        
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
                success_count += 1
            print(f"✅ {company_name}: {nb_jobs} jobs trouvés")
        else:
            print(f"❌ {company_name}: {result.get('error', 'Unknown')}")
    
    # Sauvegarder
    with open('jobs_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎯 Résultat : {total_jobs} jobs trouvés pour {success_count} entreprises")
    print(f"💾 Sauvegardé dans jobs_data.json")

# ============================================================================
# ÉTAPE 2 : ANALYSE DES JOBS (OpenAI) - BATCH PROCESSING
# ============================================================================

async def analyze_job_batch(jobs_batch: List[Dict], company_name: str) -> List[Optional[Dict]]:
    """Analyse un batch de jobs en parallèle"""
    
    system_prompt = """You are an expert analyst specialized in identifying buying signals for AI visual content generation services.

Analyze job postings and extract structured information about:
1. Relevance score (1-10) for an AI company that generates product lifestyle images
2. Team structure and decision makers
3. Tools ecosystem (design, 3D, ecommerce platforms)
4. Strategic priorities
5. Budget indicators

Be thorough and precise."""

    # Créer les tâches pour le batch
    tasks = []
    for job in jobs_batch:
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

        task = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        tasks.append(task)
    
    # Exécuter toutes les analyses en parallèle
    try:
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"❌ Erreur analyse job {i+1}: {response}")
                results.append(None)
            else:
                try:
                    content = response.choices[0].message.content
                    analysis = json.loads(content)
                    results.append(analysis)
                except Exception as e:
                    print(f"❌ Erreur parsing job {i+1}: {e}")
                    results.append(None)
        
        return results
    
    except Exception as e:
        print(f"❌ Erreur batch: {e}")
        return [None] * len(jobs_batch)

async def analyze_all_jobs_async():
    """Analyse tous les jobs des entreprises cibles avec batch processing"""
    print_header("ÉTAPE 2/5 : ANALYSE DES JOBS (OpenAI GPT-4o) - BATCH PROCESSING")
    
    # Charger jobs_data.json
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filtrer les entreprises cibles avec des jobs
    companies_to_analyze = []
    for company_entry in data['companies']:
        company_name = company_entry.get('company', {}).get('name', '')
        if company_name in TARGET_COMPANIES and company_entry.get('nb_jobs', 0) > 0:
            companies_to_analyze.append(company_entry)
    
    print(f"🚀 Analyse ASYNC de {len(companies_to_analyze)} entreprises avec batch processing")
    
    total_analyzed = 0
    
    for company_entry in companies_to_analyze:
        company_name = company_entry.get('company', {}).get('name')
        jobs = company_entry.get('jobs', [])
        
        # Filtrer les jobs non analysés
        jobs_to_analyze = [job for job in jobs if not job.get('analysis')]
        
        if not jobs_to_analyze:
            print(f"⏭️  {company_name}: Tous les jobs déjà analysés")
            continue
        
        print(f"🔍 {company_name}: {len(jobs_to_analyze)} jobs à analyser")
        
        # Diviser en batches
        batches = [
            jobs_to_analyze[i:i + BATCH_SIZE] 
            for i in range(0, len(jobs_to_analyze), BATCH_SIZE)
        ]
        
        analyzed_count = 0
        start_time = time.time()
        
        for i, batch in enumerate(batches, 1):
            print(f"  📦 Batch {i}/{len(batches)} ({len(batch)} jobs)...", end=" ")
            
            batch_results = await analyze_job_batch(batch, company_name)
            
            # Appliquer les résultats
            for job, analysis in zip(batch, batch_results):
                if analysis:
                    job['analysis'] = analysis
                    analyzed_count += 1
            
            print(f"✅ {sum(1 for r in batch_results if r)} analysés")
            
            # Petite pause entre les batches pour éviter le rate limiting
            if i < len(batches):
                await asyncio.sleep(0.5)
        
        elapsed = time.time() - start_time
        total_analyzed += analyzed_count
        
        print(f"  ⚡ {company_name}: {analyzed_count} jobs analysés en {elapsed:.2f}s")
        
        # Sauvegarder après chaque entreprise
        with open('jobs_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎯 Total : {total_analyzed} jobs analysés avec batch processing")

# ============================================================================
# ÉTAPE 3 & 4 : NEWS & INTERVIEWS - PARALLEL PROCESSING
# ============================================================================

async def search_with_perplexity_async(
    session: aiohttp.ClientSession,
    company_name: str,
    company_website: str,
    search_type: str
) -> Optional[Dict[str, Any]]:
    """Recherche avec Perplexity de façon asynchrone"""
    
    if search_type == "news":
        print(f"📰 {company_name} - Recherche news (ASYNC)...")
        prompt = f"""Search the web for recent news articles about {company_name} from 2024-2026.

TOPICS: E-commerce growth, digital transformation, product catalog, AI adoption, 
visualization tech, product photography, customization, marketing campaigns, 
sustainability initiatives, new product launches, retail expansion.

Find 10-15 articles with REAL URLs. List each with:
- Title
- Source
- Complete URL
- Date
- Brief summary"""
    else:  # interviews
        print(f"🎤 {company_name} - Recherche interviews (ASYNC)...")
        prompt = f"""Search for executive interviews from {company_name} (2024-2026).

TARGET: CEO, CMO, CTO, VP Ecommerce, VP Digital, VP Marketing, 
Directeur Général, Directeur Marketing, Directeur Digital

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
                print(f"❌ {company_name} - Erreur Perplexity (status {response.status})")
                return None
            
            result = await response.json()
            
            if 'choices' not in result or len(result['choices']) == 0:
                return None
            
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            return {
                "raw_content": content,
                "citations": citations,
                "company_name": company_name,
                "search_type": search_type
            }
    
    except Exception as e:
        print(f"❌ {company_name} - Erreur: {e}")
        return None

async def structure_with_openai_async(perplexity_data: Dict) -> Optional[List]:
    """Structure les données avec OpenAI de façon asynchrone"""
    
    company_name = perplexity_data['company_name']
    raw_content = perplexity_data['raw_content']
    citations = perplexity_data['citations']
    search_type = perplexity_data['search_type']
    
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
      "category": "technology_innovation|ecommerce_growth|sustainability|product_launch|..."
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
        print(f"❌ {company_name} - Erreur OpenAI: {e}")
        return None

async def scrape_company_data_async(company_entry: Dict, search_type: str, session: aiohttp.ClientSession):
    """Scrape news ou interviews pour une entreprise de façon asynchrone"""
    company = company_entry['company']
    company_name = company['name']
    company_website = company['website']
    
    # Étape 1 : Perplexity
    perplexity_result = await search_with_perplexity_async(
        session, company_name, company_website, search_type
    )
    
    if not perplexity_result:
        return None
    
    # Étape 2 : OpenAI
    structured_data = await structure_with_openai_async(perplexity_result)
    
    if not structured_data:
        return None
    
    return {
        "company_name": company_name,
        "items": structured_data,
        "search_date": datetime.now().isoformat(),
        "success": True,
        "count": len(structured_data),
        "search_type": search_type
    }

async def scrape_news_and_interviews_async():
    """Scrape news et interviews pour toutes les entreprises en parallèle"""
    print_header("ÉTAPES 3 & 4 : NEWS & INTERVIEWS (Perplexity + OpenAI) - PARALLEL")
    
    # Charger jobs_data.json
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filtrer les entreprises cibles
    companies_to_scrape = []
    for company_entry in data['companies']:
        company_name = company_entry.get('company', {}).get('name', '')
        if company_name in TARGET_COMPANIES:
            companies_to_scrape.append(company_entry)
    
    print(f"🚀 Scraping PARALLEL de {len(companies_to_scrape)} entreprises")
    for company_entry in companies_to_scrape:
        print(f"  • {company_entry.get('company', {}).get('name', '')}")
    print()
    
    # Charger ou créer les fichiers de données
    news_path = 'company_news.json'
    if os.path.exists(news_path):
        with open(news_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    else:
        news_data = {}
    
    interviews_path = 'management_interviews.json'
    if os.path.exists(interviews_path):
        with open(interviews_path, 'r', encoding='utf-8') as f:
            interviews_data = json.load(f)
    else:
        interviews_data = {}
    
    # Configuration de session avec limitation de concurrence
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
    timeout = aiohttp.ClientTimeout(total=120)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Créer toutes les tâches (news + interviews) en parallèle
        tasks = []
        
        for company_entry in companies_to_scrape:
            # Tâche pour les news
            tasks.append(scrape_company_data_async(company_entry, "news", session))
            # Tâche pour les interviews
            tasks.append(scrape_company_data_async(company_entry, "interviews", session))
        
        print(f"⚡ Lancement de {len(tasks)} requêtes simultanées (news + interviews)...")
        start_time = time.time()
        
        # Exécuter toutes les tâches en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        print(f"✅ Scraping terminé en {elapsed:.2f}s")
    
    # Traiter les résultats
    news_count = 0
    interviews_count = 0
    
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Erreur: {result}")
            continue
        
        if not result:
            continue
        
        company_name = result['company_name']
        search_type = result['search_type']
        
        if search_type == "news":
            news_data[company_name] = {
                "company_name": company_name,
                "news_items": result['items'],
                "search_date": result['search_date'],
                "scrape_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "search_engine": "perplexity-sonar",
                    "structuring_model": "gpt-4o",
                    "success": True,
                    "articles_found": result['count']
                }
            }
            news_count += result['count']
            print(f"✅ {company_name} - News: {result['count']} articles")
        
        else:  # interviews
            interviews_data[company_name] = {
                "company_name": company_name,
                "interviews": result['items'],
                "search_date": result['search_date'],
                "scrape_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "search_engine": "perplexity-sonar",
                    "structuring_model": "gpt-4o",
                    "success": True,
                    "interviews_found": result['count']
                }
            }
            interviews_count += result['count']
            print(f"✅ {company_name} - Interviews: {result['count']} interviews")
    
    # Sauvegarder les résultats
    with open(news_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    with open(interviews_path, 'w', encoding='utf-8') as f:
        json.dump(interviews_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎯 Résultats : {news_count} articles de news, {interviews_count} interviews")

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
    
    # Convertir jobs_data.json vers public/jobs_analysis.json
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
            "industry": company.get('industry', 'Retail'),
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
# MAIN OPTIMISÉ
# ============================================================================

async def main():
    start_time = datetime.now()
    
    print("\n" + "="*80)
    print("🚀 SCRAPING ULTRA-RAPIDE - LE CREUSET & NATURE & DÉCOUVERTES")
    print("="*80)
    print(f"🕒 Démarrage : {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("🏢 Entreprises cibles :")
    for company in TARGET_COMPANIES:
        print(f"  • {company}")
    print(f"⚡ Configuration optimisée :")
    print(f"  • Max requêtes simultanées : {MAX_CONCURRENT_REQUESTS}")
    print(f"  • Taille des batches : {BATCH_SIZE}")
    print(f"  • Workers max : {MAX_WORKERS}")
    print("="*80)
    
    try:
        # ÉTAPE 1 : Scraping des jobs (ASYNC)
        await scrape_jobs_for_target_companies_async()
        
        # ÉTAPE 2 : Analyse des jobs (BATCH)
        await analyze_all_jobs_async()
        
        # ÉTAPES 3 & 4 : News et Interviews (PARALLEL)
        await scrape_news_and_interviews_async()
        
        # ÉTAPE 5 : Mise à jour frontend
        update_frontend()
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        return
    
    # Résumé final
    elapsed_time = datetime.now() - start_time
    print("\n" + "="*80)
    print("🎉 PROCESSUS ULTRA-RAPIDE TERMINÉ")
    print("="*80)
    print(f"⚡ Durée totale : {elapsed_time}")
    print(f"🚀 Optimisations utilisées :")
    print(f"  ✓ Scraping jobs en parallèle")
    print(f"  ✓ Analyse jobs par batch")
    print(f"  ✓ News + interviews simultanés")
    print(f"  ✓ Workers asynchrones")
    print("\n📁 Fichiers générés/mis à jour :")
    print("   ✓ database/jobs_data.json")
    print("   ✓ database/company_news.json")
    print("   ✓ database/management_interviews.json")
    print("   ✓ public/jobs_analysis.json")
    print("   ✓ public/news_data.json")
    print("   ✓ public/management_interviews.json")
    print("\n🎨 Les nouvelles données sont maintenant disponibles dans l'application !")
    print("="*80 + "\n")

if __name__ == "__main__":
    # Configuration pour optimiser les performances
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    asyncio.run(main())