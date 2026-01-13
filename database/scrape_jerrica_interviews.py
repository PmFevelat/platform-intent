#!/usr/bin/env python3
"""
Scrape management interviews pour les entreprises de Jerrica sans interviews
"""

import json
import asyncio
from scrape_management_interviews import get_management_interviews
from dotenv import load_dotenv

load_dotenv()

# Les 13 entreprises de Jerrica sans interviews
COMPANIES_TO_SCRAPE = [
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
    "Theodore Alexander",
    "Ballard Designs",
    "Design Within Reach"
]

async def scrape_company(company_name, company_data):
    """Scrape les interviews pour une entreprise"""
    website = company_data.get('website', '')
    industry = company_data.get('industry', 'Furniture')
    
    interviews = await get_management_interviews(company_name, website, industry)
    return company_name, interviews

async def main():
    print("="*80)
    print("SCRAPING MANAGEMENT INTERVIEWS - ENTREPRISES DE JERRICA")
    print("="*80)
    
    # Charger les données frontend
    with open('../public/data.json', 'r') as f:
        data = json.load(f)
    
    companies = data['companies']
    
    # Normaliser les noms
    def normalize_name(name):
        return name.lower().replace(',', '').replace('.', '').replace('-', '').replace('&', 'and').replace('  ', ' ').strip()
    
    normalized_to_scrape = {normalize_name(name): name for name in COMPANIES_TO_SCRAPE}
    
    # Trouver les entreprises à scraper
    companies_to_process = []
    for company_key, company_data in companies.items():
        company_name = company_data.get('name', '')
        normalized = normalize_name(company_name)
        
        if normalized in normalized_to_scrape or normalize_name(company_key) in normalized_to_scrape:
            companies_to_process.append((company_name, company_data))
    
    print(f"\n📋 {len(companies_to_process)} entreprises à scraper")
    print()
    
    # Charger les interviews existantes
    try:
        with open('../public/management_interviews.json', 'r') as f:
            interviews_data = json.load(f)
    except FileNotFoundError:
        interviews_data = {}
    
    # Scraper en parallèle (par batch de 3)
    batch_size = 3
    for i in range(0, len(companies_to_process), batch_size):
        batch = companies_to_process[i:i+batch_size]
        
        print(f"\n🔄 Batch {i//batch_size + 1}/{(len(companies_to_process)-1)//batch_size + 1}")
        
        tasks = [scrape_company(name, data) for name, data in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                print(f"  ❌ Erreur: {str(result)}")
                continue
            
            company_name, interviews = result
            if interviews and interviews.get('management_items'):
                interviews_data[company_name] = interviews
                print(f"  ✅ {company_name}: {len(interviews['management_items'])} interviews")
            else:
                print(f"  ⚠️  {company_name}: Aucune interview trouvée")
        
        # Sauvegarder après chaque batch
        with open('../public/management_interviews.json', 'w') as f:
            json.dump(interviews_data, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Sauvegardé")
    
    print("\n" + "="*80)
    print("✅ SCRAPING TERMINÉ")
    print("="*80)
    print(f"\n📊 Total entreprises avec interviews: {len(interviews_data)}")

if __name__ == "__main__":
    asyncio.run(main())

