#!/usr/bin/env python3
"""
Script pour analyser les jobs manquants des entreprises de Jerrica's accounts
"""

import json
import asyncio
import sys
import os
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv

sys.stdout.reconfigure(line_buffering=True)

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

NUM_WORKERS = 20  # Augmenté à 20 workers pour aller plus vite
client = AsyncOpenAI(api_key=OPENAI_API_KEY, max_retries=2, timeout=30.0)

SYSTEM_PROMPT = """You are an expert at analyzing job descriptions to identify B2B commercial opportunities.

CONTEXT:
presti.ai is an AI tool that allows furniture/home decor companies to generate realistic photostaging/photoshoot images from their product photos.

OBJECTIVE:
Analyze the job description EXHAUSTIVELY to extract all relevant information, especially the tools ecosystem (tech stack).

IMPORTANT: 
- For each piece of information, include an exact quote from the description as evidence
- Extract broadly, do not filter aggressively
- If nothing is found for a field, leave an empty array []
- ALL insights must be written in ENGLISH

Respond ONLY with valid JSON:
{
    "relevance_score": 7,
    "value_proposition": {
        "efficiency_conversion": {
            "volume_scale": [{"insight": "...", "evidence": "...", "relevance": "..."}],
            "speed_time_to_market": [{"insight": "...", "evidence": "...", "relevance": "..."}],
            "conversion_revenue": [{"insight": "...", "evidence": "...", "relevance": "..."}]
        },
        "brand_creativity": {
            "brand_consistency": [{"insight": "...", "evidence": "...", "relevance": "..."}],
            "creative_direction": [{"insight": "...", "evidence": "...", "relevance": "..."}],
            "photography_staging": [{"insight": "...", "evidence": "...", "relevance": "..."}]
        }
    },
    "team_structure": {
        "marketing": {
            "key_decision_makers": [{"role": "...", "evidence": "..."}],
            "managers": [{"role": "...", "evidence": "..."}],
            "collaborators": [{"role": "...", "evidence": "..."}]
        },
        "ecommerce": {"key_decision_makers": [], "managers": [], "collaborators": []},
        "creative": {"key_decision_makers": [], "managers": [], "collaborators": []},
        "product": {"key_decision_makers": [], "managers": [], "collaborators": []},
        "sales": {"key_decision_makers": [], "managers": [], "collaborators": []},
        "other": {"key_decision_makers": [], "managers": [], "collaborators": []}
    },
    "tools_ecosystem": {
        "design_tools": [{"tool": "Photoshop", "evidence": "exact quote"}],
        "3d_tools": [{"tool": "Blender", "evidence": "exact quote"}],
        "ecommerce_platforms": [{"platform": "Shopify", "evidence": "exact quote"}]
    },
    "sales_recommendation": "recommended commercial approach"
}

TOOLS ECOSYSTEM EXTRACTION RULES:

1. DESIGN TOOLS (design_tools):
✅ EXTRACT: Photoshop, InDesign, Illustrator, Figma, Sketch, Adobe Creative Suite, Canva, Cloudinary, Bynder
❌ REJECT: Generic terms like "design tools"

2. 3D TOOLS (3d_tools):
✅ EXTRACT: Blender, Maya, 3DS Max, Cinema 4D, SketchUp, ZBrush
❌ REJECT: "3D renderings" (process, not tool), "3D modeling" (process)

3. E-COMMERCE PLATFORMS (ecommerce_platforms):
✅ EXTRACT: Shopify, Magento, WooCommerce, BigCommerce, Salesforce Commerce Cloud, Adobe Commerce
❌ REJECT: Company's own website, generic "our website"

CRITICAL: ONLY extract NAMED PRODUCTS/SOFTWARE, not processes or company websites."""


async def analyze_job(job_data, company_name, semaphore):
    """Analyse un job avec OpenAI"""
    
    async with semaphore:
        description = job_data.get('description', '')
        if not description or len(description) < 50:
            return None
        
        user_prompt = f"""Analyze this job posting for {company_name}.

JOB TITLE: {job_data.get('job_title', 'N/A')}
LOCATION: {job_data.get('location', 'N/A')}

DESCRIPTION:
{description}

Extract all relevant information, especially tools_ecosystem (tech stack).
Respond ONLY with valid JSON."""
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=60.0
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
        
        except Exception as e:
            print(f"    ❌ Erreur: {str(e)[:50]}")
            return None


