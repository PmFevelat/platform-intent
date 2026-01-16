#!/usr/bin/env python3
"""Complète la structure des données Pet Care avec tous les champs requis"""

import json

print("🔧 Complétion de la structure des données...")

# Management Interviews - Ajouter key_executives_identified et overall_assessment
with open('../public/management_interviews.json', 'r', encoding='utf-8') as f:
    interviews_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in interviews_data:
        data = interviews_data[company]
        items = data.get('management_items', [])
        
        # Générer key_executives_identified depuis les items
        executives = {}
        for item in items:
            exec_name = item.get('executive_name', '')
            exec_title = item.get('executive_title', '')
            if exec_name:
                if exec_name not in executives:
                    executives[exec_name] = {
                        "name": exec_name,
                        "title": exec_title,
                        "relevance": f"Key decision maker in {exec_title.lower()} role",
                        "content_count": 0
                    }
                executives[exec_name]['content_count'] += 1
        
        data['key_executives_identified'] = list(executives.values())
        
        # Ajouter overall_assessment s'il n'existe pas
        if 'overall_assessment' not in data:
            data['overall_assessment'] = {
                "decision_maker_visibility": "high" if len(items) >= 3 else "medium" if len(items) >= 1 else "low",
                "strategic_priorities": [
                    "Ecommerce growth",
                    "Customer experience",
                    "Digital transformation"
                ],
                "presti_entry_points": [
                    "Product photography and visualization",
                    "Marketing content creation"
                ],
                "recommended_contact": executives[list(executives.keys())[0]]['name'] if executives else "CEO"
            }
        
        print(f"  ✅ {company}: {len(items)} interviews, {len(executives)} executives")

with open('../public/management_interviews.json', 'w', encoding='utf-8') as f:
    json.dump(interviews_data, f, ensure_ascii=False, indent=2)

# Company News - Ajouter overall_assessment
with open('../public/news_data.json', 'r', encoding='utf-8') as f:
    news_data = json.load(f)

for company in ['Chewy', 'Petco', 'Petmate', 'Petsmart']:
    if company in news_data:
        data = news_data[company]
        items = data.get('news_items', [])
        
        if 'overall_assessment' not in data:
            avg_score = sum(item.get('relevance_score', 0) for item in items) / len(items) if items else 0
            
            data['overall_assessment'] = {
                "presti_fit_score": round(avg_score, 1),
                "key_opportunities": [
                    "Growing product catalog",
                    "Visual content needs",
                    "Marketing campaigns"
                ],
                "recommended_approach": "Focus on ecommerce and digital transformation initiatives"
            }
        
        print(f"  ✅ {company}: {len(items)} news")

with open('../public/news_data.json', 'w', encoding='utf-8') as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

print("\n✅ Structure complétée! Rafraîchissez votre navigateur.")
