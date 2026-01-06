#!/usr/bin/env python3
"""
Convertit les analyses de tendances au format frontend
"""

import json
from datetime import datetime

def convert_trends_to_frontend():
    """Convertit jobs_trends_analysis.json vers le format data.json du frontend"""
    
    print("📂 Chargement des données...")
    
    # Charger les données originales
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        jobs_data = json.load(f)
    
    # Charger les analyses de tendances
    with open('jobs_trends_analysis.json', 'r', encoding='utf-8') as f:
        trends_data = json.load(f)
    
    # Créer la structure pour le frontend
    frontend_data = {
        "companies": {},
        "metadata": {
            "started": datetime.now().isoformat(),
            "completed": datetime.now().isoformat(),
            "total_jobs": 0
        }
    }
    
    total_jobs = 0
    
    # Pour chaque entreprise avec des jobs
    for company_data in jobs_data['companies']:
        if not company_data.get('success') or company_data.get('nb_jobs', 0) == 0:
            continue
        
        company_info = company_data['company']
        company_name = company_info['name']
        jobs = company_data.get('jobs', [])
        
        # Récupérer l'analyse de tendances si elle existe
        trends_analysis = None
        if company_name in trends_data:
            trends_analysis = trends_data[company_name].get('analysis')
        
        # Convertir les jobs
        converted_jobs = []
        for job in jobs:
            job_date = job.get('date_creation', '')[:10] if job.get('date_creation') else ''
            
            converted_job = {
                "job_title": job.get('job_title', ''),
                "job_url": job.get('job_board_url', ''),
                "job_board": job.get('job_board', ''),
                "location": job.get('location', ''),
                "date": job_date,
                "description": job.get('description', ''),
                "analysis": None,  # On ne garde plus les analyses individuelles
                "success": True
            }
            
            converted_jobs.append(converted_job)
            total_jobs += 1
        
        # Ajouter l'entreprise au résultat
        frontend_data['companies'][company_name] = {
            "name": company_name,
            "industry": company_info.get('industry', ''),
            "website": company_info.get('website', ''),
            "employees": company_info.get('employees', ''),
            "linkedin": company_info.get('linkedin', ''),
            "jobs": converted_jobs,
            "trends_analysis": trends_analysis  # Nouvelle structure d'analyse
        }
    
    frontend_data['metadata']['total_jobs'] = total_jobs
    
    # Sauvegarder
    output_path = '../public/data.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(frontend_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Conversion terminée !")
    print(f"📊 {len(frontend_data['companies'])} entreprises")
    print(f"💼 {total_jobs} offres d'emploi")
    print(f"📁 Sauvegardé dans : {output_path}")
    
    # Statistiques sur les tendances
    high_signal = sum(1 for c in frontend_data['companies'].values() 
                      if c.get('trends_analysis') and c['trends_analysis'].get('overall_signal_strength', 0) >= 7)
    
    print(f"\n🎯 Entreprises avec signal fort (≥7/10) : {high_signal}")


if __name__ == "__main__":
    convert_trends_to_frontend()

