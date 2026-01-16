#!/usr/bin/env python3
"""Corrige la structure des données Pet Care pour correspondre à l'interface"""

import json

print("🔧 Correction de la structure des données Pet Care...")

# 1. Management Interviews
print("\n📋 Management Interviews")
with open('../public/management_interviews.json', 'r', encoding='utf-8') as f:
    interviews_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in interviews_data:
        items = interviews_data[company].get('management_items', [])
        for item in items:
            # Renommer 'date' en 'published_date'
            if 'date' in item and 'published_date' not in item:
                item['published_date'] = item.pop('date')
            
            # S'assurer que format existe
            if 'format' not in item:
                item['format'] = 'interview'
            
            # S'assurer que sales_insights existe
            if 'sales_insights' not in item:
                item['sales_insights'] = []
            
            # S'assurer que relevance_reason existe
            if 'relevance_reason' not in item:
                item['relevance_reason'] = f"Interview with {item.get('executive_title', 'executive')}"
        
        print(f"  ✅ {company}: {len(items)} interviews corrigées")

with open('../public/management_interviews.json', 'w', encoding='utf-8') as f:
    json.dump(interviews_data, f, ensure_ascii=False, indent=2)

# 2. Company News
print("\n📰 Company News")
with open('../public/news_data.json', 'r', encoding='utf-8') as f:
    news_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in news_data:
        items = news_data[company].get('news_items', [])
        for item in items:
            # Renommer 'date' en 'published_date'
            if 'date' in item and 'published_date' not in item:
                item['published_date'] = item.pop('date')
            
            # S'assurer que category existe
            if 'category' not in item:
                item['category'] = 'ecommerce_growth'
            
            # Renommer presti_score en relevance_score
            if 'presti_score' in item:
                item['relevance_score'] = item.pop('presti_score')
            
            # S'assurer que relevance_reason existe
            if 'relevance_reason' not in item:
                item['relevance_reason'] = 'Recent company development'
        
        print(f"  ✅ {company}: {len(items)} news corrigées")

with open('../public/news_data.json', 'w', encoding='utf-8') as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

# 3. Financial News
print("\n💰 Financial News")
with open('../public/financial_news.json', 'r', encoding='utf-8') as f:
    financial_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in financial_data:
        items = financial_data[company].get('financial_items', [])
        for item in items:
            # Renommer 'date' en 'published_date'
            if 'date' in item and 'published_date' not in item:
                item['published_date'] = item.pop('date')
            
            # S'assurer que period existe
            if 'period' not in item:
                item['period'] = 'Q1 2024'
            
            # S'assurer que document_type existe
            if 'document_type' not in item:
                item['document_type'] = 'press_release'
            
            # S'assurer que category existe
            if 'category' not in item:
                item['category'] = 'earnings'
            
            # S'assurer que relevance_score existe
            if 'relevance_score' not in item:
                item['relevance_score'] = 7
        
        print(f"  ✅ {company}: {len(items)} documents corrigés")

with open('../public/financial_news.json', 'w', encoding='utf-8') as f:
    json.dump(financial_data, f, ensure_ascii=False, indent=2)

print("\n✅ Structure corrigée pour toutes les données Pet Care!")
print("\n🔄 Rafraîchissez votre navigateur pour voir les données.")
