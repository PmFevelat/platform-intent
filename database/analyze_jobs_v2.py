#!/usr/bin/env python3
"""
Script d'analyse V2 - Approche exhaustive et structurée
Extraction large avec organisation intelligente
"""

import json
import asyncio
import sys
import os
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv

sys.stdout.reconfigure(line_buffering=True)

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

NUM_WORKERS = 25
OUTPUT_FILE = "jobs_analysis_v2.json"

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You are an expert at analyzing job descriptions to identify B2B commercial opportunities.

CONTEXT:
presti.ai is an AI tool that allows furniture/home decor companies to generate realistic photostaging/photoshoot images from their product photos.

Value proposition:
- Generate images with intact products (no deformation)
- Respect brand identity and visual consistency
- Produce at scale across entire catalog
- Speed of production and iteration
- Reduce photo production costs
- Improve e-commerce conversion through better images

OBJECTIVE:
Analyze the job description EXHAUSTIVELY to extract all relevant information. Be generous in extraction - better to include than exclude.

IMPORTANT: 
- For each piece of information, include an exact quote from the description as evidence
- Extract broadly, do not filter aggressively
- If nothing is found for a field, leave an empty array []
- ALL insights, relevance explanations, and recommendations must be written in ENGLISH

Respond ONLY with valid JSON using this structure:
{
    "relevance_score": <1-10>,
    
    "value_proposition": {
        "efficiency_conversion": {
            "volume_scale": [
                {"insight": "challenge identified related to volume/scale/catalog", "evidence": "exact quote", "relevance": "why this is relevant for presti"}
            ],
            "speed_time_to_market": [
                {"insight": "challenge related to speed/deadlines/launches", "evidence": "exact quote", "relevance": "why this is relevant for presti"}
            ],
            "conversion_revenue": [
                {"insight": "challenge related to conversion/sales/user experience", "evidence": "exact quote", "relevance": "why this is relevant for presti"}
            ]
        },
        "brand_creativity": {
            "brand_consistency": [
                {"insight": "challenge related to brand consistency/visual quality", "evidence": "exact quote", "relevance": "why this is relevant for presti"}
            ],
            "creative_direction": [
                {"insight": "challenge related to creative direction/image production", "evidence": "exact quote", "relevance": "why this is relevant for presti"}
            ],
            "photography_staging": [
                {"insight": "challenge related to photography/staging/3D rendering", "evidence": "exact quote", "relevance": "why this is relevant for presti"}
            ]
        }
    },
    
    "team_structure": {
        "marketing": {
            "key_decision_makers": [{"role": "exact title", "evidence": "quote with 'reports to' or 'manages'"}],
            "managers": [{"role": "exact title", "evidence": "quote"}],
            "collaborators": [{"role": "exact title", "evidence": "quote mentioning collaboration"}]
        },
        "ecommerce": {
            "key_decision_makers": [{"role": "exact title", "evidence": "quote"}],
            "managers": [{"role": "exact title", "evidence": "quote"}],
            "collaborators": [{"role": "exact title", "evidence": "quote"}]
        },
        "creative": {
            "key_decision_makers": [{"role": "exact title", "evidence": "quote"}],
            "managers": [{"role": "exact title", "evidence": "quote"}],
            "collaborators": [{"role": "exact title", "evidence": "quote"}]
        },
        "product": {
            "key_decision_makers": [{"role": "exact title", "evidence": "quote"}],
            "managers": [{"role": "exact title", "evidence": "quote"}],
            "collaborators": [{"role": "exact title", "evidence": "quote"}]
        },
        "sales": {
            "key_decision_makers": [{"role": "exact title", "evidence": "quote"}],
            "managers": [{"role": "exact title", "evidence": "quote"}],
            "collaborators": [{"role": "exact title", "evidence": "quote"}]
        },
        "other": {
            "key_decision_makers": [{"role": "exact title", "evidence": "quote"}],
            "managers": [{"role": "exact title", "evidence": "quote"}],
            "collaborators": [{"role": "exact title", "evidence": "quote"}]
        }
    },
    
    "tools_ecosystem": {
        "design_tools": [{"tool": "specific software name", "evidence": "exact quote"}],
        "3d_tools": [{"tool": "specific 3D software name", "evidence": "exact quote"}],
        "ecommerce_platforms": [{"platform": "specific platform name", "evidence": "exact quote"}]
    },
    
    "sales_recommendation": "recommended commercial approach in 2-3 sentences based on insights found"
}

EXTRACTION RULES:

VALUE PROPOSITION:
✅ Extract EVERYTHING mentioning: production, volume, scale, speed, launch, conversion, revenue, brand, visual, creative, photography, staging, imagery, 3D, rendering, catalog, SKU, product presentation, quality, consistency, art direction, etc.
✅ Include missions and pain points
❌ Only reject: external relationships (retailers, influencers), pure HR/finance issues, mentions too vague without context

TEAM STRUCTURE:
✅ Extract ALL mentioned job titles and teams
✅ Identify hierarchical relationships ("reports to", "manages team of")
✅ Identify cross-team collaborations ("work with", "partner with", "collaborate with")
❌ Only reject: external relationships, "leadership" without precision

