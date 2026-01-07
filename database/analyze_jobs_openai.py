#!/usr/bin/env python3
"""
Script d'analyse des offres d'emploi avec OpenAI GPT-4
Objectif : Extraire les intents clés pour positionner presti.ai
Version ASYNC avec 6 workers parallèles
"""

import json
import asyncio
import time
import sys
import os
from datetime import datetime
import html
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

NUM_WORKERS = 6  # Nombre de workers parallèles

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Prompt système pour l'analyse
SYSTEM_PROMPT = """Tu es un expert en analyse de descriptions de poste pour identifier des opportunités commerciales B2B.

CONTEXTE :
presti.ai est un outil IA permettant aux entreprises de furniture/home decor de faire du photostaging et photoshooting réalistes à partir des photos de leurs produits. 
Proposition de valeur : générer des images avec produits intacts, en respectant la brand identity, at scale sur un catalogue entier, rapidement.

OBJECTIF :
Analyser chaque description de poste pour extraire 3 catégories d'informations clés qui aideront à positionner presti.ai auprès de ces entreprises.

Tu dois répondre UNIQUEMENT en JSON valide, sans markdown, avec la structure exacte suivante :
{
    "relevance_score": <score de 1 à 10 indiquant la pertinence de cette offre pour presti.ai>,
    "missions_fit": {
        "key_personas_mentioned": ["liste des personas clés mentionnés (marketing, e-commerce, design, creative, photo, content, etc.)"],
        "relevant_missions": ["liste des missions qui correspondent à la proposition de valeur de presti.ai"],
        "pain_points": ["points de douleur potentiels identifiés (scale, rapidité, cohérence visuelle, etc.)"],
        "summary": "résumé en 2-3 phrases des enjeux identifiés"
    },
    "team_structure": {
        "reports_to": "à qui le poste reporte (manager direct)",
        "collaborates_with": ["équipes/personnes avec qui le poste collabore"],
        "decision_makers": ["décideurs potentiels identifiés (C-level, VP, Director, etc.)"],
        "team_size_hint": "indication sur la taille de l'équipe si mentionnée"
    },
    "tools_ecosystem": {
        "design_tools": ["outils de design mentionnés (Photoshop, Illustrator, Figma, etc.)"],
        "3d_tools": ["outils 3D mentionnés (Blender, SketchUp, etc.)"],
        "ecommerce_platforms": ["plateformes e-commerce mentionnées (Shopify, Magento, etc.)"],
        "dam_pim_tools": ["outils DAM/PIM mentionnés"],
        "competitors_hints": ["indices sur les solutions concurrentes utilisées"],
        "other_tools": ["autres outils pertinents"]
    },
    "sales_insights": {
        "buying_signals": ["signaux d'achat identifiés"],
        "recommended_approach": "approche commerciale recommandée en 1-2 phrases",
        "key_talking_points": ["3 points clés à aborder lors d'un pitch"]
    }
}"""

USER_PROMPT_TEMPLATE = """Analyse cette description de poste pour l'entreprise "{company_name}" (industrie: {industry}).

TITRE DU POSTE : {job_title}
LOCALISATION : {location}

DESCRIPTION :
{description}

Extrais les informations selon les 3 catégories (missions_fit, team_structure, tools_ecosystem) + insights commerciaux.
Réponds UNIQUEMENT en JSON valide."""


async def analyze_job_with_openai(job, company_info, semaphore, retry_count=3):
    """Analyse une offre d'emploi avec OpenAI GPT-4 (async)"""
    
    user_prompt = USER_PROMPT_TEMPLATE.format(
        company_name=company_info['name'],
        industry=company_info['industry'],
        job_title=job.get('job_title', 'N/A'),
        location=job.get('location', 'N/A'),
        description=job.get('description', 'N/A')[:8000]
    )
    
    async with semaphore:  # Limite le nombre de requêtes simultanées
        for attempt in range(retry_count):
            try:
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                return {
                    'success': True,
                    'analysis': result,
                    'tokens_used': response.usage.total_tokens
                }
                
            except json.JSONDecodeError as e:
                if attempt < retry_count - 1:
                    await asyncio.sleep(1)
                    continue
                return {
                    'success': False,
                    'error': f"JSON parsing error: {str(e)}",
                    'analysis': None
                }
            except Exception as e:
                if attempt < retry_count - 1:
                    await asyncio.sleep(2)
                    continue
                return {
                    'success': False,
                    'error': str(e),
                    'analysis': None
                }
    
    return {'success': False, 'error': 'Max retries reached', 'analysis': None}


