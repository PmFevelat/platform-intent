#!/usr/bin/env python3
"""
Script d'analyse des tendances sur 3 mois
Objectif : Détecter des signaux d'intention d'achat à partir des offres d'emploi
pour positionner presti.ai
"""

import json
import asyncio
import sys
import os
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from collections import defaultdict
from dotenv import load_dotenv

sys.stdout.reconfigure(line_buffering=True)

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

NUM_WORKERS = 4
OUTPUT_FILE = "jobs_trends_analysis.json"

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an expert at analyzing hiring trends to identify business buying signals.

CONTEXT:
presti.ai is an AI tool that allows furniture/home decor companies to generate realistic photostaging/photoshoot images from their product photos.

Target personas:
- Marketing / Brand teams
- E-commerce / Digital teams
- Creative / Content / Design teams
- Retail / Merchandising teams

OBJECTIVE:
Analyze ALL job postings for a company over the last 3 months to detect TRENDS and buying signals.
DO NOT analyze each job separately - look for patterns, evolution, and emerging themes.

Focus on 2 major categories:

A. DIGITAL GROWTH & PRODUCT STRATEGY
Signals: e-commerce expansion, digital transformation, product launches, merchandising
Keywords: site redesign, scaling, internationalization, e-commerce growth, new collections, product launches, seasonal campaigns, digital marketing, CRO, product marketing

B. VISUAL CONTENT & CREATIVE PRODUCTION
Signals: roles related to visual creation, content, design, brand, photography
Keywords: photos, visuals, assets, catalogs, product pages, content production, brand imagery, creative direction, photoshoots, 3D rendering

For each category, identify:
- EVOLUTION: increase/decrease in job volume, changing focus areas
- NEW THEMES: emerging topics that weren't mentioned before
- HIRING VELOCITY: sudden acceleration in specific areas

IMPORTANT: All analysis must be in ENGLISH.

Respond ONLY with valid JSON using this structure:
{
    "company_name": "company name",
    "analysis_period": {
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "total_jobs": <number>
    },
    "overall_signal_strength": <1-10>,
    "overall_summary": "1-2 concise sentences highlighting the main buying signal detected",
    
    "trends": {
        "digital_growth_product": {
            "signal_strength": <1-10>,
            "job_count": <number>,
            "key_roles": ["list of relevant job titles"],
            "evolution": "description of evolution/changes over time",
            "new_themes": ["list of new themes appearing"],
            "hiring_velocity": "slow/moderate/fast/accelerating",
            "evidence": ["key quotes from job descriptions"]
        },
        "visual_content_creative": {
            "signal_strength": <1-10>,
            "job_count": <number>,
            "key_roles": ["list of relevant job titles"],
            "evolution": "description of evolution/changes over time",
            "new_themes": ["list of new themes appearing"],
            "hiring_velocity": "slow/moderate/fast/accelerating",
            "evidence": ["key quotes from job descriptions"]
        }
    }
}"""

USER_PROMPT_TEMPLATE = """Analyze the hiring trends for {company_name} over the last 3 months.

COMPANY INFO:
- Industry: {industry}
- Size: {employees}

ALL JOB POSTINGS ({job_count} total):

{jobs_summary}

Analyze these jobs collectively to detect trends and buying signals in the 2 categories:
A. Digital Growth & Product Strategy (e-commerce, digital transformation, product launches, merchandising)
B. Visual Content & Creative Production (visuals, content, design, photography, brand)

Look for patterns, evolution, and emerging themes that indicate business initiatives."""


async def analyze_company_trends(company_data, semaphore):
    """Analyse les tendances d'embauche pour une entreprise"""
    async with semaphore:
        try:
            company_info = company_data['company']
            jobs = company_data.get('jobs', [])
            
            if not jobs:
                return {
                    'success': False,
                    'company_name': company_info['name'],
                    'error': 'No jobs to analyze'
                }
            
            # Préparer un résumé de tous les jobs
            jobs_summary = []
            for i, job in enumerate(jobs, 1):
                job_date = job.get('date_creation', '')[:10] if job.get('date_creation') else 'Unknown'
                jobs_summary.append(
                    f"\n--- JOB {i} ---\n"
                    f"Title: {job.get('job_title', 'N/A')}\n"
                    f"Location: {job.get('location', 'N/A')}\n"
                    f"Date: {job_date}\n"
                    f"Description: {job.get('description', 'N/A')[:1500]}...\n"
                )
            
            user_prompt = USER_PROMPT_TEMPLATE.format(
                company_name=company_info['name'],
                industry=company_info['industry'],
                employees=company_info['employees'],
                job_count=len(jobs),
                jobs_summary='\n'.join(jobs_summary[:20])  # Limite pour éviter de dépasser le token limit
            )
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                'success': True,
                'company_name': company_info['name'],
                'analysis': analysis,
                'tokens': response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                'success': False,
                'company_name': company_data['company']['name'],
                'error': str(e),
                'analysis': None
            }


async def process_all_companies(data, output_file):
    """Traite toutes les entreprises avec sauvegarde incrémentale"""
    semaphore = asyncio.Semaphore(NUM_WORKERS)
    
    # Charger les résultats existants
    results = {}
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        print(f"✓ {len(results)} analyses déjà complétées")
    
    # Filtrer les entreprises avec des jobs
    companies_with_jobs = [
        c for c in data['companies'] 
        if c.get('success') and c.get('nb_jobs', 0) > 0
    ]
    
    total = len(companies_with_jobs)
    completed = len(results)
    total_tokens = 0
    
    print(f"\n🚀 Démarrage de l'analyse des tendances")
    print(f"📊 {total} entreprises avec des offres d'emploi")
    print(f"⚙️  Workers : {NUM_WORKERS}")
    print(f"💾 Sauvegarde : {output_file}\n")
    
    tasks = []
    company_names = []
    
    for company_data in companies_with_jobs:
        company_name = company_data['company']['name']
        if company_name not in results:
            tasks.append(analyze_company_trends(company_data, semaphore))
            company_names.append(company_name)
    
    if not tasks:
        print("✅ Toutes les analyses sont déjà complétées !")
        return results
    
    # Process companies
    for i, task in enumerate(asyncio.as_completed(tasks)):
        result = await task
        
        if result['success']:
            results[result['company_name']] = {
                'analyzed_at': datetime.now().isoformat(),
                'analysis': result['analysis']
            }
            total_tokens += result['tokens']
            completed += 1
            
            # Sauvegarde incrémentale toutes les 2 analyses
            if completed % 2 == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
            
            signal = result['analysis'].get('overall_signal_strength', 0)
            job_count = result['analysis']['analysis_period'].get('total_jobs', 0)
            print(f"[{completed}/{total}] ✓ {result['company_name'][:35]:35} | Jobs: {job_count:3} | Signal: {signal}/10 | Tokens: {total_tokens:,}")
        else:
            print(f"[{completed}/{total}] ✗ {result['company_name'][:35]:35} | Erreur: {result.get('error', 'Unknown')[:50]}")
    
    # Sauvegarde finale
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Analyse des tendances terminée !")
    print(f"📊 Total tokens utilisés : {total_tokens:,}")
    print(f"💰 Coût estimé : ${(total_tokens / 1000000) * 0.15:.2f}")
    
    return results


async def main():
    print("=" * 70)
    print("🎯 presti.ai - Analyse des Tendances sur 3 mois")
    print("=" * 70)
    
    # Charger les données
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n📁 {len(data['companies'])} entreprises chargées")
    
    await process_all_companies(data, OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(main())

