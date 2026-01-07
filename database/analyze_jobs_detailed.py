#!/usr/bin/env python3
"""
Script d'analyse détaillée des offres d'emploi avec OpenAI
Sauvegarde incrémentale + extraction des preuves
"""

import json
import asyncio
import sys
import os
from datetime import datetime
from openai import AsyncOpenAI
from dotenv import load_dotenv

sys.stdout.reconfigure(line_buffering=True)

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

NUM_WORKERS = 6
OUTPUT_FILE = "jobs_analysis_detailed.json"

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """Tu es un expert en analyse de descriptions de poste pour identifier des opportunités commerciales B2B.

CONTEXTE :
presti.ai est un outil IA permettant aux entreprises de furniture/home decor de faire du photostaging et photoshooting réalistes à partir des photos de leurs produits. 
Proposition de valeur : générer des images avec produits intacts, en respectant la brand identity, at scale sur un catalogue entier, rapidement.

OBJECTIF :
Analyser la description de poste pour extraire 3 catégories d'informations + des citations exactes de la description comme preuves.

IMPORTANT: Pour chaque information trouvée, tu DOIS inclure une citation exacte (verbatim) de la description originale comme preuve. Si rien n'est trouvé pour un champ, laisse un tableau vide [].

Réponds UNIQUEMENT en JSON valide avec cette structure :
{
    "relevance_score": <1-10>,
    "missions_fit": {
        "key_personas": [{"name": "persona", "evidence": "citation exacte de la description"}],
        "relevant_missions": [{"mission": "description de la mission", "evidence": "citation exacte"}],
        "pain_points": [{"pain": "point de douleur", "evidence": "citation exacte"}],
        "summary": "résumé 2-3 phrases"
    },
    "team_structure": {
        "reports_to": {"role": "titre du manager", "evidence": "citation exacte"},
        "collaborates_with": [{"team": "équipe", "evidence": "citation exacte"}],
        "decision_makers": [{"role": "titre", "evidence": "citation exacte"}],
        "team_info": "info sur l'équipe si mentionnée"
    },
    "tools_ecosystem": {
        "design_tools": [{"tool": "nom", "evidence": "citation exacte"}],
        "3d_tools": [{"tool": "nom", "evidence": "citation exacte"}],
        "ecommerce_platforms": [{"platform": "nom", "evidence": "citation exacte"}],
        "other_tools": [{"tool": "nom", "evidence": "citation exacte"}]
    },
    "sales_recommendation": "approche commerciale recommandée en 2-3 phrases"
}"""

USER_PROMPT = """Analyse cette description de poste:

ENTREPRISE: {company}
TITRE: {title}
LOCALISATION: {location}

DESCRIPTION COMPLÈTE:
{description}

Extrais les informations avec des citations exactes comme preuves."""


async def analyze_job(job_data, semaphore):
    """Analyse un job avec OpenAI"""
    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT.format(
                        company=job_data['company_name'],
                        title=job_data['job_title'],
                        location=job_data.get('location', 'N/A'),
                        description=job_data['description'][:10000]
                    )}
                ],
                temperature=0.2,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return {
                'success': True,
                'analysis': analysis,
                'tokens': response.usage.total_tokens
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'analysis': None}


