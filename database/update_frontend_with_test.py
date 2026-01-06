#!/usr/bin/env python3
"""
Met à jour public/data.json avec l'analyse de test de California Closets
"""

import json

print("📂 Loading test analysis...")
with open('california_closets_test.json', 'r', encoding='utf-8') as f:
    test_data = json.load(f)

print("📂 Loading current frontend data...")
with open('../public/data.json', 'r', encoding='utf-8') as f:
    frontend_data = json.load(f)

# Trouver California Closets dans les données frontend
company_name = "California Closets"

if company_name in frontend_data['companies']:
    print(f"✅ Found {company_name} in frontend data")
    
    # Ajouter l'analyse de tendances
    frontend_data['companies'][company_name]['trends_analysis'] = test_data['analysis']
    
    # Sauvegarder
    with open('../public/data.json', 'w', encoding='utf-8') as f:
        json.dump(frontend_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated {company_name} with trend analysis")
    print(f"   Signal strength: {test_data['analysis']['overall_signal_strength']}/10")
    print(f"\n🌐 Refresh your browser to see the changes!")
else:
    print(f"❌ {company_name} not found in frontend data")
    print("\nAvailable companies:")
    for name in list(frontend_data['companies'].keys())[:10]:
        print(f"   - {name}")