def normalize_name(name):
    """Normalise le nom de l'entreprise"""
    return name.lower().replace(',', '').replace('.', '').replace('-', ' ').replace('&', 'and').strip()


async def analyze_missing_jobs():
    """Analyse les jobs manquants pour les entreprises de Jerrica's accounts"""
    
    # Liste des entreprises de Jerrica's accounts
    jerrica_accounts = [
        "La-Z-Boy", "Williams Sonoma", "Millerknoll", "Palliser Furniture Ltd.",
        "Rooms to Go", "Article", "American Leather", "Serena & Lily",
        "Anthropologie Home", "Rowe Furniture", "Room & Board", "Bassett Furniture",
        "Living Spaces", "Jonathan Louis", "Theodore Alexander", "Kimball International",
        "Ballard Designs", "Design Within Reach", "Saks Global", "Costco"
    ]
    
    # Charger data.json
    with open('../public/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    companies_normalized = {normalize_name(name): name for name in data['companies'].keys()}
    
    # Identifier les jobs à analyser
    jobs_to_analyze = []
    company_job_map = {}
    
    for company in jerrica_accounts:
        norm_name = normalize_name(company)
        data_name = companies_normalized.get(norm_name)
        
        if data_name:
            company_data = data['companies'][data_name]
            for i, job in enumerate(company_data['jobs']):
                if not job.get('analysis'):
                    jobs_to_analyze.append({
                        'company_key': data_name,
                        'job_index': i,
                        'job_data': job,
                        'company_name': company_data['name']
                    })
                    if data_name not in company_job_map:
                        company_job_map[data_name] = []
                    company_job_map[data_name].append(i)
    
    print(f"\n{'='*80}")
    print(f"🚀 ANALYSE DES JOBS MANQUANTS - JERRICA'S ACCOUNTS")
    print(f"{'='*80}")
    print(f"📊 {len(jobs_to_analyze)} jobs à analyser")
    print(f"🏢 {len(company_job_map)} entreprises concernées")
    print(f"👥 {NUM_WORKERS} workers en parallèle")
    print(f"{'='*80}\n")
    
    # Créer un semaphore pour limiter les requêtes simultanées
    semaphore = asyncio.Semaphore(NUM_WORKERS)
    
    # Analyser tous les jobs
    tasks = []
    for job_info in jobs_to_analyze:
        task = analyze_job(job_info['job_data'], job_info['company_name'], semaphore)
        tasks.append((job_info, task))
    
    analyzed_count = 0
    failed_count = 0
    total = len(tasks)
    
    print("Analyse en cours...\n")
    
    # Traiter par batch avec asyncio.gather
    batch_size = 50
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i+batch_size]
        batch_tasks = [task_coro for _, task_coro in batch]
        
        try:
            results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for idx, result in enumerate(results):
                job_info = batch[idx][0]
                
                if isinstance(result, Exception):
                    failed_count += 1
                    print(f"❌", end="", flush=True)
                elif result:
                    # Mettre à jour l'analyse dans data
                    data['companies'][job_info['company_key']]['jobs'][job_info['job_index']]['analysis'] = result
                    analyzed_count += 1
                    print(f"✓", end="", flush=True)
                else:
                    failed_count += 1
                    print(f".", end="", flush=True)
            
            # Sauvegarde après chaque batch
            with open('../public/data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f" [{analyzed_count}/{total}]")
            
        except Exception as e:
            print(f"\n❌ Erreur batch: {str(e)[:100]}")
            failed_count += len(batch)
    
    # Sauvegarde finale
    with open('../public/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n✅ Analyse terminée!")
    print(f"📁 Résultats sauvegardés dans ../public/data.json")
    print(f"\n📈 Statistiques:")
    print(f"   - Jobs analysés avec succès: {analyzed_count}/{total}")
    print(f"   - Jobs échoués: {failed_count}/{total}")
    print(f"   - Taux de succès: {analyzed_count*100/total:.1f}%")
    
    # Vérification par entreprise
    print(f"\n📊 Par entreprise:")
    for company_key, job_indices in company_job_map.items():
        company_data = data['companies'][company_key]
        analyzed = sum(1 for i in job_indices if company_data['jobs'][i].get('analysis'))
        print(f"   - {company_data['name']:40} | {analyzed}/{len(job_indices)} jobs analysés")


if __name__ == "__main__":
    asyncio.run(analyze_missing_jobs())
