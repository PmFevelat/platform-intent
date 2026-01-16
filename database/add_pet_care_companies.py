#!/usr/bin/env python3
"""
Script pour ajouter les entreprises Pet Care à la base de données.
Ce script ajoute les nouvelles entreprises au fichier TAM.csv existant.
"""

import csv
import os
from datetime import datetime

# Nouvelles entreprises Pet Care à ajouter
PET_CARE_COMPANIES = [
    {
        "CompanyName": "Chewy",
        "Website": "https://www.chewy.com/",
        "LinkedIn": "https://www.linkedin.com/company/chewy-com/",
        "Sub Industry": "Pet Supplies E-commerce",
        "Country": "United States",
        "Employees": "10,000+"
    },
    {
        "CompanyName": "Petco",
        "Website": "https://www.petco.com/shop/en/petcostore",
        "LinkedIn": "https://www.linkedin.com/company/petco/",
        "Sub Industry": "Pet Retail",
        "Country": "United States", 
        "Employees": "25,000+"
    },
    {
        "CompanyName": "Petmate",
        "Website": "https://www.petmate.com/",
        "LinkedIn": "https://www.linkedin.com/company/petmate/",
        "Sub Industry": "Pet Products Manufacturing",
        "Country": "United States",
        "Employees": "500-1000"
    },
    {
        "CompanyName": "Petsmart",
        "Website": "https://www.petsmart.com/",
        "LinkedIn": "https://www.linkedin.com/company/petsmart/",
        "Sub Industry": "Pet Retail",
        "Country": "United States",
        "Employees": "50,000+"
    }
]

def add_companies_to_tam():
    """Ajoute les entreprises Pet Care au fichier TAM.csv"""
    
    # Chemins des fichiers
    database_dir = os.path.dirname(os.path.abspath(__file__))
    tam_file = os.path.join(database_dir, "TAM.csv")
    backup_file = os.path.join(database_dir, f"TAM_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    # Vérifier si le fichier TAM.csv existe
    if not os.path.exists(tam_file):
        print(f"❌ Fichier TAM.csv non trouvé: {tam_file}")
        return False
    
    # Créer une sauvegarde
    try:
        with open(tam_file, 'r', encoding='utf-8') as src, open(backup_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        print(f"✅ Sauvegarde créée: {backup_file}")
    except Exception as e:
        print(f"❌ Erreur lors de la création de la sauvegarde: {e}")
        return False
    
    # Lire les entreprises existantes
    existing_companies = set()
    try:
        with open(tam_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_companies.add(row.get('CompanyName', '').strip().lower())
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier TAM.csv: {e}")
        return False
    
    # Filtrer les nouvelles entreprises
    new_companies = []
    for company in PET_CARE_COMPANIES:
        if company['CompanyName'].lower() not in existing_companies:
            new_companies.append(company)
        else:
            print(f"⚠️  Entreprise déjà existante: {company['CompanyName']}")
    
    if not new_companies:
        print("ℹ️  Aucune nouvelle entreprise à ajouter.")
        return True
    
    # Ajouter les nouvelles entreprises
    try:
        with open(tam_file, 'a', encoding='utf-8', newline='') as f:
            fieldnames = ['CompanyName', 'Website', 'LinkedIn', 'Sub Industry', 'Country', 'Employees']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            for company in new_companies:
                writer.writerow(company)
                print(f"✅ Ajouté: {company['CompanyName']}")
        
        print(f"\n🎉 {len(new_companies)} nouvelles entreprises Pet Care ajoutées avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout des entreprises: {e}")
        return False

def main():
    """Fonction principale"""
    print("🐾 Ajout des entreprises Pet Care à la base de données")
    print("=" * 50)
    
    success = add_companies_to_tam()
    
    if success:
        print("\n✅ Script terminé avec succès!")
        print("\nProchaintes étapes:")
        print("1. Lancer le scraping des company news")
        print("2. Lancer le scraping des management interviews")
        print("3. Lancer l'analyse des job offers")
        print("4. Lancer le scraping des financial news")
        print("\nUtilisez l'interface web temporaire pour lancer ces scripts.")
    else:
        print("\n❌ Erreurs détectées lors de l'exécution.")

if __name__ == "__main__":
    main()