async def process_and_save(jobs, output_file):
    """Traite les jobs et sauvegarde au fur et à mesure"""
    semaphore = asyncio.Semaphore(NUM_WORKERS)
    
    # Charger les résultats existants si présents
    results = {'companies': {}, 'metadata': {'started': datetime.now().isoformat()}}
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            results = json.load(f)
        print(f"📂 Reprise depuis {len(results.get('companies', {}))} entreprises existantes")
    
    # Identifier les jobs déjà analysés
    analyzed_jobs = set()
    for company_data in results.get('companies', {}).values():
        for job in company_data.get('jobs', []):
            analyzed_jobs.add(job.get('job_url', ''))
    
    # Filtrer les jobs à analyser
    jobs_to_analyze = [j for j in jobs if j.get('job_url', '') not in analyzed_jobs]
    print(f"📊 {len(jobs_to_analyze)} jobs à analyser (sur {len(jobs)} total)")
    
    if not jobs_to_analyze:
        print("✅ Tous les jobs ont déjà été analysés!")
        return results
    
    total = len(jobs_to_analyze)
    completed = 0
    
    async def process_job(job):
        nonlocal completed
        result = await analyze_job(job, semaphore)
        completed += 1
        
        company = job['company_name']
        if company not in results['companies']:
            results['companies'][company] = {
                'name': company,
                'industry': job.get('industry', ''),
                'website': job.get('website', ''),
                'employees': job.get('employees', ''),
                'jobs': []
            }
        
        job_result = {
            'job_title': job['job_title'],
            'job_url': job.get('job_url', ''),
            'job_board': job.get('job_board', ''),
            'location': job.get('location', ''),
            'date': job.get('date', ''),
            'description': job['description'],
            'analysis': result.get('analysis'),
            'success': result['success']
        }
        
        results['companies'][company]['jobs'].append(job_result)
        
        # Sauvegarder après chaque job
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        if result['success']:
            score = result['analysis'].get('relevance_score', 0)
            print(f"[{completed}/{total}] ✅ {company[:25]} - {job['job_title'][:30]}... Score: {score}/10")
        else:
            print(f"[{completed}/{total}] ❌ {company[:25]} - {result.get('error', '')[:40]}")
        
        return job_result
    
    # Lancer les analyses en parallèle par batches
    batch_size = 20
    for i in range(0, len(jobs_to_analyze), batch_size):
        batch = jobs_to_analyze[i:i+batch_size]
        await asyncio.gather(*[process_job(job) for job in batch])
        await asyncio.sleep(0.5)  # Pause entre batches
    
    results['metadata']['completed'] = datetime.now().isoformat()
    results['metadata']['total_jobs'] = sum(len(c['jobs']) for c in results['companies'].values())
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results


