#!/usr/bin/env python3
"""
Script pour intégrer les entreprises Pet Care au fichier data.json frontend.
Ce script ajoute les 4 entreprises avec une structure de base, qui sera enrichie par les scripts de scraping.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Définir les entreprises Pet Care
PET_CARE_COMPANIES = [
    {
        "name": "Chewy",
        "website": "https://www.chewy.com/",
        "linkedin": "https://www.linkedin.com/company/chewy-com/",
        "industry": "Pet Supplies E-commerce",
        "employees": "10,000+",
        "jobs": []
    },
    {
        "name": "Petco",
        "website": "https://www.petco.com/shop/en/petcostore",
        "linkedin": "https://www.linkedin.com/company/petco/",
        "industry": "Pet Retail",
        "employees": "25,000+",
        "jobs": []
    },
    {
        "name": "Petmate",
        "website": "https://www.petmate.com/",
        "linkedin": "https://www.linkedin.com/company/petmate/",
        "industry": "Pet Products Manufacturing",
        "employees": "500-1000",
        "jobs": []
    },
    {
        "name": "Petsmart",
        "website": "https://www.petsmart.com/",
        "linkedin": "https://www.linkedin.com/company/petsmart/",
        "industry": "Pet Retail",
        "employees": "50,000+",
        "jobs": []
    }
]

def normalize_company_name(name: str) -> str:
    """Normalise le nom de l'entreprise pour l'utiliser comme clé"""
    return name.lower().strip()

def integrate_pet_care_companies():
    """Intègre les entreprises Pet Care au fichier data.json"""
    
    # Chemins des fichiers
    project_root = Path(__file__).parent.parent
    data_file = project_root / "public" / "data.json"
    backup_file = project_root / "public" / f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print("🐾 Intégration des entreprises Pet Care au frontend")
    print("=" * 60)
    
    # Vérifier que le fichier existe
    if not data_file.exists():
        print(f"❌ Fichier data.json non trouvé: {data_file}")
        return False
    
    # Charger les données existantes
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Fichier data.json chargé: {data_file}")
    except Exception as e:
        print(f"❌ Erreur lors du chargement de data.json: {e}")
        return False
    
    # Créer une sauvegarde
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Sauvegarde créée: {backup_file}")
    except Exception as e:
        print(f"❌ Erreur lors de la création de la sauvegarde: {e}")
        return False
    
    # Vérifier que la structure companies existe
    if 'companies' not in data:
        data['companies'] = {}
    
    # Ajouter les entreprises Pet Care
    added_count = 0
    updated_count = 0
    
    for company in PET_CARE_COMPANIES:
        company_key = normalize_company_name(company['name'])
        
        if company_key in data['companies']:
            print(f"⚠️  Entreprise déjà existante: {company['name']} - Mise à jour...")
            # Garder les jobs existants si présents
            existing_jobs = data['companies'][company_key].get('jobs', [])
            company['jobs'] = existing_jobs if existing_jobs else []
            data['companies'][company_key] = company
            updated_count += 1
        else:
            print(f"✅ Ajout de: {company['name']}")
            data['companies'][company_key] = company
            added_count += 1
    
    # Mettre à jour les métadonnées
    if 'metadata' not in data:
        data['metadata'] = {}
    
    data['metadata']['last_updated'] = datetime.now().isoformat()
    data['metadata']['total_companies'] = len(data['companies'])
    
    # Compter le total des jobs
    total_jobs = sum(len(company.get('jobs', [])) for company in data['companies'].values())
    data['metadata']['total_jobs'] = total_jobs
    
    # Sauvegarder le fichier mis à jour
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Fichier data.json mis à jour avec succès!")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False
    
    # Résumé
    print("\n" + "=" * 60)
    print(f"📊 Résumé:")
    print(f"   - Entreprises ajoutées: {added_count}")
    print(f"   - Entreprises mises à jour: {updated_count}")
    print(f"   - Total entreprises: {data['metadata']['total_companies']}")
    print(f"   - Total jobs: {data['metadata']['total_jobs']}")
    print("\n🎉 Les entreprises Pet Care sont maintenant visibles dans /jobs!")
    print("\n📝 Prochaines étapes:")
    print("   1. Les entreprises apparaissent maintenant dans l'interface /jobs")
    print("   2. Lancez les scripts de scraping pour enrichir les données")
    print("   3. Les données seront automatiquement mises à jour")
    
    return True

def main():
    """Fonction principale"""
    success = integrate_pet_care_companies()
    
    if not success:
        print("\n❌ Échec de l'intégration des entreprises Pet Care")
        exit(1)
    
    print("\n✅ Intégration terminée avec succès!")

if __name__ == "__main__":
    main()