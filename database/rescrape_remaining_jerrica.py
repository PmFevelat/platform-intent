#!/usr/bin/env python3
"""
Re-scrape les 9 entreprises restantes de Jerrica avec l'ANCIEN script
"""

import json
from scrape_company_news import get_company_news
from dotenv import load_dotenv

load_dotenv()

# Les 9 entreprises restantes à re-scraper
REMAINING_COMPANIES = [
    "Article",
    "Serena & Lily",
    "Rowe Furniture",
    "Room & Board",
    "Living Spaces",
    "Jonathan Louis",
    "Theodore Alexander",
    "Kimball International",
    "Saks Global"
]

def normalize_name(name):
    return name.lower().replace(',', '').replace('.', '').replace('-', '').replace('&', 'and').replace('  ', ' ').strip()

def main():
    print("="*80)
    print("RE-SCRAPING NEWS - 9 ENTREPRISES RESTANTES")
    print("Script: OpenAI Web Search")
    print("="*80)
    
    # Charger les données
    with open('../public/data.json', 'r') as f:
        companies_data = json.load(f)['companies']
    
    with open('../public/news_data.json', 'r') as f:
        news_data = json.load(f)
    
    normalized_remaining = {normalize_name(name): name for name in REMAINING_COMPANIES}
    
    companies_to_scrape = []
    for company_key, company_info in companies_data.items():
        company_name = company_info.get('name', '')
        normalized = normalize_name(company_name)
        
        if normalized in normalized_remaining:
            companies_to_scrape.append({
                'name': company_name,
                'website': company_info.get('website', ''),
                'industry': company_info.get('industry', 'Furniture')
            })
    
    print(f"\n📋 {len(companies_to_scrape)} entreprises à scraper\n")
    
    for i, company in enumerate(companies_to_scrape, 1):
        company_name = company['name']
        print(f"\n[{i}/{len(companies_to_scrape)}] 🔄 {company_name}")
        
        try:
            result = get_company_news(
                company_name=company_name,
                company_website=company['website'],
                industry=company['industry']
            )
            
            if result and result.get('news_items'):
                news_data[company_name] = result
                print(f"  ✅ {len(result['news_items'])} articles trouvés")
                
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

if __name__ == "__main__":
    main()

