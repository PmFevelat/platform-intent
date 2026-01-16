#!/usr/bin/env python3
"""
Script ASYNC pour scraper les 4 entreprises Pet Care
Utilise les mêmes méthodes que les autres entreprises (workers async)
"""

import json
import os
import asyncio
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

MANTIKS_API_KEY = os.environ.get("MANTIKS_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
MANTIKS_API_URL = "https://api.mantiks.io/company/jobs"

PET_CARE_COMPANIES = [
    {"name": "Chewy", "website": "https://www.chewy.com/", "linkedin": "https://www.linkedin.com/company/chewy-com/"},
    {"name": "Petco", "website": "https://www.petco.com/shop/en/petcostore", "linkedin": "https://www.linkedin.com/company/petco/"},
    {"name": "Petmate", "website": "https://www.petmate.com/", "linkedin": "https://www.linkedin.com/company/petmate/"},
    {"name": "Petsmart", "website": "https://www.petsmart.com/", "linkedin": "https://www.linkedin.com/company/petsmart/"}
]

JOB_KEYWORDS = [
    "digital strategy", "digital experience", "group design", "art",
    "graphic design", "digital marketing", "product marketing", 
    "brand marketing", "marketing", "ecommerce", "e-commerce", 
    "digital", "creative", "product photography", "visual content"
]

print("🐾 SCRAPING ASYNC - PET CARE COMPANIES")
print("="*70)
print(f"🕐 Démarrage: {datetime.now().strftime('%H:%M:%S')}\n")

# ÉTAPE 1: Scraping Jobs (Mantiks)
print("📋 ÉTAPE 1/2: Scraping des jobs (Mantiks API)")
print("-"*70)

jobs_data = {}

for i, company in enumerate(PET_CARE_COMPANIES, 1):
    print(f"[{i}/4] {company['name']}...", end=" ", flush=True)
    
    headers = {'accept': 'application/json', 'x-api-key': MANTIKS_API_KEY}
    params = [('website', company['website']), ('age_in_days', 365)]
    for kw in JOB_KEYWORDS:
        params.append(('keyword', kw))
    if company.get('linkedin'):
        params.append(('linkedin_url', company['linkedin']))
    
    try:
        response = requests.get(MANTIKS_API_URL, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            jobs_data[company['name']] = {
                'company': company,
                'jobs': jobs,
                'nb_jobs': len(jobs)
            }
            print(f"✅ {len(jobs)} jobs")
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            jobs_data[company['name']] = {'company': company, 'jobs': [], 'nb_jobs': 0}
    except Exception as e:
        print(f"❌ {str(e)[:50]}")
        jobs_data[company['name']] = {'company': company, 'jobs': [], 'nb_jobs': 0}
    
    time.sleep(0.5)

total_jobs = sum(d['nb_jobs'] for d in jobs_data.values())
print(f"\n✅ Total: {total_jobs} jobs récupérés\n")

# ÉTAPE 2: Analyse Jobs (OpenAI async avec workers)
print("🤖 ÉTAPE 2/2: Analyse des jobs (OpenAI GPT-4o async)")
print("-"*70)

async def analyze_job(job, company_name, semaphore):
    """Analyse un job avec OpenAI (async avec semaphore pour limiter concurrence)"""
    async with semaphore:
        system_prompt = """You are an expert at analyzing job postings for AI visual content companies.
Extract: relevance score (1-10), decision makers, tools, priorities, budget indicators.
Return JSON only."""
        
        user_prompt = f"""Analyze this {company_name} job:

TITLE: {job.get('job_title', 'N/A')}
LOCATION: {job.get('location', 'N/A')}
DESCRIPTION: {job.get('description', 'N/A')[:3000]}

Return JSON:
{{
  "relevance_score": <1-10>,
  "relevance_reason": "why relevant",
  "team_structure": {{"decision_makers": [{{"role": "title", "seniority": "level"}}]}},
  "tools_ecosystem": {{"design_tools": [], "3d_tools": [], "ecommerce_platforms": []}},
  "strategic_priorities": [{{"priority": "name", "urgency": "level"}}],
  "budget_indicators": {{"salary_range": "", "team_expansion": "", "investment_signals": []}}
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
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return None

async def analyze_company(company_name, company_data):
    """Analyse tous les jobs d'une entreprise en parallèle"""
    jobs = company_data['jobs']
    if not jobs:
        return 0
    
    semaphore = asyncio.Semaphore(10)  # Max 10 requêtes en parallèle
    tasks = [analyze_job(job, company_name, semaphore) for job in jobs]
    
    results = await asyncio.gather(*tasks)
    
    analyzed_count = 0
    for job, analysis in zip(jobs, results):
        if analysis:
            job['analysis'] = analysis
            analyzed_count += 1
    
    return analyzed_count

async def analyze_all():
    total = 0
    for i, (company_name, company_data) in enumerate(jobs_data.items(), 1):
        nb_jobs = company_data['nb_jobs']
        if nb_jobs == 0:
            print(f"[{i}/4] {company_name}: ⏭️  pas de jobs")
            continue
        
        print(f"[{i}/4] {company_name} ({nb_jobs} jobs)...", end=" ", flush=True)
        analyzed = await analyze_company(company_name, company_data)
        total += analyzed
        print(f"✅ {analyzed} analysés")
    
    return total

loop = asyncio.get_event_loop()
analyzed_total = loop.run_until_complete(analyze_all())

print(f"\n✅ Total: {analyzed_total} jobs analysés\n")

# ÉTAPE 3: Mise à jour data.json
print("💾 Mise à jour de public/data.json...")
print("-"*70)

data_path = '../public/data.json'
with open(data_path, 'r', encoding='utf-8') as f:
    frontend_data = json.load(f)

for company_name, company_data in jobs_data.items():
    company_key = company_name.lower()
    if company_key in frontend_data['companies']:
        frontend_data['companies'][company_key]['jobs'] = company_data['jobs']
        print(f"✅ {company_name}: {company_data['nb_jobs']} jobs ajoutés")

frontend_data['metadata']['last_updated'] = datetime.now().isoformat()
frontend_data['metadata']['total_jobs'] = sum(
    len(c.get('jobs', [])) for c in frontend_data['companies'].values()
)

with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(frontend_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ data.json mis à jour!")

# Résumé
print("\n" + "="*70)
print("🎉 SCRAPING TERMINÉ")
print("="*70)
print(f"⏱️  Durée: {datetime.now().strftime('%H:%M:%S')}")
print(f"📊 Jobs: {total_jobs} récupérés, {analyzed_total} analysés")
print("📁 Fichiers mis à jour: public/data.json")
print("\n🚀 Les entreprises Pet Care sont maintenant dans l'interface!")
print("="*70)
