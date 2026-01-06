#!/usr/bin/env python3
"""
Script de test pour analyser une seule entreprise (California Closets)
"""

import json
import asyncio
import sys
import os
from datetime import datetime
from openai import AsyncOpenAI

sys.stdout.reconfigure(line_buffering=True)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

OUTPUT_FILE = "california_closets_test.json"
TARGET_COMPANY = "California Closets"

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


async def analyze_company_trends(company_data):
    """Analyse les tendances d'embauche pour California Closets"""
    try:
        company_info = company_data['company']
        jobs = company_data.get('jobs', [])
        
        if not jobs:
            print(f"❌ No jobs found for {company_info['name']}")
            return None
        
        print(f"\n📊 Analyzing {company_info['name']}")
        print(f"   Industry: {company_info['industry']}")
        print(f"   Employees: {company_info['employees']}")
        print(f"   Jobs to analyze: {len(jobs)}")
        print()
        
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
            jobs_summary='\n'.join(jobs_summary)
        )
        
        print("🤖 Sending to GPT-4o-mini for analysis...")
        print(f"   Prompt size: {len(user_prompt)} characters")
        print()
        
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
        tokens_used = response.usage.total_tokens
        
        print(f"✅ Analysis complete!")
        print(f"   Tokens used: {tokens_used:,}")
        print(f"   Overall signal strength: {analysis.get('overall_signal_strength', 0)}/10")
        print()
        
        return {
            'success': True,
            'company_name': company_info['name'],
            'analysis': analysis,
            'tokens': tokens_used
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            'success': False,
            'company_name': company_data['company']['name'],
            'error': str(e),
            'analysis': None
        }


async def main():
    print("=" * 70)
    print("🎯 PRESTI.AI - TEST ANALYSIS FOR CALIFORNIA CLOSETS")
    print("=" * 70)
    
    # Charger les données
    print("\n📂 Loading data from jobs_data.json...")
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Trouver California Closets
    target_company_data = None
    for company_data in data['companies']:
        if company_data['company']['name'] == TARGET_COMPANY:
            target_company_data = company_data
            break
    
    if not target_company_data:
        print(f"❌ Company '{TARGET_COMPANY}' not found in data!")
        print("\nAvailable companies:")
        for c in data['companies'][:10]:
            print(f"   - {c['company']['name']}")
        return
    
    if not target_company_data.get('jobs'):
        print(f"❌ No jobs found for {TARGET_COMPANY}")
        return
    
    print(f"✅ Found {TARGET_COMPANY}")
    print(f"   Jobs available: {len(target_company_data['jobs'])}")
    
    # Analyser
    result = await analyze_company_trends(target_company_data)
    
    if result and result['success']:
        # Sauvegarder
        output_data = {
            'analyzed_at': datetime.now().isoformat(),
            'company': target_company_data['company'],
            'analysis': result['analysis'],
            'tokens_used': result['tokens']
        }
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print("=" * 70)
        print("📄 ANALYSIS RESULTS PREVIEW")
        print("=" * 70)
        print(f"\n📊 Overall Summary:")
        print(f"   {result['analysis']['overall_summary']}")
        print()
        
        print("📈 Trend Categories:")
        for cat_key, cat_name in [
            ('digital_growth_product', 'Digital Growth & Product Strategy'),
            ('visual_content_creative', 'Visual Content & Creative Production')
        ]:
            cat_data = result['analysis']['trends'][cat_key]
            print(f"\n   {cat_name}:")
            print(f"   └─ Signal: {cat_data['signal_strength']}/10")
            print(f"   └─ Jobs: {cat_data['job_count']}")
            print(f"   └─ Velocity: {cat_data['hiring_velocity']}")
        
        print()
        print("=" * 70)
        print(f"✅ Full results saved to: {OUTPUT_FILE}")
        print("=" * 70)
    else:
        print("\n❌ Analysis failed")


if __name__ == "__main__":
    asyncio.run(main())

