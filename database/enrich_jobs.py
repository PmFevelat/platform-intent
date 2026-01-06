#!/usr/bin/env python3
"""
Script d'enrichissement des offres d'emploi via l'API Mantiks
Pour les 50 premières entreprises US du fichier TAM.csv
"""

import csv
import requests
import json
import time
from datetime import datetime
import html

# Configuration API Mantiks
API_KEY = "gAAAAABpNqgBNC-71TSTMTTeFqP6TLDqHSCXnCCVRbkXOvdrOh3uqXwYsA7XtOGTo8lSp_VJWLxI76bQ5-jR0aGVpEXx1bk5iw=="
API_URL = "https://api.mantiks.io/company/jobs"

# Mots-clés de recherche pour les titres de poste
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

def load_us_companies(csv_path, limit=50):
    """Charge les entreprises US depuis le fichier CSV"""
    companies = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Country', '').strip() == 'United States':
                companies.append({
                    'name': row.get('CompanyName', '').strip(),
                    'website': row.get('Website', '').strip(),
                    'linkedin': row.get('LinkedIn', '').strip(),
                    'industry': row.get('Sub Industry', '').strip(),
                    'employees': row.get('Employees', '').strip()
                })
            if len(companies) >= limit:
                break
    return companies

def clean_url(url):
    """Nettoie l'URL pour l'API (retire les suffixes de langue, etc.)"""
    if not url:
        return url
    # Retirer les suffixes de langue courants
    for suffix in ['/fr/', '/en/', '/de/', '/es/', '/it/']:
        if url.endswith(suffix):
            url = url[:-len(suffix)] + '/'
    return url

def fetch_jobs_for_company(company):
    """Récupère les offres d'emploi pour une entreprise via l'API Mantiks"""
    headers = {
        'accept': 'application/json',
        'x-api-key': API_KEY
    }
    
    # Nettoyer l'URL du site web
    website = clean_url(company['website'])
    
    # Construire les paramètres - l'API attend des paramètres répétés pour les arrays
    # Utiliser une liste de tuples pour permettre les clés répétées
    params = [
        ('website', website),
        ('age_in_days', 365)  # Obligatoire - récupérer les offres de la dernière année
    ]
    
    # Ajouter chaque keyword séparément (format attendu par l'API)
    for kw in JOB_KEYWORDS:
        params.append(('keyword', kw))
    
    # Ajouter LinkedIn URL si disponible
    if company['linkedin']:
        params.append(('linkedin_url', company['linkedin']))
    
    try:
        response = requests.get(API_URL, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'jobs': data.get('jobs', []),
                'nb_jobs': data.get('nb_jobs', 0),
                'credits_remaining': data.get('credits_remaining'),
                'credits_cost': data.get('credits_cost', 0)
            }
        else:
            return {
                'success': False,
                'error': f"HTTP {response.status_code}: {response.text}",
                'jobs': [],
                'nb_jobs': 0
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'jobs': [],
            'nb_jobs': 0
        }

def calculate_age_in_days(date_str):
    """Calcule l'âge d'une offre en jours"""
    if not date_str:
        return None
    try:
        # Format: "2023-06-14T00:41:30.644058"
        job_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        now = datetime.now(job_date.tzinfo) if job_date.tzinfo else datetime.now()
        delta = now - job_date
        return delta.days
    except:
        return None

def escape_html(text):
    """Échappe les caractères HTML spéciaux"""
    if text is None:
        return ""
    return html.escape(str(text))

def truncate_description(description, max_length=500):
    """Tronque la description pour l'affichage"""
    if not description:
        return ""
    if len(description) <= max_length:
        return description
    return description[:max_length] + "..."