TOOLS ECOSYSTEM - BE VERY PRECISE:

1. DESIGN TOOLS (design_tools):
✅ EXTRACT: Specific design software names
   Examples: Photoshop, InDesign, Illustrator, Figma, Sketch, Adobe Creative Suite, Canva, DAM platforms (Cloudinary, Bynder, etc.)
❌ REJECT: Generic terms like "design tools", "creative software"

2. 3D TOOLS (3d_tools):
✅ EXTRACT: Specific 3D software names ONLY
   Examples: Blender, Maya, 3DS Max, Cinema 4D, SketchUp, ZBrush
❌ REJECT: 
   - "3D renderings" (this is a process/output, NOT a tool)
   - "3D modeling" (this is a process, NOT a tool)
   - Generic terms without software names

3. E-COMMERCE PLATFORMS (ecommerce_platforms):
✅ EXTRACT: External e-commerce platforms and systems
   Examples: Shopify, Magento, WooCommerce, Amazon (as platform), Wayfair (as platform), BigCommerce, Salesforce Commerce Cloud, Adobe Commerce, Contentful, PIM systems, DAM systems
❌ REJECT:
   - The company's own website (e.g., if working for Ashley, DON'T extract "AshleyFurniture.com" or "Ashley.com")
   - Generic mentions like "our website", "our ecommerce site"
   - URLs ending in the company's domain name

CRITICAL RULES:
- ONLY extract tools/platforms that are NAMED PRODUCTS/SOFTWARE
- If it's a process, method, or technique → DON'T extract it
- If it's the company's own website/app → DON'T extract it
- If you're unsure whether it's a specific tool → DON'T extract it
❌ Also reject: CRM (Salesforce, HubSpot), Microsoft Office, Jira, Slack, HR/finance tools
"""

USER_PROMPT = """Analyse cette description de poste de manière EXHAUSTIVE :

ENTREPRISE: {company}
TITRE: {title}
LOCALISATION: {location}

DESCRIPTION COMPLÈTE:
{description}

Extrais toutes les informations pertinentes avec des citations exactes comme preuves. Sois généreux dans l'extraction."""


async def analyze_job(job_data, semaphore):
    """Analyse un job avec OpenAI"""
    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT.format(
                        company=job_data['company_name'],
                        title=job_data['job_title'],
                        location=job_data.get('location', 'N/A'),
                        description=job_data['description'][:12000]
                    )}
                ],
                temperature=0.2,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'analysis': analysis,
                'tokens': response.usage.total_tokens
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'analysis': None}


async def process_and_save(jobs, output_file):
    """Traite tous les jobs avec sauvegarde incrémentale"""
    semaphore = asyncio.Semaphore(NUM_WORKERS)
    
    # Charger les résultats existants
    results = {}
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        print(f"✓ {len(results)} analyses déjà complétées")
    
    total = len(jobs)
    completed = len(results)
    total_tokens = 0
    
    print(f"\n🚀 Démarrage de l'analyse : {total - completed} jobs à traiter")
    print(f"⚙️  Workers : {NUM_WORKERS}")
    print(f"💾 Sauvegarde : {output_file}\n")
    
    tasks = []
    job_keys = []
    
    for job in jobs:
        job_key = f"{job['company_name']}_{job['job_title']}"
        if job_key not in results:
            tasks.append(analyze_job(job, semaphore))
            job_keys.append((job_key, job))
    
    if not tasks:
        print("✅ Toutes les analyses sont déjà complétées !")
        return results
    
    # Process jobs
    for i, task in enumerate(asyncio.as_completed(tasks)):
        result = await task
        job_key, job = job_keys[i]
        
        if result['success']:
            results[job_key] = {
                **job,
                'analysis': result['analysis'],
                'analyzed_at': datetime.now().isoformat()
            }
            total_tokens += result['tokens']
            completed += 1
            
            # Sauvegarde incrémentale toutes les 5 analyses
            if completed % 5 == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
            
            score = result['analysis'].get('relevance_score', 0)
            print(f"[{completed}/{total}] ✓ {job['company_name'][:25]:25} | {job['job_title'][:40]:40} | Score: {score}/10 | Tokens: {total_tokens:,}")
        else:
            print(f"[{completed}/{total}] ✗ {job['company_name'][:25]:25} | {job['job_title'][:40]:40} | Erreur: {result['error']}")
    
    # Sauvegarde finale
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Analyse terminée !")
    print(f"📊 Total tokens utilisés : {total_tokens:,}")
    print(f"💰 Coût estimé : ${(total_tokens / 1000000) * 0.15:.2f}")
    
    return results


async def main():
    # Charger les données
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jobs = []
    for company_data in data['companies']:
        if not company_data.get('jobs'):
            continue
        
        company_info = company_data['company']
        for job in company_data['jobs']:
            jobs.append({
                'company_name': company_info['name'],
                'company_website': company_info.get('website', ''),
                'company_linkedin': company_info.get('linkedin', ''),
                **job
            })
    
    print(f"📁 {len(jobs)} offres d'emploi chargées")
    
    await process_and_save(jobs, OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(main())

