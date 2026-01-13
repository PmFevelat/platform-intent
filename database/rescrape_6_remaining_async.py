#!/usr/bin/env python3
"""
Re-scrape les 6 dernières entreprises avec le script ASYNC (avec workers)
Beaucoup plus rapide !
"""

import json
import asyncio
from scrape_company_news_async import get_company_news
from dotenv import load_dotenv

load_dotenv()

# Les 6 entreprises restantes
REMAINING = [
    "Room & Board",
    "Living Spaces",
    "Jonathan Louis",
    "Theodore Alexander",
    "Kimball International",
    "Saks Global"
]

async def scrape_company(company_name, company_info, news_data):
    """Scrape une entreprise"""
    try:
        result = await get_company_news(
            company_name=company_name,
            company_website=company_info.get('website', ''),
            industry=company_info.get('industry', 'Furniture')
        )
        
        if result and result.get('news_items'):
            news_data[company_name] = result
            return (company_name, len(result['news_items']), None)
        else:
            return (company_name, 0, None)
    except Exception as e:
        return (company_name, 0, str(e))

async def main():
    print("="*80)
    print("RE-SCRAPING ASYNC - 6 ENTREPRISES RESTANTES")
    print("Avec workers parallèles (5 simultanés)")
    print("="*80)
    
    # Charger les données
    with open('../public/data.json', 'r') as f:
        companies_data = json.load(f)['companies']
    
    with open('../public/news_data.json', 'r') as f:
        news_data = json.load(f)
    
    # Trouver les entreprises
    companies_to_scrape = []
    for target in REMAINING:
        for key, info in companies_data.items():
            if target.lower() in key.lower() or target.lower() in info.get('name', '').lower():
                companies_to_scrape.append((info.get('name', target), info))
                break
    
    print(f"\n📋 {len(companies_to_scrape)} entreprises à scraper\n")
    
    # Scraper en parallèle (toutes en même temps)
    tasks = [scrape_company(name, info, news_data) for name, info in companies_to_scrape]
    results = await asyncio.gather(*tasks)
    
    # Afficher les résultats
    print("\n" + "="*80)
    print("RÉSULTATS:")
    print("="*80)
    
    for company_name, count, error in results:
        if error:
            print(f"❌ {company_name}: Erreur - {error[:50]}")
        elif count > 0:
            print(f"✅ {company_name}: {count} articles")
        else:
            print(f"⚠️  {company_name}: Aucun article")
    
    # Sauvegarder
    print("\n💾 Sauvegarde...")
    with open('../public/news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, indent=2, ensure_ascii=False)
    
    print("\n✅ TERMINÉ - Toutes les entreprises de Jerrica utilisent maintenant l'ancien script!")

if __name__ == "__main__":
    asyncio.run(main())

