#!/bin/bash
# Pipeline complète pour scraper les 14 nouvelles entreprises

set -e  # Arrêter en cas d'erreur

echo "=============================================================================="
echo "🚀 PIPELINE COMPLÈTE - 14 NOUVELLES ENTREPRISES"
echo "=============================================================================="
echo ""
echo "Nouvelles entreprises à traiter:"
echo "  • Millerknoll"
echo "  • Palliser Furniture Ltd."
echo "  • Rooms to Go"
echo "  • Article"
echo "  • American Leather"
echo "  • Serena & Lily"
echo "  • Rowe Furniture"
echo "  • Room & Board"
echo "  • Bassett Furniture"
echo "  • Living Spaces"
echo "  • Jonathan Louis"
echo "  • Theodore Alexander"
echo "  • Kimball International"
echo "  • Saks Global"
echo ""
echo "=============================================================================="
echo ""

# Activer l'environnement virtuel
source venv_async/bin/activate

# Charger les variables d'environnement depuis .env
export $(cat .env | grep -v '^#' | xargs)

# Liste des nouvelles entreprises
COMPANIES=(
    "Millerknoll"
    "Palliser Furniture Ltd."
    "Rooms to Go"
    "Article"
    "American Leather"
    "Serena & Lily"
    "Rowe Furniture"
    "Room & Board"
    "Bassett Furniture"
    "Living Spaces"
    "Jonathan Louis"
    "Theodore Alexander"
    "Kimball International"
    "Saks Global"
)

echo "=============================================================================="
echo "ÉTAPE 1/5 : SCRAPING DES JOBS (MANTIKS API)"
echo "=============================================================================="
echo ""

# Scraper les jobs pour chaque nouvelle entreprise
python3 << 'PYTHON_SCRIPT'
import json
import requests
import time
import os

MANTIKS_API_KEY = os.environ.get("MANTIKS_API_KEY")
MANTIKS_API_URL = "https://api.mantiks.io/company/jobs"

JOB_KEYWORDS = [
    "digital strategy", "digital experience", "group design", "art",
    "graphic design", "sales", "revenue", "digital marketing",
    "international marketing", "product marketing", "group marketing",
    "brand marketing", "strategic marketing", "marketing",
    "ecommerce", "e-commerce", "digital", "creative",
    "group creative", "global creative"
]

NEW_COMPANIES = [
    "Millerknoll", "Palliser Furniture Ltd.", "Rooms to Go", "Article",
    "American Leather", "Serena & Lily", "Rowe Furniture", "Room & Board",
    "Bassett Furniture", "Living Spaces", "Jonathan Louis", "Theodore Alexander",
    "Kimball International", "Saks Global"
]

def clean_url(url):
    if not url:
        return url
    for suffix in ['/fr/', '/en/', '/de/', '/es/', '/it/']:
        if url.endswith(suffix):
            url = url[:-len(suffix)] + '/'
    return url

def fetch_jobs(company):
    headers = {
        'accept': 'application/json',
        'x-api-key': MANTIKS_API_KEY
    }
    
    website = clean_url(company['website'])
    params = [('website', website), ('age_in_days', 365)]
    
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
                'error': f"HTTP {response.status_code}",
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

