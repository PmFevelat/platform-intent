#!/usr/bin/env python3
"""
Met à jour le frontend directement depuis jobs_data.json
"""

import json
import csv

def load_tam_data():
    """Charge les données TAM"""
    tam_companies = {}
    with open('TAM.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['CompanyName'].strip()
            tam_companies[name] = {
                'industry': row.get('Sub Industry', 'Furniture'),
                'employees': row.get('Employees', 'N/A'),
                'linkedin': row.get('LinkedIn', ''),
                'website': row.get('Website', '')
            }
    return tam_companies

print("="*80)
print("🔄 MISE À JOUR DU FRONTEND DEPUIS jobs_data.json")
print("="*80)
print()

# Charger jobs_data.json
print("📖 Lecture de jobs_data.json...")
with open('jobs_data.json', 'r', encoding='utf-8') as f:
    jobs_data = json.load(f)

print(f"✅ {jobs_data['total_companies']} entreprises trouvées")
print()

# Charger TAM
print("📊 Chargement des données TAM...")
tam_companies = load_tam_data()

# Construire le format frontend
frontend_data = {
    "companies": {},
    "metadata": {
        "last_updated": jobs_data.get('metadata', {}).get('last_updated', ''),
        "total_companies": 0,
        "total_jobs": 0
    }
}

total_jobs = 0
companies_with_jobs = 0

for company_entry in jobs_data['companies']:
    company = company_entry.get('company', {})
    company_name = company.get('name', '')
    
    if not company_name:
        continue
    
    # Normaliser le nom (lowercase pour la clé)
    company_key = company_name.lower()
    
    # Récupérer les infos TAM si disponibles
    tam_info = tam_companies.get(company_name, {})
    
    # Construire l'objet entreprise
    jobs = company_entry.get('jobs', [])
    nb_jobs = len(jobs)
    total_jobs += nb_jobs
    
    if nb_jobs > 0:
        companies_with_jobs += 1
    
    frontend_data['companies'][company_key] = {
        'name': company_name,
        'website': company.get('website', '') or tam_info.get('website', ''),
        'linkedin': company.get('linkedin', '') or tam_info.get('linkedin', ''),
        'industry': company.get('industry', '') or tam_info.get('industry', 'Furniture'),
        'employees': company.get('employees', '') or tam_info.get('employees', 'N/A'),
        'jobs': jobs
    }

frontend_data['metadata']['total_companies'] = len(frontend_data['companies'])
frontend_data['metadata']['total_jobs'] = total_jobs

# Sauvegarder dans public/data.json
print("💾 Sauvegarde dans ../public/data.json...")
with open('../public/data.json', 'w', encoding='utf-8') as f:
    json.dump(frontend_data, f, ensure_ascii=False, indent=2)

print()
print("="*80)
print("✅ MISE À JOUR TERMINÉE")
print("="*80)
print()
print(f"📊 Statistiques:")
print(f"   • Total entreprises: {len(frontend_data['companies'])}")
print(f"   • Entreprises avec jobs: {companies_with_jobs}")
print(f"   • Total jobs: {total_jobs}")
print()

# Afficher les nouvelles entreprises
NEW_COMPANIES = [
    "Millerknoll", "Palliser Furniture Ltd.", "Rooms to Go", "Article",
    "American Leather", "Serena & Lily", "Rowe Furniture", "Room & Board",
    "Bassett Furniture", "Living Spaces", "Jonathan Louis", "Theodore Alexander",
    "Kimball International", "Saks Global"
]

print("🆕 Nouvelles entreprises ajoutées:")
for company_name in NEW_COMPANIES:
    company_key = company_name.lower()
    if company_key in frontend_data['companies']:
        nb_jobs = len(frontend_data['companies'][company_key]['jobs'])
        print(f"   ✅ {company_name}: {nb_jobs} jobs")
    else:
        print(f"   ⚠️  {company_name}: non trouvée")

print()
print("="*80)

