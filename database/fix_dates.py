#!/usr/bin/env python3
"""Corrige les dates invalides dans les données Pet Care"""

import json
import re

print("📅 Correction des dates...")

# Management Interviews
with open('../public/management_interviews.json', 'r', encoding='utf-8') as f:
    interviews_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in interviews_data:
        items = interviews_data[company].get('management_items', [])
        for item in items:
            date = item.get('published_date', '')
            # Si c'est juste une année, ajouter -01-01
            if re.match(r'^\d{4}$', date):
                item['published_date'] = f"{date}-01-01"
            # Si c'est juste année-mois, ajouter -01
            elif re.match(r'^\d{4}-\d{2}$', date):
                item['published_date'] = f"{date}-01"
        print(f"  ✅ {company}: {len(items)} interviews")

with open('../public/management_interviews.json', 'w', encoding='utf-8') as f:
    json.dump(interviews_data, f, ensure_ascii=False, indent=2)

# Company News
with open('../public/news_data.json', 'r', encoding='utf-8') as f:
    news_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in news_data:
        items = news_data[company].get('news_items', [])
        for item in items:
            date = item.get('published_date', '')
            if re.match(r'^\d{4}$', date):
                item['published_date'] = f"{date}-01-01"
            elif re.match(r'^\d{4}-\d{2}$', date):
                item['published_date'] = f"{date}-01"
        print(f"  ✅ {company}: {len(items)} news")

with open('../public/news_data.json', 'w', encoding='utf-8') as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

# Financial News
with open('../public/financial_news.json', 'r', encoding='utf-8') as f:
    financial_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in financial_data:
        items = financial_data[company].get('financial_items', [])
        for item in items:
            date = item.get('published_date', '')
            if re.match(r'^\d{4}$', date):
                item['published_date'] = f"{date}-01-01"
            elif re.match(r'^\d{4}-\d{2}$', date):
                item['published_date'] = f"{date}-01"
        print(f"  ✅ {company}: {len(items)} financial")

with open('../public/financial_news.json', 'w', encoding='utf-8') as f:
    json.dump(financial_data, f, ensure_ascii=False, indent=2)

print("\n✅ Dates corrigées! Rafraîchissez votre navigateur.")
