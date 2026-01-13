#!/usr/bin/env python3
"""
Re-scrape les 20 entreprises de Jerrica avec l'ANCIEN script (OpenAI Web Search)
Pour avoir une cohérence dans les données
"""

import json
import os
from scrape_company_news import get_company_news
from dotenv import load_dotenv

load_dotenv()

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
    return name.lower().replace(',', '').replace('.', '').replace('-', '').replace('&', 'and').replace('  ', ' ').strip()

def main():
    print("="*80)
    print("RE-SCRAPING NEWS - 20 ENTREPRISES DE JERRICA")
    print("Script: OpenAI Web Search (ancien script pour cohérence)")
    print("="*80)
    
    # Charger les données frontend pour avoir les infos entreprises
    with open('../public/data.json', 'r') as f:
        companies_data = json.load(f)['companies']
    
    # Charger les news existantes
    with open('../public/news_data.json', 'r') as f:
        news_data = json.load(f)
    
    # Normaliser les noms
    normalized_jerrica = {normalize_name(name): name for name in JERRICA_COMPANIES}
    
    # Trouver les entreprises à scraper
    companies_to_scrape = []
    for company_key, company_info in companies_data.items():
        company_name = company_info.get('name', '')
        normalized = normalize_name(company_name)
        
        if normalized in normalized_jerrica or normalize_name(company_key) in normalized_jerrica:
            companies_to_scrape.append({
                'name': company_name,
                'website': company_info.get('website', ''),
                'industry': company_info.get('industry', 'Furniture')
            })
    
    print(f"\n📋 {len(companies_to_scrape)} entreprises à re-scraper\n")
    
    # Scraper chaque entreprise
    for i, company in enumerate(companies_to_scrape, 1):
        company_name = company['name']
        print(f"\n[{i}/{len(companies_to_scrape)}] 🔄 {company_name}")
        
        try:
            # Utiliser l'ancien script
            result = get_company_news(
                company_name=company_name,
                company_website=company['website'],
                industry=company['industry']
            )
            
            if result and result.get('news_items'):
                news_data[company_name] = result
                print(f"  ✅ {len(result['news_items'])} articles trouvés")
                
                # Sauvegarder après chaque entreprise
                with open('../public/news_data.json', 'w', encoding='utf-8') as f:
                    json.dump(news_data, f, indent=2, ensure_ascii=False)
                print(f"  💾 Sauvegardé")
            else:
                print(f"  ⚠️  Aucun article trouvé")
                
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")
            continue
    
    print("\n" + "="*80)
    print("✅ RE-SCRAPING TERMINÉ")
    print("="*80)
    print(f"\nToutes les entreprises de Jerrica utilisent maintenant l'ancien script (OpenAI Web Search)")

if __name__ == "__main__":
    main()