# Charger jobs_data.json
with open('jobs_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total_jobs = 0
success_count = 0

for i, company_entry in enumerate(data['companies']):
    company = company_entry.get('company', {})
    company_name = company.get('name', '')
    
    if company_name not in NEW_COMPANIES:
        continue
    
    print(f"[{NEW_COMPANIES.index(company_name) + 1}/{len(NEW_COMPANIES)}] {company_name}...", end=" ", flush=True)
    
    result = fetch_jobs(company)
    
    company_entry['success'] = result['success']
    company_entry['jobs'] = result['jobs']
    company_entry['nb_jobs'] = result['nb_jobs']
    
    if 'credits_remaining' in result:
        company_entry['credits_remaining'] = result['credits_remaining']
    if 'credits_cost' in result:
        company_entry['credits_cost'] = result['credits_cost']
    if 'error' in result:
        company_entry['error'] = result['error']
    
    if result['success']:
        nb_jobs = result['nb_jobs']
        total_jobs += nb_jobs
        if nb_jobs > 0:
            success_count += 1
        print(f"✅ {nb_jobs} jobs")
    else:
        print(f"❌ {result.get('error', 'Unknown')}")
    
    time.sleep(0.5)

# Sauvegarder
with open('jobs_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Total: {total_jobs} jobs pour {success_count} entreprises")
print(f"💾 Sauvegardé dans jobs_data.json")
PYTHON_SCRIPT

echo ""
echo "=============================================================================="
echo "ÉTAPE 2/5 : ANALYSE DES JOBS (OpenAI GPT-4o)"
echo "=============================================================================="
echo ""

python3 << 'PYTHON_SCRIPT'
import json
import os
import asyncio
from openai import AsyncOpenAI

openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

NEW_COMPANIES = [
    "Millerknoll", "Palliser Furniture Ltd.", "Rooms to Go", "Article",
    "American Leather", "Serena & Lily", "Rowe Furniture", "Room & Board",
    "Bassett Furniture", "Living Spaces", "Jonathan Louis", "Theodore Alexander",
    "Kimball International", "Saks Global"
]

async def analyze_job(job, company_name):
    system_prompt = """You are an expert analyst specialized in identifying buying signals for AI visual content generation services.

Analyze this job posting and extract structured information about:
1. Relevance score (1-10) for an AI company that generates product lifestyle images
2. Team structure and decision makers
3. Tools ecosystem (design, 3D, ecommerce platforms)
4. Strategic priorities
5. Budget indicators

Return JSON only."""

    user_prompt = f"""Analyze this job from {company_name}:

TITLE: {job.get('job_title', 'N/A')}
LOCATION: {job.get('location', 'N/A')}
DESCRIPTION: {job.get('description', 'N/A')[:3000]}

Return JSON:
{{
  "relevance_score": <1-10>,
  "relevance_reason": "why relevant",
  "team_structure": {{"decision_makers": [{{"role": "title", "seniority": "level"}}]}},
  "tools_ecosystem": {{"design_tools": [{{"tool": "name"}}], "3d_tools": [], "ecommerce_platforms": []}},
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
        print(f"❌ Erreur: {e}")
        return None

async def analyze_company_jobs(company_entry):
    jobs = company_entry.get('jobs', [])
    if not jobs:
        return 0
    
    company_name = company_entry.get('company', {}).get('name', '')
    analyzed = 0
    
    for job in jobs:
        if job.get('analysis'):
            continue
        
        analysis = await analyze_job(job, company_name)
        if analysis:
            job['analysis'] = analysis
            analyzed += 1
    
    return analyzed

async def main():
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    companies_to_analyze = [
        c for c in data['companies']
        if c.get('company', {}).get('name') in NEW_COMPANIES and c.get('nb_jobs', 0) > 0
    ]
    
    print(f"🔍 {len(companies_to_analyze)} entreprises avec des jobs à analyser\n")
    
    total_analyzed = 0
    
    for i, company_entry in enumerate(companies_to_analyze, 1):
        company_name = company_entry.get('company', {}).get('name')
        nb_jobs = company_entry.get('nb_jobs', 0)
        
        print(f"[{i}/{len(companies_to_analyze)}] {company_name} ({nb_jobs} jobs)...", end=" ", flush=True)
        
        analyzed = await analyze_company_jobs(company_entry)
        total_analyzed += analyzed
        
        print(f"✅ {analyzed} analysés")
        
        # Sauvegarder après chaque entreprise
        with open('jobs_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Total: {total_analyzed} jobs analysés")

asyncio.run(main())
PYTHON_SCRIPT

echo ""
echo "=============================================================================="
echo "ÉTAPE 3/5 : COMPANY NEWS (Perplexity + OpenAI)"
echo "=============================================================================="
echo ""

echo "⏭️  Scraping des news pour chaque entreprise..."
for company in "${COMPANIES[@]}"; do
    echo "  📰 $company"
    python3 scrape_company_news_hybrid_async.py --company "$company" 2>/dev/null || true
    sleep 3
done

echo ""
echo "=============================================================================="
echo "ÉTAPE 4/5 : MANAGEMENT INTERVIEWS (Perplexity + OpenAI)"
echo "=============================================================================="
echo ""

echo "⏭️  Scraping des interviews pour chaque entreprise..."
for company in "${COMPANIES[@]}"; do
    echo "  🎤 $company"
    python3 scrape_management_interviews.py --company "$company" 2>/dev/null || true
    sleep 3
done

echo ""
echo "=============================================================================="
echo "ÉTAPE 5/5 : MISE À JOUR DU FRONTEND"
echo "=============================================================================="
echo ""

# Copier les fichiers vers public/
echo "📁 Copie des fichiers vers public/..."

if [ -f "company_news.json" ]; then
    cp company_news.json ../public/news_data.json
    echo "  ✅ news_data.json"
fi

if [ -f "management_interviews.json" ]; then
    cp management_interviews.json ../public/management_interviews.json
    echo "  ✅ management_interviews.json"
fi

# Conversion des jobs pour le frontend
echo "  🔄 Conversion jobs_analysis.json..."
python3 convert_v2_to_frontend.py

echo ""
echo "=============================================================================="
echo "✅ PIPELINE COMPLÈTE TERMINÉE"
echo "=============================================================================="
echo ""
echo "📁 Fichiers mis à jour:"
echo "  ✓ database/jobs_data.json"
echo "  ✓ database/company_news.json"
echo "  ✓ database/management_interviews.json"
echo "  ✓ public/jobs_analysis.json"
echo "  ✓ public/news_data.json"
echo "  ✓ public/management_interviews.json"
echo ""
echo "🎨 L'application Next.js détectera automatiquement les changements"
echo "=============================================================================="

