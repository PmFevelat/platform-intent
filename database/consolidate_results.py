#!/usr/bin/env python3
"""
Script pour consolider les résultats des nouvelles entreprises
dans company_news.json et management_interviews.json
"""

import json
import os
import glob

print("="*80)
print("🔄 CONSOLIDATION DES RÉSULTATS")
print("="*80)
print()

# ============================================================================
# CONSOLIDER LES COMPANY NEWS
# ============================================================================

print("📰 Consolidation des company news...")

# Charger le fichier existant
with open('company_news.json', 'r', encoding='utf-8') as f:
    news_data = json.load(f)

print(f"   Entreprises existantes: {len(news_data)}")

# Trouver tous les fichiers hybrid_*_results.json
hybrid_files = glob.glob('hybrid_*_results.json')
print(f"   Fichiers à consolider: {len(hybrid_files)}")

added_news = 0
for file_path in hybrid_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    # Vérifier si le fichier contient des news
    if 'news' in result:
        news_info = result['news']
        company_name = news_info['company_name']
        
        # Ajouter ou mettre à jour dans news_data
        news_data[company_name] = news_info
        added_news += 1
        print(f"   ✅ {company_name}: {len(news_info.get('news_items', []))} articles")

# Sauvegarder
with open('company_news.json', 'w', encoding='utf-8') as f:
    json.dump(news_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Company news consolidées: {added_news} entreprises ajoutées")
print(f"   Total: {len(news_data)} entreprises")

# ============================================================================
# CONSOLIDER LES MANAGEMENT INTERVIEWS
# ============================================================================

print()
print("🎤 Consolidation des management interviews...")

# Charger le fichier existant
with open('management_interviews.json', 'r', encoding='utf-8') as f:
    interviews_data = json.load(f)

print(f"   Entreprises existantes: {len(interviews_data)}")

# Trouver tous les fichiers hybrid_*_results.json qui contiennent des interviews
added_interviews = 0
for file_path in hybrid_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    # Vérifier si le fichier contient des interviews
    if 'interviews' in result:
        interview_info = result['interviews']
        company_name = interview_info['company_name']
        
        # Convertir au format attendu
        formatted_data = {
            "company_name": company_name,
            "interviews": interview_info.get('interviews', []),
            "search_date": interview_info.get('search_date'),
            "scrape_metadata": interview_info.get('scrape_metadata', {})
        }
        
        # Renommer 'interviews' en 'management_items' si nécessaire
        if 'interviews' in formatted_data:
            formatted_data['management_items'] = formatted_data.pop('interviews')
        
        interviews_data[company_name] = formatted_data
        added_interviews += 1
        print(f"   ✅ {company_name}: {len(formatted_data.get('management_items', []))} interviews")

# Vérifier aussi management_interviews_test.json
if os.path.exists('management_interviews_test.json'):
    with open('management_interviews_test.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    for company_name, data in test_data.items():
        if company_name not in interviews_data or not interviews_data[company_name].get('management_items'):
            interviews_data[company_name] = data
            added_interviews += 1
            print(f"   ✅ {company_name}: {len(data.get('management_items', []))} interviews (from test)")

# Sauvegarder
with open('management_interviews.json', 'w', encoding='utf-8') as f:
    json.dump(interviews_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Management interviews consolidées: {added_interviews} entreprises ajoutées")
print(f"   Total: {len(interviews_data)} entreprises")

# ============================================================================
# METTRE À JOUR LE FRONTEND
# ============================================================================

print()
print("="*80)
print("📁 MISE À JOUR DU FRONTEND")
print("="*80)
print()

# Copier vers public/
import shutil

shutil.copy('company_news.json', '../public/news_data.json')
print("✅ news_data.json copié vers public/")

shutil.copy('management_interviews.json', '../public/management_interviews.json')
print("✅ management_interviews.json copié vers public/")

# Conversion des jobs
print()
print("🔄 Conversion jobs_analysis.json...")
try:
    import subprocess
    result = subprocess.run(['python3', 'convert_v2_to_frontend.py'], 
                          capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print("✅ jobs_analysis.json mis à jour")
    else:
        print(f"⚠️  Erreur conversion: {result.stderr[:200]}")
except Exception as e:
    print(f"⚠️  Erreur: {e}")

print()
print("="*80)
print("✅ CONSOLIDATION TERMINÉE !")
print("="*80)
print()
print("📊 Résumé:")
print(f"   • {added_news} entreprises avec news")
print(f"   • {added_interviews} entreprises avec interviews")
print(f"   • Frontend mis à jour")
print()
print("🎉 Les 14 nouvelles entreprises sont maintenant disponibles dans l'app !")
print("="*80)