async def process_job(job_data, semaphore, progress_counter, total_jobs):
    """Traite un job et met à jour le compteur de progression"""
    result = await analyze_job_with_openai(
        {'job_title': job_data['job_title'], 'location': job_data['location'], 'description': job_data['description']},
        {'name': job_data['company_name'], 'industry': job_data['industry']},
        semaphore
    )
    
    job_result = job_data.copy()
    job_result['analysis_success'] = result['success']
    job_result['analysis'] = result.get('analysis')
    job_result['tokens_used'] = result.get('tokens_used', 0)
    
    # Mise à jour du compteur
    progress_counter['count'] += 1
    count = progress_counter['count']
    
    if result['success']:
        score = result['analysis'].get('relevance_score', 0)
        print(f"[{count}/{total_jobs}] ✅ {job_data['company_name'][:25]} - {job_data['job_title'][:30]}... Score: {score}/10")
    else:
        print(f"[{count}/{total_jobs}] ❌ {job_data['company_name'][:25]} - {result.get('error', 'Unknown')[:40]}")
    
    return job_result


def escape_html(text):
    """Échappe les caractères HTML"""
    if text is None:
        return ""
    return html.escape(str(text))


def format_list_html(items):
    """Formate une liste en HTML"""
    if not items or items == []:
        return '<span class="no-data">Non mentionné</span>'
    if isinstance(items, str):
        items = [items]
    return '<ul class="tag-list">' + ''.join(f'<li>{escape_html(item)}</li>' for item in items if item) + '</ul>'