def generate_html_report(results, output_path):
    """Génère un rapport HTML avec tous les résultats"""
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Enrichment Report - US Companies</title>
    <style>
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --text-primary: #c9d1d9;
            --text-secondary: #8b949e;
            --accent-blue: #58a6ff;
            --accent-green: #3fb950;
            --accent-orange: #d29922;
            --accent-red: #f85149;
            --accent-purple: #a371f7;
            --border-color: #30363d;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 2rem;
        }
        
        .container {
            max-width: 1800px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
            border-radius: 16px;
            border: 1px solid var(--border-color);
        }
        
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }
        
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-top: 1.5rem;
            flex-wrap: wrap;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent-green);
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        
        .company-section {
            margin-bottom: 2rem;
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            overflow: hidden;
        }
        
        .company-header {
            padding: 1.5rem;
            background: var(--bg-tertiary);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        
        .company-name {
            font-size: 1.4rem;
            font-weight: 600;
            color: var(--accent-blue);
        }
        
        .company-meta {
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        
        .meta-item .icon {
            width: 16px;
            height: 16px;
        }
        
        .job-count-badge {
            background: var(--accent-green);
            color: var(--bg-primary);
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .no-jobs-badge {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        .error-badge {
            background: var(--accent-red);
            color: white;
            padding: 0.4rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        .jobs-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .jobs-table th {
            background: var(--bg-tertiary);
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: sticky;
            top: 0;
        }
        
        .jobs-table td {
            padding: 1rem;
            border-top: 1px solid var(--border-color);
            vertical-align: top;
        }
        
        .jobs-table tr:hover td {
            background: var(--bg-tertiary);
        }
        
        .job-title {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.3rem;
        }
        
        .job-title a {
            color: var(--accent-blue);
            text-decoration: none;
        }
        
        .job-title a:hover {
            text-decoration: underline;
        }
        
        .job-board {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            background: var(--bg-tertiary);
            border-radius: 4px;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }
        
        .job-board.linkedin {
            background: rgba(10, 102, 194, 0.2);
            color: #0a66c2;
        }
        
        .job-board.indeed {
            background: rgba(37, 87, 167, 0.2);
            color: #2557a7;
        }
        
        .job-location {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        .job-date {
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        
        .age-badge {
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .age-fresh {
            background: rgba(63, 185, 80, 0.2);
            color: var(--accent-green);
        }
        
        .age-recent {
            background: rgba(210, 153, 34, 0.2);
            color: var(--accent-orange);
        }
        
        .age-old {
            background: rgba(248, 81, 73, 0.2);
            color: var(--accent-red);
        }
        
        .description-cell {
            max-width: 500px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        
        .description-toggle {
            color: var(--accent-blue);
            cursor: pointer;
            font-size: 0.85rem;
            margin-top: 0.5rem;
            display: inline-block;
        }
        
        .description-full {
            display: none;
            margin-top: 0.5rem;
            padding: 1rem;
            background: var(--bg-tertiary);
            border-radius: 8px;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .no-jobs-message {
            padding: 2rem;
            text-align: center;
            color: var(--text-secondary);
        }
        
        .filter-bar {
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }
        
        .filter-bar input,
        .filter-bar select {
            padding: 0.75rem 1rem;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: var(--bg-tertiary);
            color: var(--text-primary);
            font-size: 0.95rem;
        }
        
        .filter-bar input:focus,
        .filter-bar select:focus {
            outline: none;
            border-color: var(--accent-blue);
        }
        
        .filter-bar input::placeholder {
            color: var(--text-secondary);
        }
        
        @media (max-width: 768px) {
            body {
                padding: 1rem;
            }
            
            h1 {
                font-size: 1.8rem;
            }
            
            .stats-bar {
                gap: 1.5rem;
            }
            
            .company-header {
                flex-direction: column;
                align-items: flex-start;
            }
            
            .jobs-table {
                display: block;
                overflow-x: auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Job Enrichment Report</h1>
            <p class="subtitle">US Companies - Mantiks API Data Collection</p>
            <p class="subtitle" style="margin-top: 0.5rem; font-size: 0.9rem;">Generated: ''' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '''</p>
            <div class="stats-bar">
                <div class="stat">
                    <div class="stat-value">''' + str(results['total_companies']) + '''</div>
                    <div class="stat-label">Companies Analyzed</div>
                </div>
                <div class="stat">
                    <div class="stat-value">''' + str(results['total_jobs']) + '''</div>
                    <div class="stat-label">Jobs Found</div>
                </div>
                <div class="stat">
                    <div class="stat-value">''' + str(results['companies_with_jobs']) + '''</div>
                    <div class="stat-label">Companies with Jobs</div>
                </div>
            </div>
        </header>
        
        <div class="filter-bar">
            <input type="text" id="searchInput" placeholder="🔍 Search jobs, companies..." onkeyup="filterResults()">
            <select id="boardFilter" onchange="filterResults()">
                <option value="">All Job Boards</option>
                <option value="linkedin">LinkedIn</option>
                <option value="indeed">Indeed</option>
                <option value="other">Other</option>
            </select>
            <select id="ageFilter" onchange="filterResults()">
                <option value="">All Ages</option>
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 90 days</option>
            </select>
        </div>
'''
    
    # Générer les sections pour chaque entreprise
    for company_result in results['companies']:
        company = company_result['company']
        jobs = company_result.get('jobs', [])
        nb_jobs = company_result.get('nb_jobs', 0)
        success = company_result.get('success', False)
        error = company_result.get('error', '')
        
        html_content += f'''
        <div class="company-section" data-company="{escape_html(company['name'].lower())}">
            <div class="company-header">
                <div>
                    <div class="company-name">{escape_html(company['name'])}</div>
                    <div class="company-meta">
                        <span class="meta-item">
                            <span>🌐</span>
                            <a href="{escape_html(company['website'])}" target="_blank" style="color: var(--text-secondary);">{escape_html(company['website'][:50])}...</a>
                        </span>
                        <span class="meta-item">
                            <span>🏢</span>
                            {escape_html(company['industry'])}
                        </span>
                        <span class="meta-item">
                            <span>👥</span>
                            {escape_html(company['employees'])} employees
                        </span>
                    </div>
                </div>
'''
        
        if not success:
            html_content += f'''
                <span class="error-badge">⚠️ Error: {escape_html(error[:50])}</span>
            </div>
            <div class="no-jobs-message">API call failed - {escape_html(error)}</div>
        </div>
'''
        elif nb_jobs == 0:
            html_content += '''
                <span class="no-jobs-badge">No matching jobs</span>
            </div>
            <div class="no-jobs-message">No jobs found matching the keywords</div>
        </div>
'''
        else:
            html_content += f'''
                <span class="job-count-badge">{nb_jobs} jobs found</span>
            </div>
            <table class="jobs-table">
                <thead>
                    <tr>
                        <th style="width: 25%;">Job Title</th>
                        <th style="width: 10%;">Job Board</th>
                        <th style="width: 15%;">Location</th>
                        <th style="width: 10%;">Date Posted</th>
                        <th style="width: 8%;">Age</th>
                        <th style="width: 32%;">Description</th>
                    </tr>
                </thead>
                <tbody>
'''
            for idx, job in enumerate(jobs):
                job_title = escape_html(job.get('job_title', 'N/A'))
                job_url = escape_html(job.get('job_board_url', '#'))
                job_board = job.get('job_board', 'unknown').lower()
                location = escape_html(job.get('location', 'N/A'))
                date_creation = job.get('date_creation', '')
                last_seen = job.get('last_seen', '')
                description = job.get('description', '')
                
                # Calculer l'âge
                age_days = calculate_age_in_days(date_creation)
                age_class = 'age-fresh' if age_days and age_days <= 7 else ('age-recent' if age_days and age_days <= 30 else 'age-old')
                age_text = f"{age_days} days" if age_days is not None else "N/A"
                
                # Formatter la date
                date_display = date_creation[:10] if date_creation else 'N/A'
                
                # Board class
                board_class = 'linkedin' if 'linkedin' in job_board else ('indeed' if 'indeed' in job_board else '')
                
                # Description tronquée
                desc_preview = escape_html(truncate_description(description, 200))
                desc_full = escape_html(description)
                
                job_id = f"job_{company['name'].replace(' ', '_')}_{idx}"
                
                html_content += f'''
                    <tr data-job-title="{job_title.lower()}" data-board="{job_board}" data-age="{age_days if age_days else 999}">
                        <td>
                            <div class="job-title">
                                <a href="{job_url}" target="_blank">{job_title}</a>
                            </div>
                        </td>
                        <td>
                            <span class="job-board {board_class}">{escape_html(job_board)}</span>
                        </td>
                        <td class="job-location">{location}</td>
                        <td class="job-date">{date_display}</td>
                        <td>
                            <span class="age-badge {age_class}">{age_text}</span>
                        </td>
                        <td class="description-cell">
                            <div class="desc-preview">{desc_preview}</div>
                            <span class="description-toggle" onclick="toggleDescription('{job_id}')">Show full description ▼</span>
                            <div id="{job_id}" class="description-full">{desc_full}</div>
                        </td>
                    </tr>
'''
            
            html_content += '''
                </tbody>
            </table>
        </div>
'''
    
    # Fermer le HTML
    html_content += '''
    </div>
    
    <script>
        function toggleDescription(id) {
            const elem = document.getElementById(id);
            const toggle = elem.previousElementSibling;
            if (elem.style.display === 'block') {
                elem.style.display = 'none';
                toggle.textContent = 'Show full description ▼';
            } else {
                elem.style.display = 'block';
                toggle.textContent = 'Hide description ▲';
            }
        }
        
        function filterResults() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const board = document.getElementById('boardFilter').value.toLowerCase();
            const ageLimit = parseInt(document.getElementById('ageFilter').value) || 9999;
            
            document.querySelectorAll('.company-section').forEach(section => {
                const companyName = section.dataset.company;
                const rows = section.querySelectorAll('tbody tr');
                let visibleRows = 0;
                
                rows.forEach(row => {
                    const jobTitle = row.dataset.jobTitle || '';
                    const jobBoard = row.dataset.board || '';
                    const jobAge = parseInt(row.dataset.age) || 9999;
                    
                    const matchSearch = !search || companyName.includes(search) || jobTitle.includes(search);
                    const matchBoard = !board || jobBoard.includes(board) || (board === 'other' && !['linkedin', 'indeed'].some(b => jobBoard.includes(b)));
                    const matchAge = jobAge <= ageLimit;
                    
                    if (matchSearch && matchBoard && matchAge) {
                        row.style.display = '';
                        visibleRows++;
                    } else {
                        row.style.display = 'none';
                    }
                });
                
                // Show/hide company section based on visible rows or search match
                const hasTable = section.querySelector('tbody');
                if (hasTable) {
                    section.style.display = visibleRows > 0 ? '' : 'none';
                } else {
                    section.style.display = companyName.includes(search) || !search ? '' : 'none';
                }
            });
        }
    </script>
</body>
</html>
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML report generated: {output_path}")

def main():
    print("=" * 60)
    print("🚀 Job Enrichment Script - Mantiks API")
    print("=" * 60)
    
    # Charger les entreprises US
    csv_path = "TAM.csv"
    print(f"\n📂 Loading US companies from {csv_path}...")
    companies = load_us_companies(csv_path, limit=50)
    print(f"✅ Loaded {len(companies)} US companies")
    
    # Afficher les mots-clés utilisés
    print(f"\n🔑 Keywords used for search:")
    for kw in JOB_KEYWORDS:
        print(f"   • {kw}")
    
    # Résultats
    results = {
        'total_companies': len(companies),
        'total_jobs': 0,
        'companies_with_jobs': 0,
        'companies': []
    }
    
    # Enrichir chaque entreprise
    print(f"\n🔍 Fetching jobs for each company...")
    print("-" * 60)
    
    for i, company in enumerate(companies, 1):
        print(f"[{i}/{len(companies)}] {company['name']}...", end=" ")
        
        result = fetch_jobs_for_company(company)
        result['company'] = company
        results['companies'].append(result)
        
        if result['success']:
            nb_jobs = result['nb_jobs']
            results['total_jobs'] += nb_jobs
            if nb_jobs > 0:
                results['companies_with_jobs'] += 1
            print(f"✅ {nb_jobs} jobs found")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown')[:50]}")
        
        # Petite pause pour éviter le rate limiting
        time.sleep(0.5)
    
    # Générer le rapport HTML
    print("\n" + "=" * 60)
    print("📊 Generating HTML report...")
    output_path = "jobs_enrichment_report.html"
    generate_html_report(results, output_path)
    
    # Sauvegarder les données JSON pour l'analyse OpenAI
    json_path = "jobs_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON data saved: {json_path}")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📈 SUMMARY")
    print("=" * 60)
    print(f"   Total companies analyzed: {results['total_companies']}")
    print(f"   Companies with matching jobs: {results['companies_with_jobs']}")
    print(f"   Total jobs found: {results['total_jobs']}")
    print(f"\n   Report saved to: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()

