#!/usr/bin/env python3
"""Corrige les key_insights pour qu'ils soient toujours des tableaux"""

import json

print("🔧 Correction des key_insights...")

# Company News
with open('../public/news_data.json', 'r', encoding='utf-8') as f:
    news_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in news_data:
        items = news_data[company].get('news_items', [])
        for item in items:
            # S'assurer que key_insights est un tableau
            if 'key_insights' not in item:
                item['key_insights'] = []
            elif not isinstance(item['key_insights'], list):
                # Si c'est une string, la mettre dans un tableau
                if isinstance(item['key_insights'], str):
                    item['key_insights'] = [item['key_insights']]
                else:
                    item['key_insights'] = []
        
        print(f"  ✅ {company}: {len(items)} news corrigées")

with open('../public/news_data.json', 'w', encoding='utf-8') as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

# Management Interviews
with open('../public/management_interviews.json', 'r', encoding='utf-8') as f:
    interviews_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in interviews_data:
        items = interviews_data[company].get('management_items', [])
        for item in items:
            # S'assurer que key_quotes est un tableau
            if 'key_quotes' not in item:
                item['key_quotes'] = []
            elif not isinstance(item['key_quotes'], list):
                if isinstance(item['key_quotes'], str):
                    item['key_quotes'] = [item['key_quotes']]
                else:
                    item['key_quotes'] = []
            
            # S'assurer que topics_discussed est un tableau
            if 'topics_discussed' not in item:
                item['topics_discussed'] = []
            elif not isinstance(item['topics_discussed'], list):
                if isinstance(item['topics_discussed'], str):
                    item['topics_discussed'] = [item['topics_discussed']]
                else:
                    item['topics_discussed'] = []
        
        print(f"  ✅ {company}: {len(items)} interviews corrigées")

with open('../public/management_interviews.json', 'w', encoding='utf-8') as f:
    json.dump(interviews_data, f, ensure_ascii=False, indent=2)

# Financial News
with open('../public/financial_news.json', 'r', encoding='utf-8') as f:
    financial_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in financial_data:
        items = financial_data[company].get('financial_items', [])
        for item in items:
            # S'assurer que key_metrics est un tableau
            if 'key_metrics' not in item:
                item['key_metrics'] = []
            elif not isinstance(item['key_metrics'], list):
                if isinstance(item['key_metrics'], str):
                    item['key_metrics'] = [item['key_metrics']]
                else:
                    item['key_metrics'] = []
            
            # S'assurer que strategic_highlights est un tableau
            if 'strategic_highlights' not in item:
                item['strategic_highlights'] = []
            elif not isinstance(item['strategic_highlights'], list):
                if isinstance(item['strategic_highlights'], str):
                    item['strategic_highlights'] = [item['strategic_highlights']]
                else:
                    item['strategic_highlights'] = []
        
        print(f"  ✅ {company}: {len(items)} financial corrigés")

with open('../public/financial_news.json', 'w', encoding='utf-8') as f:
    json.dump(financial_data, f, ensure_ascii=False, indent=2)

print("\n✅ Tous les tableaux sont corrigés! Rafraîchissez votre navigateur.")
