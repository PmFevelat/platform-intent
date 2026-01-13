#!/usr/bin/env python3
"""
Corrige la structure du tech stack : doit être dans job.analysis.tools_ecosystem
"""

import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Les 20 entreprises de Jerrica
JERRICA_COMPANIES = [
    "La-Z-Boy", "Williams Sonoma", "Millerknoll", "Palliser Furniture Ltd.",
    "Rooms to Go", "Article", "American Leather", "Serena & Lily",
    "Anthropologie Home", "Rowe Furniture", "Room & Board", "Bassett Furniture",
    "Living Spaces", "Jonathan Louis", "Theodore Alexander", "Kimball International",
    "Ballard Designs", "Design Within Reach", "Saks Global", "Costco"
]

def normalize_name(name):
    return name.lower().replace(',', '').replace('.', '').replace('-', '').replace('&', 'and').replace('  ', ' ').strip()

async def extract_tools_from_job(job_description):
    """Extrait les outils d'une description de job avec evidence"""
    
    prompt = f"""Extract ALL specific software/tool names mentioned in this job description.

Look for:
1. Design/Creative tools: Adobe Creative Suite, Photoshop, Illustrator, InDesign, Figma, Sketch, Canva, etc.
2. 3D/Rendering tools: Blender, Maya, 3DS Max, Cinema 4D, SketchUp, ZBrush, KeyShot, V-Ray, etc.
3. E-commerce/Platform tools: Shopify, Magento, WooCommerce, BigCommerce, Salesforce Commerce Cloud, SAP, etc.

For EACH tool found, provide:
- The tool name
- An exact quote from the job description as evidence

Job Description:
{job_description[:4000]}

Respond ONLY with valid JSON in this exact format:
{{
  "design_tools": [
    {{"tool": "Tool Name", "evidence": "exact quote mentioning the tool"}}
  ],
  "3d_tools": [
    {{"tool": "Tool Name", "evidence": "exact quote mentioning the tool"}}
  ],
  "ecommerce_platforms": [
    {{"platform": "Platform Name", "evidence": "exact quote mentioning the platform"}}
  ]
}}
"""
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={ "type": "json_object" }
        )
        
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        
        # Valider la structure
        if not isinstance(result.get('design_tools'), list):
            result['design_tools'] = []
        if not isinstance(result.get('3d_tools'), list):
            result['3d_tools'] = []
        if not isinstance(result.get('ecommerce_platforms'), list):
            result['ecommerce_platforms'] = []
            
        return result
    except Exception as e:
        return {"design_tools": [], "3d_tools": [], "ecommerce_platforms": []}

async def analyze_job(job):
    """Analyse un job et ajoute le tech stack"""
    description = job.get('description', '')
    if not description or len(description) < 100:
        return None
    
    tools = await extract_tools_from_job(description)
    
    # Ne retourner que si au moins un outil trouvé
    total = len(tools.get('design_tools', [])) + len(tools.get('3d_tools', [])) + len(tools.get('ecommerce_platforms', []))
    if total > 0:
        return tools
    return None

async def main():
    print("="*80)
    print("CORRECTION DE LA STRUCTURE TECH STACK")
    print("="*80)
    
    # Charger les données frontend
    with open('../public/data.json', 'r') as f:
        data = json.load(f)
    
    companies = data['companies']
    normalized_jerrica = {normalize_name(name): name for name in JERRICA_COMPANIES}
    
    total_jobs_analyzed = 0
    total_jobs_with_tools = 0
    companies_updated = 0
    
    for company_key, company_data in companies.items():
        company_name = company_data.get('name', '')
        normalized = normalize_name(company_name)
        
        # Vérifier si c'est une entreprise de Jerrica
        if normalized not in normalized_jerrica and normalize_name(company_key) not in normalized_jerrica:
            continue
        
        jobs = company_data.get('jobs', [])
        if not jobs:
            continue
        
        print(f"\n🏢 {company_name}")
        print(f"  📊 Analyse de {len(jobs)} jobs...")
        
        jobs_to_analyze = jobs[:50]  # Max 50 jobs par entreprise
        
        # Analyser les jobs par batch de 5
        for i in range(0, len(jobs_to_analyze), 5):
            batch = jobs_to_analyze[i:i+5]
            tasks = [analyze_job(job) for job in batch]
            results = await asyncio.gather(*tasks)
            
            for job, tools in zip(batch, results):
                total_jobs_analyzed += 1
                if tools:
                    # Ajouter les outils dans job.analysis.tools_ecosystem
                    if 'analysis' not in job:
                        job['analysis'] = {}
                    job['analysis']['tools_ecosystem'] = tools
                    total_jobs_with_tools += 1
        
        # Compter les jobs avec outils
        jobs_with_tools = sum(1 for j in jobs if j.get('analysis', {}).get('tools_ecosystem'))
        if jobs_with_tools > 0:
            print(f"  ✅ {jobs_with_tools} jobs avec outils identifiés")
            companies_updated += 1
        else:
            print(f"  ⚠️  Aucun outil identifié")
    
    # Sauvegarder
    print(f"\n💾 Sauvegarde des modifications...")
    with open('../public/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ CORRECTION TERMINÉE")
    print(f"📊 {companies_updated} entreprises mises à jour")
    print(f"📋 {total_jobs_with_tools}/{total_jobs_analyzed} jobs avec outils")

if __name__ == "__main__":
    asyncio.run(main())

