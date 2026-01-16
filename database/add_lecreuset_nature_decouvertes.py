#!/usr/bin/env python3
"""
Script pour ajouter Le Creuset et Nature & Découvertes à jobs_data.json
"""

import json
import os
from datetime import datetime

def add_new_companies():
    """Ajoute les nouvelles entreprises à jobs_data.json"""
    
    # Nouvelles entreprises à ajouter
    new_companies = [
        {
            "name": "Le Creuset",
            "website": "https://www.lecreuset.fr/fr_FR/",
            "linkedin": "https://www.linkedin.com/company/le-creuset/",
            "industry": "Cookware & Kitchen",
            "employees": "1000-5000"
        },
        {
            "name": "Nature & Découvertes", 
            "website": "https://www.natureetdecouvertes.com/",
            "linkedin": "https://www.linkedin.com/company/nature-et-decouvertes/",
            "industry": "Retail & Lifestyle",
            "employees": "1000-5000"
        }
    ]
    
    # Charger jobs_data.json existant
    jobs_data_path = 'jobs_data.json'
    if os.path.exists(jobs_data_path):
        with open(jobs_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("❌ Fichier jobs_data.json non trouvé")
        return False
    
    # Vérifier si les entreprises existent déjà
    existing_companies = [
        company_entry.get('company', {}).get('name', '') 
        for company_entry in data.get('companies', [])
    ]
    
    companies_added = 0
    
    for new_company in new_companies:
        company_name = new_company['name']
        
        if company_name in existing_companies:
            print(f"⚠️  {company_name} existe déjà dans la base")
            continue
        
        # Créer l'entrée pour la nouvelle entreprise
        company_entry = {
            "success": False,  # Sera mis à jour lors du scraping
            "jobs": [],
            "nb_jobs": 0,
            "company": new_company
        }
        
        # Ajouter à la liste
        data['companies'].append(company_entry)
        companies_added += 1
        
        print(f"✅ {company_name} ajouté")
    
    if companies_added > 0:
        # Mettre à jour les statistiques
        data['total_companies'] = len(data['companies'])
        
        # Sauvegarder
        with open(jobs_data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ {companies_added} nouvelles entreprises ajoutées")
        print(f"📊 Total entreprises : {data['total_companies']}")
        print(f"💾 Sauvegardé dans {jobs_data_path}")
        return True
    else:
        print("\n⚠️  Aucune nouvelle entreprise à ajouter")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🏢 AJOUT DE NOUVELLES ENTREPRISES")
    print("="*60)
    print("📋 Entreprises à ajouter :")
    print("  • Le Creuset")
    print("  • Nature & Découvertes")
    print("="*60)
    
    success = add_new_companies()
    
    if success:
        print("\n🚀 Prêt pour le scraping !")
        print("   Utilisez : python3 scrape_lecreuset_nature_decouvertes.py")
    
    print("="*60)