def generate_analysis_report(analyzed_data, output_path):
    """Génère le rapport HTML d'analyse"""
    
    total_jobs = len(analyzed_data['jobs'])
    successful_analyses = sum(1 for j in analyzed_data['jobs'] if j.get('analysis_success'))
    high_relevance = sum(1 for j in analyzed_data['jobs'] if j.get('analysis') and j['analysis'].get('relevance_score', 0) >= 7)
    total_tokens = sum(j.get('tokens_used', 0) for j in analyzed_data['jobs'])
    
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>presti.ai - Job Analysis Report</title>
    <style>
        :root {{
            --bg-dark: #0f0f23;
            --bg-card: #1a1a2e;
            --bg-accent: #16213e;
            --text-primary: #eaeaea;
            --text-secondary: #a0a0a0;
            --accent-purple: #9d4edd;
            --accent-blue: #4cc9f0;
            --accent-green: #06ffa5;
            --accent-orange: #ff9e00;
            --accent-red: #ff5c5c;
            --accent-pink: #f72585;
            --border-color: #2a2a4a;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        header {{
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-accent) 100%);
            border-radius: 20px;
            margin-bottom: 2rem;
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }}
        
        header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(157, 78, 221, 0.1) 0%, transparent 50%);
            animation: pulse 4s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.5; }}
            50% {{ transform: scale(1.1); opacity: 0.8; }}
        }}
        
        .logo {{
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue), var(--accent-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            position: relative;
            z-index: 1;
        }}
        
        .subtitle {{
            color: var(--text-secondary);
            font-size: 1.2rem;
            position: relative;
            z-index: 1;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
            position: relative;
            z-index: 1;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.05);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--border-color);
        }}
        
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}
        
        .filters {{
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            align-items: center;
            padding: 1.5rem;
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }}
        
        .filters input, .filters select {{
            padding: 0.75rem 1rem;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: var(--bg-accent);
            color: var(--text-primary);
            font-size: 0.95rem;
            min-width: 200px;
        }}
        
        .filters input:focus, .filters select:focus {{
            outline: none;
            border-color: var(--accent-purple);
        }}
        
        .job-card {{
            background: var(--bg-card);
            border-radius: 16px;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .job-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 40px rgba(157, 78, 221, 0.1);
        }}
        
        .job-header {{
            padding: 1.5rem;
            background: var(--bg-accent);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        
        .job-title {{
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--accent-blue);
            margin-bottom: 0.5rem;
        }}
        
        .job-title a {{
            color: inherit;
            text-decoration: none;
        }}
        
        .job-title a:hover {{
            text-decoration: underline;
        }}
        
        .company-name {{
            color: var(--text-primary);
            font-weight: 500;
        }}
        
        .job-meta {{
            display: flex;
            gap: 1.5rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 0.5rem;
            flex-wrap: wrap;
        }}
        
        .relevance-badge {{
            padding: 0.5rem 1.2rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        .relevance-high {{
            background: linear-gradient(135deg, var(--accent-green), #00cc88);
            color: #000;
        }}
        
        .relevance-medium {{
            background: linear-gradient(135deg, var(--accent-orange), #ffb700);
            color: #000;
        }}
        
        .relevance-low {{
            background: var(--bg-accent);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }}
        
        .analysis-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            padding: 1.5rem;
        }}
        
        .analysis-section {{
            background: var(--bg-accent);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
        }}
        
        .section-title {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .section-title.missions {{ color: var(--accent-purple); }}
        .section-title.team {{ color: var(--accent-blue); }}
        .section-title.tools {{ color: var(--accent-green); }}
        .section-title.sales {{ color: var(--accent-pink); }}
        
        .tag-list {{
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        
        .tag-list li {{
            background: rgba(255,255,255,0.1);
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.85rem;
            color: var(--text-primary);
        }}
        
        .insight-box {{
            background: rgba(157, 78, 221, 0.1);
            border-left: 3px solid var(--accent-purple);
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin-top: 1rem;
        }}
        
        .insight-box h4 {{
            color: var(--accent-purple);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        
        .insight-box p {{
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .field-label {{
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-bottom: 0.3rem;
        }}
        
        .field-value {{
            color: var(--text-primary);
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }}
        
        .no-data {{
            color: var(--text-secondary);
            font-style: italic;
            font-size: 0.9rem;
        }}
        
        .talking-points {{
            background: rgba(247, 37, 133, 0.1);
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
        }}
        
        .talking-points h4 {{
            color: var(--accent-pink);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        
        .talking-points ol {{
            padding-left: 1.2rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}
        
        .talking-points li {{
            margin-bottom: 0.3rem;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 1rem; }}
            .logo {{ font-size: 2rem; }}
            .analysis-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">🎯 presti.ai</div>
            <p class="subtitle">Job Analysis Report - Sales Intelligence</p>
            <p class="subtitle" style="font-size: 0.9rem; margin-top: 0.5rem;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{total_jobs}</div>
                    <div class="stat-label">Jobs Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{successful_analyses}</div>
                    <div class="stat-label">Successful Analyses</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{high_relevance}</div>
                    <div class="stat-label">High Relevance (≥7/10)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_tokens:,}</div>
                    <div class="stat-label">Tokens Used</div>
                </div>
            </div>
        </header>
        
        <div class="filters">
            <input type="text" id="searchInput" placeholder="🔍 Search company, job title..." onkeyup="filterJobs()">
            <select id="relevanceFilter" onchange="filterJobs()">
                <option value="">All Relevance</option>
                <option value="high">High (≥7)</option>
                <option value="medium">Medium (4-6)</option>
                <option value="low">Low (≤3)</option>
            </select>
            <select id="sortBy" onchange="sortJobs()">
                <option value="relevance">Sort by Relevance</option>
                <option value="company">Sort by Company</option>
            </select>
        </div>
        
        <div id="jobsList">
'''

    # Trier par score de pertinence
    sorted_jobs = sorted(
        analyzed_data['jobs'],
        key=lambda x: x.get('analysis', {}).get('relevance_score', 0) if x.get('analysis') else 0,
        reverse=True
    )
    
    for job_data in sorted_jobs:
        analysis = job_data.get('analysis', {})
        if not analysis:
            continue
            
        relevance = analysis.get('relevance_score', 0)
        relevance_class = 'high' if relevance >= 7 else ('medium' if relevance >= 4 else 'low')
        
        missions = analysis.get('missions_fit', {})
        team = analysis.get('team_structure', {})
        tools = analysis.get('tools_ecosystem', {})
        sales = analysis.get('sales_insights', {})
        
        html_content += f'''
            <div class="job-card" data-relevance="{relevance}" data-company="{escape_html(job_data.get('company_name', '').lower())}" data-title="{escape_html(job_data.get('job_title', '').lower())}">
                <div class="job-header">
                    <div>
                        <div class="job-title">
                            <a href="{escape_html(job_data.get('job_url', '#'))}" target="_blank">{escape_html(job_data.get('job_title', 'N/A'))}</a>
                        </div>
                        <div class="company-name">🏢 {escape_html(job_data.get('company_name', 'N/A'))} • {escape_html(job_data.get('industry', 'N/A'))}</div>
                        <div class="job-meta">
                            <span>📍 {escape_html(job_data.get('location', 'N/A'))}</span>
                            <span>🌐 {escape_html(job_data.get('job_board', 'N/A'))}</span>
                            <span>📅 {escape_html(job_data.get('date', 'N/A'))}</span>
                        </div>
                    </div>
                    <div class="relevance-badge relevance-{relevance_class}">
                        ⭐ {relevance}/10
                    </div>
                </div>
                
                <div class="analysis-grid">
                    <div class="analysis-section">
                        <div class="section-title missions">🎯 Missions & Value Fit</div>
                        <div class="field-label">Key Personas Mentioned</div>
                        <div class="field-value">{format_list_html(missions.get('key_personas_mentioned', []))}</div>
                        <div class="field-label">Relevant Missions</div>
                        <div class="field-value">{format_list_html(missions.get('relevant_missions', []))}</div>
                        <div class="field-label">Pain Points Identified</div>
                        <div class="field-value">{format_list_html(missions.get('pain_points', []))}</div>
                        <div class="insight-box">
                            <h4>💡 Summary</h4>
                            <p>{escape_html(missions.get('summary', 'No summary available'))}</p>
                        </div>
                    </div>
                    
                    <div class="analysis-section">
                        <div class="section-title team">👥 Team Structure</div>
                        <div class="field-label">Reports To</div>
                        <div class="field-value">{escape_html(team.get('reports_to', 'Not mentioned')) or '<span class="no-data">Not mentioned</span>'}</div>
                        <div class="field-label">Collaborates With</div>
                        <div class="field-value">{format_list_html(team.get('collaborates_with', []))}</div>
                        <div class="field-label">🎯 Decision Makers</div>
                        <div class="field-value">{format_list_html(team.get('decision_makers', []))}</div>
                        <div class="field-label">Team Size</div>
                        <div class="field-value">{escape_html(team.get('team_size_hint', 'Not mentioned')) or '<span class="no-data">Not mentioned</span>'}</div>
                    </div>
                    
                    <div class="analysis-section">
                        <div class="section-title tools">🛠️ Tools Ecosystem</div>
                        <div class="field-label">Design Tools</div>
                        <div class="field-value">{format_list_html(tools.get('design_tools', []))}</div>
                        <div class="field-label">3D Tools</div>
                        <div class="field-value">{format_list_html(tools.get('3d_tools', []))}</div>
                        <div class="field-label">E-commerce Platforms</div>
                        <div class="field-value">{format_list_html(tools.get('ecommerce_platforms', []))}</div>
                        <div class="field-label">DAM/PIM Tools</div>
                        <div class="field-value">{format_list_html(tools.get('dam_pim_tools', []))}</div>
                        <div class="field-label">Competitor Hints</div>
                        <div class="field-value">{format_list_html(tools.get('competitors_hints', []))}</div>
                    </div>
                    
                    <div class="analysis-section">
                        <div class="section-title sales">💰 Sales Insights</div>
                        <div class="field-label">Buying Signals</div>
                        <div class="field-value">{format_list_html(sales.get('buying_signals', []))}</div>
                        <div class="insight-box" style="background: rgba(247, 37, 133, 0.1); border-left-color: var(--accent-pink);">
                            <h4>🚀 Recommended Approach</h4>
                            <p>{escape_html(sales.get('recommended_approach', 'No recommendation'))}</p>
                        </div>
                        <div class="talking-points">
                            <h4>💬 Key Talking Points</h4>
                            <ol>
                                {''.join(f'<li>{escape_html(point)}</li>' for point in sales.get('key_talking_points', []) if point)}
                            </ol>
                        </div>
                    </div>
                </div>
            </div>
'''

    html_content += '''
        </div>
    </div>
    
    <script>
        function filterJobs() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const relevance = document.getElementById('relevanceFilter').value;
            
            document.querySelectorAll('.job-card').forEach(card => {
                const company = card.dataset.company;
                const title = card.dataset.title;
                const score = parseInt(card.dataset.relevance);
                
                const matchSearch = !search || company.includes(search) || title.includes(search);
                
                let matchRelevance = true;
                if (relevance === 'high') matchRelevance = score >= 7;
                else if (relevance === 'medium') matchRelevance = score >= 4 && score < 7;
                else if (relevance === 'low') matchRelevance = score < 4;
                
                card.style.display = matchSearch && matchRelevance ? '' : 'none';
            });
        }
        
        function sortJobs() {
            const sortBy = document.getElementById('sortBy').value;
            const container = document.getElementById('jobsList');
            const cards = Array.from(container.querySelectorAll('.job-card'));
            
            cards.sort((a, b) => {
                if (sortBy === 'relevance') {
                    return parseInt(b.dataset.relevance) - parseInt(a.dataset.relevance);
                } else if (sortBy === 'company') {
                    return a.dataset.company.localeCompare(b.dataset.company);
                }
                return 0;
            });
            
            cards.forEach(card => container.appendChild(card));
        }
    </script>
</body>
</html>
'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Analysis report generated: {output_path}")


async def main():
    print("=" * 60)
    print("🎯 presti.ai - Job Analysis with OpenAI (ASYNC)")
    print(f"🚀 Using {NUM_WORKERS} parallel workers")
    print("=" * 60)
    
    start_time = time.time()
    
    # Charger les données collectées
    print("\n📂 Loading collected job data...")
    with open('jobs_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Préparer les données pour l'analyse
    jobs_to_analyze = []
    for company_data in data['companies']:
        if company_data.get('success') and company_data.get('nb_jobs', 0) > 0:
            company = company_data['company']
            for job in company_data['jobs']:
                jobs_to_analyze.append({
                    'company_name': company['name'],
                    'industry': company['industry'],
                    'employees': company['employees'],
                    'website': company['website'],
                    'job_title': job.get('job_title', ''),
                    'job_url': job.get('job_board_url', ''),
                    'job_board': job.get('job_board', ''),
                    'location': job.get('location', ''),
                    'date': job.get('date_creation', '')[:10] if job.get('date_creation') else '',
                    'description': job.get('description', '')
                })
    
    print(f"✅ Found {len(jobs_to_analyze)} jobs to analyze")
    
    # Créer un semaphore pour limiter les requêtes parallèles
    semaphore = asyncio.Semaphore(NUM_WORKERS)
    progress_counter = {'count': 0}
    
    # Analyser tous les jobs en parallèle
    print(f"\n🤖 Analyzing jobs with OpenAI GPT-4o-mini ({NUM_WORKERS} workers)...")
    print("-" * 60)
    
    tasks = [
        process_job(job, semaphore, progress_counter, len(jobs_to_analyze))
        for job in jobs_to_analyze
    ]
    
    analyzed_jobs = await asyncio.gather(*tasks)
    
    elapsed_time = time.time() - start_time
    
    # Calculer les stats
    total_tokens = sum(j.get('tokens_used', 0) for j in analyzed_jobs)
    successful = sum(1 for j in analyzed_jobs if j.get('analysis_success'))
    high_relevance = sum(1 for j in analyzed_jobs if j.get('analysis') and j['analysis'].get('relevance_score', 0) >= 7)
    
    # Sauvegarder les résultats
    analyzed_data = {
        'generated_at': datetime.now().isoformat(),
        'total_jobs': len(jobs_to_analyze),
        'total_tokens': total_tokens,
        'jobs': analyzed_jobs
    }
    
    # Sauvegarder en JSON
    json_path = 'jobs_analysis_results.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analyzed_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ JSON results saved: {json_path}")
    
    # Générer le rapport HTML
    print("\n📊 Generating HTML report...")
    html_path = 'jobs_analysis_report.html'
    generate_analysis_report(analyzed_data, html_path)
    
    # Résumé
    print("\n" + "=" * 60)
    print("📈 SUMMARY")
    print("=" * 60)
    print(f"   Jobs analyzed: {len(jobs_to_analyze)}")
    print(f"   Successful analyses: {successful}")
    print(f"   High relevance (≥7/10): {high_relevance}")
    print(f"   Total tokens used: {total_tokens:,}")
    print(f"   Estimated cost: ${total_tokens * 0.00015:.2f}")
    print(f"   ⏱️  Total time: {elapsed_time:.1f}s ({elapsed_time/len(jobs_to_analyze):.2f}s/job)")
    print(f"\n   Reports saved:")
    print(f"   - {json_path}")
    print(f"   - {html_path}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
