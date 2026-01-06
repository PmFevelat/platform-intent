#!/usr/bin/env python3
"""
Convertit jobs_analysis_v2.json vers le format attendu par le frontend (data.json)
"""

import json
import csv
from datetime import datetime

def load_tam_data():
    """Charge les données TAM pour enrichir les infos des entreprises"""
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

def convert_v2_to_frontend(input_file='jobs_analysis_v2.json', output_file='../public/data.json'):
    """Convertit le format V2 vers le format frontend"""
    
    print(f"📖 Lecture de {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        v2_data = json.load(f)
    
    print(f"📊 Chargement des données TAM...")
    tam_companies = load_tam_data()
    
    # Regrouper les jobs par entreprise
    companies_data = {}
    
    for job_key, job_data in v2_data.items():
        company_name = job_data['company_name']
        
        if company_name not in companies_data:
            # Créer l'entrée de l'entreprise
            tam_info = tam_companies.get(company_name, {})
            companies_data[company_name] = {
                'name': company_name,
                'industry': tam_info.get('industry', 'Furniture'),
                'website': job_data.get('company_website') or tam_info.get('website', ''),
                'employees': tam_info.get('employees', 'N/A'),
                'linkedin': job_data.get('company_linkedin') or tam_info.get('linkedin', ''),
                'jobs': []
            }
        
        # Convertir le job au format frontend
        job = {
            'job_title': job_data['job_title'],
            'job_url': job_data.get('job_board_url', ''),
            'job_board': job_data.get('job_board', 'unknown'),
            'location': job_data.get('location', 'N/A'),
            'date': job_data.get('date_creation', datetime.now().isoformat()),
            'description': job_data.get('description', ''),
            'analysis': job_data.get('analysis'),
            'success': True
        }
        
        companies_data[company_name]['jobs'].append(job)
    
    # Créer le format final
    output_data = {
        'companies': companies_data,
        'metadata': {
            'started': datetime.now().isoformat(),
            'completed': datetime.now().isoformat(),
            'total_jobs': sum(len(c['jobs']) for c in companies_data.values())
        }
    }
    
    print(f"💾 Sauvegarde dans {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Conversion terminée !")
    print(f"📊 {len(companies_data)} entreprises")
    print(f"📋 {output_data['metadata']['total_jobs']} jobs")
    
    # Statistiques par entreprise
    print(f"\n📈 Statistiques :")
    for company_name, company in companies_data.items():
        jobs_count = len(company['jobs'])
        analyzed = sum(1 for j in company['jobs'] if j.get('analysis'))
        print(f"   {company_name[:40]:40} | {jobs_count:3} jobs | {analyzed:3} analyzed")

if __name__ == "__main__":
    convert_v2_to_frontend()

