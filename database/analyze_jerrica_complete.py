#!/usr/bin/env python3
"""
Analyse complète des 20 entreprises de Jerrica et mise à jour du frontend
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
    "La-Z-Boy",
    "Williams Sonoma",
    "Millerknoll",
    "Palliser Furniture Ltd.",
    "Rooms to Go",
    "Article",
    "American Leather",
    "Serena & Lily",
    "Anthropologie Home",
    "Rowe Furniture",
    "Room & Board",
    "Bassett Furniture",
    "Living Spaces",
    "Jonathan Louis",
    "Theodore Alexander",
    "Kimball International",
    "Ballard Designs",
    "Design Within Reach",
    "Saks Global",
    "Costco"
]

def normalize_name(name):
    """Normalise les noms d'entreprises"""
    return name.lower().replace(',', '').replace('.', '').replace('-', '').replace('&', 'and').replace('  ', ' ').strip()

async def extract_tools_from_job(job_description):
    """Extrait les outils/plateformes d'une description de job"""
    
    prompt = f"""Extract ALL specific software/tool names mentioned in this job description.

Look for:
1. Design/Creative tools: Adobe Creative Suite, Photoshop, Illustrator, InDesign, Figma, Sketch, Canva, etc.
2. 3D/Rendering tools: Blender, Maya, 3DS Max, Cinema 4D, SketchUp, ZBrush, KeyShot, V-Ray, etc.
3. E-commerce/Platform tools: Shopify, Magento, WooCommerce, BigCommerce, Salesforce Commerce Cloud, etc.

IMPORTANT:
- Extract ONLY specific tool/software names that are explicitly mentioned
- Include version numbers if mentioned (e.g., "Adobe Creative Suite")
- Be generous - include anything that might be a tool
- Return empty arrays if nothing found

Job Description:
{job_description[:4000]}

Respond ONLY with valid JSON in this exact format:
{{
  "design_tools": [],
  "3d_tools": [],
  "ecommerce_platforms": []
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
        #print(f"    ⚠️  Erreur extraction: {str(e)}")
        return {"design_tools": [], "3d_tools": [], "ecommerce_platforms": []}

async def analyze_company(company_name, company_data):
    """Analyse une entreprise et extrait le tech stack"""
    
    print(f"\n🏢 {company_name}")
    
    jobs = company_data.get('jobs', [])
    if not jobs:
        print(f"  ⚠️  Aucun job à analyser")
        return None
    
    print(f"  📊 Analyse de {len(jobs)} jobs...")
    
    # Extraire les outils de tous les jobs
    all_design_tools = set()
    all_3d_tools = set()
    all_ecommerce = set()
    
    tasks = []
    for job in jobs[:50]:  # Limiter à 50 jobs max par entreprise
        if 'description' in job and job['description']:
            tasks.append(extract_tools_from_job(job['description']))
    
    results = await asyncio.gather(*tasks)
    
    for result in results:
        all_design_tools.update(result.get('design_tools', []))
        all_3d_tools.update(result.get('3d_tools', []))
        all_ecommerce.update(result.get('ecommerce_platforms', []))
    
    tools_ecosystem = {
        "design_tools": sorted(list(all_design_tools)),
        "3d_tools": sorted(list(all_3d_tools)),
        "ecommerce_platforms": sorted(list(all_ecommerce))
    }
    
    total_tools = len(all_design_tools) + len(all_3d_tools) + len(all_ecommerce)
    print(f"  ✅ {total_tools} outils uniques trouvés")
    
    return tools_ecosystem

async def main():
    print("="*80)
    print("ANALYSE TECH STACK POUR LES 20 ENTREPRISES DE JERRICA")
    print("="*80)
    
    # Charger les données frontend
    with open('../public/data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    companies = data['companies']
    
    # Normaliser les noms pour la recherche
    normalized_jerrica = {normalize_name(name): name for name in JERRICA_COMPANIES}
    
    # Analyser chaque entreprise
    updates = 0
    for company_key, company_data in companies.items():
        company_name = company_data.get('name', '')
        normalized = normalize_name(company_name)
        
        # Vérifier si c'est une entreprise de Jerrica
        if normalized in normalized_jerrica or normalize_name(company_key) in normalized_jerrica:
            tools_ecosystem = await analyze_company(company_name, company_data)
            
            if tools_ecosystem:
                # Mettre à jour les données
                companies[company_key]['tools_ecosystem'] = tools_ecosystem
                updates += 1
    
    # Sauvegarder
    print(f"\n💾 Sauvegarde des modifications...")
    with open('../public/data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ ANALYSE TERMINÉE")
    print(f"📊 {updates} entreprises mises à jour avec leur tech stack")

if __name__ == "__main__":
    asyncio.run(main())

