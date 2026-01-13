#!/usr/bin/env python3
"""
Script pour vérifier le statut du pipeline de scraping
"""

import json
import os
from datetime import datetime

NEW_COMPANIES = [
    "Millerknoll", "Palliser Furniture Ltd.", "Rooms to Go", "Article",
    "American Leather", "Serena & Lily", "Rowe Furniture", "Room & Board",
    "Bassett Furniture", "Living Spaces", "Jonathan Louis", "Theodore Alexander",
    "Kimball International", "Saks Global"
]

def print_status():
    print("="*80)
    print("📊 STATUT DU PIPELINE - 14 NOUVELLES ENTREPRISES")
    print("="*80)
    print()
    
    # Vérifier jobs_data.json
    if os.path.exists('jobs_data.json'):
        with open('jobs_data.json', 'r', encoding='utf-8') as f:
            jobs_data = json.load(f)
        
        new_companies_data = [
            c for c in jobs_data['companies']
            if c.get('company', {}).get('name') in NEW_COMPANIES
        ]
        
        total_jobs = sum(c.get('nb_jobs', 0) for c in new_companies_data)
        companies_with_jobs = sum(1 for c in new_companies_data if c.get('nb_jobs', 0) > 0)
        
        # Compter les jobs analysés
        analyzed_jobs = 0
        for c in new_companies_data:
            for job in c.get('jobs', []):
                if job.get('analysis'):
                    analyzed_jobs += 1
        
        print("✅ ÉTAPE 1 : SCRAPING DES JOBS (Mantiks API)")
        print(f"   • {companies_with_jobs}/{len(NEW_COMPANIES)} entreprises avec des jobs")
        print(f"   • {total_jobs} jobs trouvés au total")
        print()
        
        print("✅ ÉTAPE 2 : ANALYSE DES JOBS (OpenAI)")
        print(f"   • {analyzed_jobs}/{total_jobs} jobs analysés")
        if analyzed_jobs < total_jobs:
            print(f"   ⏳ En cours... ({analyzed_jobs}/{total_jobs})")
        print()
    
    # Vérifier company_news.json
    if os.path.exists('company_news.json'):
        with open('company_news.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        new_companies_news = {k: v for k, v in news_data.items() if k in NEW_COMPANIES}
        total_articles = sum(len(v.get('news_items', [])) for v in new_companies_news.values())
        
        print("✅ ÉTAPE 3 : COMPANY NEWS (Perplexity + OpenAI)")
        print(f"   • {len(new_companies_news)}/{len(NEW_COMPANIES)} entreprises scrapées")
        print(f"   • {total_articles} articles trouvés au total")
        if len(new_companies_news) < len(NEW_COMPANIES):
            print(f"   ⏳ En cours... ({len(new_companies_news)}/{len(NEW_COMPANIES)})")
        print()
    else:
        print("⏳ ÉTAPE 3 : COMPANY NEWS - Pas encore démarré")
        print()
    
    # Vérifier management_interviews.json
    if os.path.exists('management_interviews.json'):
        with open('management_interviews.json', 'r', encoding='utf-8') as f:
            interviews_data = json.load(f)
        
        new_companies_interviews = {k: v for k, v in interviews_data.items() if k in NEW_COMPANIES}
        total_interviews = sum(len(v.get('interviews', [])) for v in new_companies_interviews.values())
        
        print("✅ ÉTAPE 4 : MANAGEMENT INTERVIEWS (Perplexity + OpenAI)")
        print(f"   • {len(new_companies_interviews)}/{len(NEW_COMPANIES)} entreprises scrapées")
        print(f"   • {total_interviews} interviews trouvées au total")
        if len(new_companies_interviews) < len(NEW_COMPANIES):
            print(f"   ⏳ En cours... ({len(new_companies_interviews)}/{len(NEW_COMPANIES)})")
        print()
    else:
        print("⏳ ÉTAPE 4 : MANAGEMENT INTERVIEWS - Pas encore démarré")
        print()
    
    # Vérifier frontend
    frontend_updated = (
        os.path.exists('../public/news_data.json') and
        os.path.exists('../public/management_interviews.json') and
        os.path.exists('../public/jobs_analysis.json')
    )
    
    if frontend_updated:
        print("✅ ÉTAPE 5 : FRONTEND MIS À JOUR")
    else:
        print("⏳ ÉTAPE 5 : MISE À JOUR FRONTEND - En attente")
    
    print()
    print("="*80)
    print("💡 COMMANDES UTILES")
    print("="*80)
    print("   # Suivre le log en temps réel:")
    print("   tail -f pipeline_new_companies.log")
    print()
    print("   # Relancer le statut:")
    print("   python3 check_pipeline_status.py")
    print()
    print("   # Vérifier les processus en cours:")
    print("   ps aux | grep python")
    print("="*80)
    
    # Détail par entreprise
    print()
    print("="*80)
    print("📋 DÉTAIL PAR ENTREPRISE")
    print("="*80)
    print()
    
    if os.path.exists('jobs_data.json'):
        with open('jobs_data.json', 'r', encoding='utf-8') as f:
            jobs_data = json.load(f)
        
        news_data = {}
        if os.path.exists('company_news.json'):
            with open('company_news.json', 'r', encoding='utf-8') as f:
                news_data = json.load(f)
        
        interviews_data = {}
        if os.path.exists('management_interviews.json'):
            with open('management_interviews.json', 'r', encoding='utf-8') as f:
                interviews_data = json.load(f)
        
        for company_name in NEW_COMPANIES:
            # Trouver les données de l'entreprise
            company_entry = next(
                (c for c in jobs_data['companies'] if c.get('company', {}).get('name') == company_name),
                None
            )
            
            if not company_entry:
                continue
            
            nb_jobs = company_entry.get('nb_jobs', 0)
            analyzed = sum(1 for j in company_entry.get('jobs', []) if j.get('analysis'))
            nb_news = len(news_data.get(company_name, {}).get('news_items', []))
            nb_interviews = len(interviews_data.get(company_name, {}).get('interviews', []))
            
            status_jobs = "✅" if nb_jobs > 0 else "❌"
            status_analysis = "✅" if analyzed == nb_jobs and nb_jobs > 0 else ("⏳" if analyzed > 0 else "⏹️")
            status_news = "✅" if nb_news > 0 else "⏹️"
            status_interviews = "✅" if nb_interviews > 0 else "⏹️"
            
            print(f"{company_name:30} {status_jobs} Jobs: {nb_jobs:2}  {status_analysis} Analysés: {analyzed:2}  {status_news} News: {nb_news:2}  {status_interviews} Interviews: {nb_interviews:2}")
    
    print()
    print("="*80)

if __name__ == "__main__":
    print_status()

