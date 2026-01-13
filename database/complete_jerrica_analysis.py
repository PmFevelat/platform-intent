#!/usr/bin/env python3
"""
Script pour compléter toutes les analyses pour les 20 entreprises de Jerrica
"""

import csv
import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
MANTIKS_API_KEY = os.environ.get("MANTIKS_API_KEY")
if not MANTIKS_API_KEY:
    raise ValueError("MANTIKS_API_KEY environment variable is required")

# Les 7 entreprises sans jobs
COMPANIES_TO_ENRICH = [
    "Palliser Furniture Ltd.",
    "Article",
    "American Leather",
    "Serena & Lily",
    "Rowe Furniture",
    "Jonathan Louis",
    "Theodore Alexander"
]

# Mots-clés de recherche
JOB_KEYWORDS = [
    "digital strategy",
    "digital experience",
    "group design",
    "art",
    "graphic design",
    "sales",
    "revenue",
    "digital marketing",
    "international marketing",
    "product marketing",
    "group marketing",
    "brand marketing",
    "strategic marketing",
    "marketing",
    "ecommerce",
    "e-commerce",
    "digital",
    "creative",
    "group creative",
    "global creative"
]

def normalize_name(name):
    """Normalise les noms d'entreprises pour la comparaison"""
    return name.lower().replace(',', '').replace('.', '').replace('-', '').replace('&', 'and').replace('  ', ' ').strip()

def load_company_from_tam(company_name):
    """Charge les données d'une entreprise depuis TAM.csv"""
    normalized_target = normalize_name(company_name)
    
    with open('TAM.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_tam_name = row.get('CompanyName', '').strip()
            if normalize_name(company_tam_name) == normalized_target:
                return {
                    'name': company_tam_name,
                    'website': row.get('Website', '').strip(),
                    'linkedin': row.get('LinkedIn', '').strip(),
                    'industry': row.get('Sub Industry', '').strip(),
                    'employees': row.get('Employees', '').strip()
                }
    return None

def clean_url(url):
    """Nettoie l'URL pour l'API"""
    if not url:
        return url
    for suffix in ['/fr/', '/en/', '/de/', '/es/', '/it/']:
        if url.endswith(suffix):
            url = url[:-len(suffix)] + '/'
    return url

def fetch_jobs_for_company(company):
    """Récupère les offres d'emploi via l'API Mantiks"""
    headers = {
        'accept': 'application/json',
        'x-api-key': MANTIKS_API_KEY
    }
    
    website = clean_url(company['website'])
    
    params = [
        ('website', website),
        ('age_in_days', 365)
    ]
    
    for kw in JOB_KEYWORDS:
        params.append(('keyword', kw))
    
    if company['linkedin']:
        params.append(('linkedin_url', company['linkedin']))
    
    try:
        print(f"  📡 Appel API Mantiks pour {company['name']}...")
        response = requests.get(
            'https://api.mantiks.io/company/jobs',
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            print(f"  ✅ {len(jobs)} jobs trouvés")
            return jobs
        else:
            print(f"  ❌ Erreur API: {response.status_code}")
            return []
    except Exception as e:
        print(f"  ❌ Erreur: {str(e)}")
        return []

def save_to_jobs_data(company, jobs):
    """Sauvegarde les jobs dans jobs_data.json"""
    # Charger les données existantes
    try:
        with open('jobs_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    
    # Normaliser le nom de la clé
    company_key = company['name'].lower()
    
    # Créer l'entrée
    data[company_key] = {
        'name': company['name'],
        'website': company['website'],
        'linkedin': company['linkedin'],
        'industry': company['industry'],
        'employees': company['employees'],
        'jobs': jobs
    }
    
    # Sauvegarder
    with open('jobs_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"  💾 Données sauvegardées dans jobs_data.json")

def main():
    print("="*80)
    print("ENRICHISSEMENT DES JOBS POUR LES 7 ENTREPRISES MANQUANTES")
    print("="*80)
    
    for company_name in COMPANIES_TO_ENRICH:
        print(f"\n🏢 {company_name}")
        
        # Charger depuis TAM.csv
        company = load_company_from_tam(company_name)
        if not company:
            print(f"  ❌ Entreprise non trouvée dans TAM.csv")
            continue
        
        # Récupérer les jobs
        jobs = fetch_jobs_for_company(company)
        
        # Sauvegarder
        save_to_jobs_data(company, jobs)
        
        # Pause pour respecter les limites de l'API
        time.sleep(2)
    
    print("\n" + "="*80)
    print("✅ ENRICHISSEMENT TERMINÉ")
    print("="*80)
    print("\nProchaines étapes:")
    print("1. Analyser les jobs pour extraire le tech stack")
    print("2. Scraper les management interviews manquantes")

if __name__ == "__main__":
    main()