def generate_html_report(results, output_path):
    """Génère le rapport HTML détaillé avec une page par entreprise"""
    
    companies = results.get('companies', {})
    total_jobs = sum(len(c['jobs']) for c in companies.values())
    high_relevance = sum(1 for c in companies.values() for j in c['jobs'] 
                        if j.get('analysis', {}).get('relevance_score', 0) >= 7)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>presti.ai - Sales Intelligence Report</title>
    <style>
        :root {{
            --bg-dark: #0a0a1a;
            --bg-card: #12122a;
            --bg-section: #1a1a3a;
            --text-primary: #f0f0f0;
            --text-secondary: #8888aa;
            --accent-purple: #8b5cf6;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-orange: #f59e0b;
            --accent-pink: #ec4899;
            --border: #2a2a4a;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .sidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 280px;
            height: 100vh;
            background: var(--bg-card);
            border-right: 1px solid var(--border);
            overflow-y: auto;
            padding: 1rem;
        }}
        .sidebar-header {{
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            margin-bottom: 1rem;
        }}
        .logo {{
            font-size: 1.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .company-list {{
            list-style: none;
        }}
        .company-link {{
            display: block;
            padding: 0.75rem 1rem;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 0.25rem;
            transition: all 0.2s;
        }}
        .company-link:hover, .company-link.active {{
            background: var(--bg-section);
            color: var(--text-primary);
        }}
        .company-link .job-count {{
            float: right;
            background: var(--accent-purple);
            color: white;
            padding: 0.1rem 0.5rem;
            border-radius: 10px;
            font-size: 0.8rem;
        }}
        .main-content {{
            margin-left: 280px;
            padding: 2rem;
        }}
        .company-section {{
            display: none;
            animation: fadeIn 0.3s ease;
        }}
        .company-section.active {{ display: block; }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        .company-header {{
            background: linear-gradient(135deg, var(--bg-card), var(--bg-section));
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
        }}
        .company-name {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        .company-meta {{
            color: var(--text-secondary);
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
        }}
        .job-card {{
            background: var(--bg-card);
            border-radius: 16px;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
            overflow: hidden;
        }}
        .job-header {{
            padding: 1.5rem;
            background: var(--bg-section);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            cursor: pointer;
        }}
        .job-header:hover {{ background: #1f1f4a; }}
        .job-title {{
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--accent-blue);
        }}
        .job-title a {{ color: inherit; text-decoration: none; }}
        .job-title a:hover {{ text-decoration: underline; }}
        .score-badge {{
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
        }}
        .score-high {{ background: var(--accent-green); color: #000; }}
        .score-medium {{ background: var(--accent-orange); color: #000; }}
        .score-low {{ background: var(--border); color: var(--text-secondary); }}
        .job-details {{
            padding: 1.5rem;
            display: none;
        }}
        .job-details.open {{ display: block; }}
        .analysis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
        }}
        .analysis-section {{
            background: var(--bg-section);
            border-radius: 12px;
            padding: 1.5rem;
        }}
        .section-title {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .section-title.value {{ color: var(--accent-purple); }}
        .section-title.team {{ color: var(--accent-blue); }}
        .section-title.tools {{ color: var(--accent-green); }}
        .evidence-item {{
            margin-bottom: 1rem;
            padding: 1rem;
            background: rgba(0,0,0,0.2);
            border-radius: 8px;
            border-left: 3px solid var(--accent-purple);
        }}
        .evidence-label {{
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }}
        .evidence-quote {{
            color: var(--text-secondary);
            font-style: italic;
            font-size: 0.9rem;
            padding: 0.5rem;
            background: rgba(139, 92, 246, 0.1);
            border-radius: 4px;
            margin-top: 0.5rem;
        }}
        .no-data {{
            color: var(--text-secondary);
            font-style: italic;
            padding: 1rem;
            text-align: center;
        }}
        .recommendation-box {{
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(59, 130, 246, 0.2));
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 1.5rem;
            border: 1px solid var(--accent-purple);
        }}
        .recommendation-title {{
            color: var(--accent-pink);
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        .stats-bar {{
            display: flex;
            gap: 1rem;
            margin: 1rem 0;
            flex-wrap: wrap;
        }}
        .stat-item {{
            background: var(--bg-section);
            padding: 0.75rem 1.25rem;
            border-radius: 8px;
        }}
        .stat-value {{ font-weight: 700; color: var(--accent-green); }}
        .toggle-all {{
            background: var(--accent-purple);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 1rem;
        }}
        .toggle-all:hover {{ background: #7c4ddb; }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <div class="logo">🎯 presti.ai</div>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">Sales Intelligence</p>
            <div class="stats-bar">
                <div class="stat-item"><span class="stat-value">{total_jobs}</span> jobs</div>
                <div class="stat-item"><span class="stat-value">{high_relevance}</span> high rel.</div>
            </div>
        </div>
        <ul class="company-list">
'''
    
    # Trier les entreprises par score moyen
    company_scores = []
    for name, data in companies.items():
        scores = [j.get('analysis', {}).get('relevance_score', 0) for j in data['jobs'] if j.get('analysis')]
        avg = sum(scores) / len(scores) if scores else 0
        company_scores.append((name, data, avg, len(data['jobs'])))
    
    company_scores.sort(key=lambda x: x[2], reverse=True)
    
    for i, (name, data, avg, job_count) in enumerate(company_scores):
        active = 'active' if i == 0 else ''
        html += f'''
            <li>
                <a href="#" class="company-link {active}" onclick="showCompany('{name.replace("'", "\\'")}'); return false;">
                    {name[:25]}{'...' if len(name) > 25 else ''}
                    <span class="job-count">{job_count}</span>
                </a>
            </li>
'''
    
    html += '''
        </ul>
    </div>
    <div class="main-content">
'''
    
    # Générer une section pour chaque entreprise
    for i, (name, data, avg, job_count) in enumerate(company_scores):
        active = 'active' if i == 0 else ''
        html += f'''
        <div class="company-section {active}" id="company-{name.replace(' ', '-').replace("'", '')}">
            <div class="company-header">
                <h1 class="company-name">{name}</h1>
                <div class="company-meta">
                    <span>🏢 {data.get('industry', 'N/A')}</span>
                    <span>👥 {data.get('employees', 'N/A')} employees</span>
                    <span>🌐 <a href="{data.get('website', '#')}" target="_blank" style="color: var(--accent-blue);">{data.get('website', 'N/A')[:40]}</a></span>
                    <span>⭐ Avg Score: {avg:.1f}/10</span>
                </div>
            </div>
            <button class="toggle-all" onclick="toggleAllJobs('{name.replace("'", "\\'")}')">📂 Expand/Collapse All Jobs</button>
'''
        
        # Trier les jobs par score
        sorted_jobs = sorted(data['jobs'], key=lambda x: x.get('analysis', {}).get('relevance_score', 0), reverse=True)
        
        for j, job in enumerate(sorted_jobs):
            analysis = job.get('analysis', {})
            score = analysis.get('relevance_score', 0)
            score_class = 'score-high' if score >= 8 else ('score-medium' if score >= 6 else 'score-low')
            job_id = f"{name.replace(' ', '-')}-job-{j}"
            
            html += f'''
            <div class="job-card" data-company="{name}">
                <div class="job-header" onclick="toggleJob('{job_id}')">
                    <div>
                        <div class="job-title">
                            <a href="{job.get('job_url', '#')}" target="_blank" onclick="event.stopPropagation();">{job.get('job_title', 'N/A')}</a>
                        </div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.25rem;">
                            📍 {job.get('location', 'N/A')} • 🌐 {job.get('job_board', 'N/A')} • 📅 {job.get('date', 'N/A')[:10] if job.get('date') else 'N/A'}
                        </div>
                    </div>
                    <div class="score-badge {score_class}">⭐ {score}/10</div>
                </div>
                <div class="job-details" id="{job_id}">
                    <div class="analysis-grid">
'''
            
            # Section Value Proposition
            missions = analysis.get('missions_fit', {})
            html += '''
                        <div class="analysis-section">
                            <div class="section-title value">🎯 Value Proposition Fit</div>
'''
            
            # Key personas
            personas = missions.get('key_personas', [])
            if personas:
                html += '<div class="evidence-label">Key Personas</div>'
                for p in personas[:5]:
                    if isinstance(p, dict):
                        html += f'''<div class="evidence-item">
                            <strong>{p.get('name', 'N/A')}</strong>
                            <div class="evidence-quote">"{p.get('evidence', 'No evidence')[:200]}"</div>
                        </div>'''
            
            # Relevant missions
            relevant = missions.get('relevant_missions', [])
            if relevant:
                html += '<div class="evidence-label" style="margin-top: 1rem;">Relevant Missions</div>'
                for m in relevant[:3]:
                    if isinstance(m, dict):
                        html += f'''<div class="evidence-item">
                            <strong>{m.get('mission', 'N/A')[:100]}</strong>
                            <div class="evidence-quote">"{m.get('evidence', 'No evidence')[:200]}"</div>
                        </div>'''
            
            # Pain points
            pains = missions.get('pain_points', [])
            if pains:
                html += '<div class="evidence-label" style="margin-top: 1rem;">Pain Points</div>'
                for p in pains[:3]:
                    if isinstance(p, dict):
                        html += f'''<div class="evidence-item">
                            <strong>{p.get('pain', 'N/A')}</strong>
                            <div class="evidence-quote">"{p.get('evidence', 'No evidence')[:200]}"</div>
                        </div>'''
            
            if not personas and not relevant and not pains:
                html += '<div class="no-data">No value proposition insights found</div>'
            
            html += '</div>'
            
            # Section Team Structure
            team = analysis.get('team_structure', {})
            html += '''
                        <div class="analysis-section">
                            <div class="section-title team">👥 Team Structure</div>
'''
            
            reports = team.get('reports_to', {})
            if reports and isinstance(reports, dict) and reports.get('role'):
                html += f'''<div class="evidence-item">
                    <div class="evidence-label">Reports To</div>
                    <strong>{reports.get('role', 'N/A')}</strong>
                    <div class="evidence-quote">"{reports.get('evidence', 'No evidence')[:200]}"</div>
                </div>'''
            
            collabs = team.get('collaborates_with', [])
            if collabs:
                html += '<div class="evidence-label" style="margin-top: 1rem;">Collaborates With</div>'
                for c in collabs[:5]:
                    if isinstance(c, dict):
                        html += f'''<div class="evidence-item">
                            <strong>{c.get('team', 'N/A')}</strong>
                            <div class="evidence-quote">"{c.get('evidence', 'No evidence')[:200]}"</div>
                        </div>'''
            
            makers = team.get('decision_makers', [])
            if makers:
                html += '<div class="evidence-label" style="margin-top: 1rem;">🎯 Decision Makers</div>'
                for d in makers[:5]:
                    if isinstance(d, dict):
                        html += f'''<div class="evidence-item">
                            <strong>{d.get('role', 'N/A')}</strong>
                            <div class="evidence-quote">"{d.get('evidence', 'No evidence')[:200]}"</div>
                        </div>'''
            
            if not reports and not collabs and not makers:
                html += '<div class="no-data">No team structure insights found</div>'
            
            html += '</div>'
            
            # Section Tools
            tools = analysis.get('tools_ecosystem', {})
            html += '''
                        <div class="analysis-section">
                            <div class="section-title tools">🛠️ Tools Ecosystem</div>
'''
            
            design_tools = tools.get('design_tools', [])
            if design_tools:
                html += '<div class="evidence-label">Design Tools</div>'
                for t in design_tools[:5]:
                    if isinstance(t, dict):
                        html += f'''<div class="evidence-item">
                            <strong>{t.get('tool', 'N/A')}</strong>
                            <div class="evidence-quote">"{t.get('evidence', 'No evidence')[:200]}"</div>
                        </div>'''
            
            tools_3d = tools.get('3d_tools', [])
            if tools_3d:
                html += '<div class="evidence-label" style="margin-top: 1rem;">3D Tools</div>'
                for t in tools_3d[:5]:
                    if isinstance(t, dict):
                        html += f'''<div class="evidence-item">
                            <strong>{t.get('tool', 'N/A')}</strong>
                            <div class="evidence-quote">"{t.get('evidence', 'No evidence')[:200]}"</div>
                        </div>'''
            
            ecom = tools.get('ecommerce_platforms', [])
            if ecom:
                html += '<div class="evidence-label" style="margin-top: 1rem;">E-commerce</div>'
                for e in ecom[:5]:
                    if isinstance(e, dict):
                        html += f'''<div class="evidence-item">
                            <strong>{e.get('platform', 'N/A')}</strong>
                            <div class="evidence-quote">"{e.get('evidence', 'No evidence')[:200]}"</div>
                        </div>'''
            
            other = tools.get('other_tools', [])
            if other:
                html += '<div class="evidence-label" style="margin-top: 1rem;">Other Tools</div>'
                for o in other[:5]:
                    if isinstance(o, dict):
                        html += f'''<div class="evidence-item">
                            <strong>{o.get('tool', 'N/A')}</strong>
                            <div class="evidence-quote">"{o.get('evidence', 'No evidence')[:200]}"</div>
                        </div>'''
            
            if not design_tools and not tools_3d and not ecom and not other:
                html += '<div class="no-data">No tools insights found</div>'
            
            html += '</div>'
            
            html += '''
                    </div>
'''
            
            # Recommendation
            rec = analysis.get('sales_recommendation', '')
            if rec:
                html += f'''
                    <div class="recommendation-box">
                        <div class="recommendation-title">💡 Sales Recommendation</div>
                        <p>{rec}</p>
                    </div>
'''
            
            html += '''
                </div>
            </div>
'''
        
        html += '''
        </div>
'''
    
    html += '''
    </div>
    <script>
        function showCompany(name) {
            document.querySelectorAll('.company-section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.company-link').forEach(l => l.classList.remove('active'));
            
            const id = 'company-' + name.replace(/ /g, '-').replace(/'/g, '');
            document.getElementById(id).classList.add('active');
            event.target.classList.add('active');
        }
        
        function toggleJob(id) {
            document.getElementById(id).classList.toggle('open');
        }
        
        function toggleAllJobs(company) {
            const cards = document.querySelectorAll(`.job-card[data-company="${company}"] .job-details`);
            const allOpen = Array.from(cards).every(c => c.classList.contains('open'));
            cards.forEach(c => {
                if (allOpen) c.classList.remove('open');
                else c.classList.add('open');
            });
        }
    </script>
</body>
</html>
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ HTML report saved: {output_path}")


async def main():
    print("=" * 60)
    print("🎯 presti.ai - Detailed Job Analysis")
    print(f"🚀 {NUM_WORKERS} parallel workers")
    print("=" * 60)
    
    # Charger les données
    with open('jobs_data.json', 'r') as f:
        data = json.load(f)
    
    jobs = []
    for company_data in data['companies']:
        if company_data.get('success') and company_data.get('nb_jobs', 0) > 0:
            company = company_data['company']
            for job in company_data['jobs']:
                jobs.append({
                    'company_name': company['name'],
                    'industry': company['industry'],
                    'employees': company['employees'],
                    'website': company['website'],
                    'job_title': job.get('job_title', ''),
                    'job_url': job.get('job_board_url', ''),
                    'job_board': job.get('job_board', ''),
                    'location': job.get('location', ''),
                    'date': job.get('date_creation', ''),
                    'description': job.get('description', '')
                })
    
    print(f"📊 {len(jobs)} jobs to analyze")
    
    # Analyser et sauvegarder
    results = await process_and_save(jobs, OUTPUT_FILE)
    
    # Générer le rapport HTML
    print("\n📊 Generating HTML report...")
    generate_html_report(results, 'jobs_analysis_detailed.html')
    
    print("\n" + "=" * 60)
    print("✅ DONE!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

