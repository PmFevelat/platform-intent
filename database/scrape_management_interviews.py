"""
Script ASYNCHRONE pour scraper les interviews et articles du management des entreprises
Focus sur les décideurs clés : E-commerce, Marketing, Digital, Design, Creative, Art Direction
"""

import json
import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
MAX_CONCURRENT_REQUESTS = 5  # Nombre de requêtes simultanées
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def get_management_interviews(company_name: str, company_website: str = "", industry: str = "") -> Dict[str, Any]:
    """
    Récupère les interviews et articles du management d'une entreprise en utilisant OpenAI Web Search (ASYNC)
    
    Args:
        company_name: Nom de l'entreprise
        company_website: Site web de l'entreprise (optionnel)
        industry: Industrie de l'entreprise (optionnel)
        
    Returns:
        Dict contenant les interviews structurées
    """
    
    print(f"\n🎤 Recherche des interviews management pour {company_name}...")
    
    # Build the prompt to target management interviews
    prompt = f"""You are an expert in researching executive interviews and leadership content for business intelligence.

Target company: {company_name}
Industry: {industry if industry else "Not specified"}
Website: {company_website if company_website else "Not specified"}

Context: Presti is an AI solution that helps home & furniture companies generate lifestyle product images at scale, independently of their supply chain. We need to understand the strategic priorities and vision of key decision-makers to tailor our sales approach.

TARGET PERSONAS & JOB TITLES TO FOCUS ON:

🎯 **PRIMARY TARGETS** (C-Level & VPs in relevant functions):
- CEO / Chief Executive Officer / President / Managing Director
- CMO / Chief Marketing Officer / VP Marketing / Head of Marketing
- CDO / Chief Digital Officer / VP Digital / Digital Director
- Chief E-commerce Officer / VP E-commerce / E-commerce Director / Head of E-commerce
- CTO / Chief Technology Officer / VP Technology / Head of Technology
- Chief Creative Officer / Creative Director / VP Creative
- Chief Design Officer / VP Design / Design Director / Head of Design
- VP Innovation / Innovation Director
- VP Brand / Brand Director / Head of Brand
- VP Product / Product Director
- VP Content / Content Director

🎯 **SECONDARY TARGETS** (Directors & Managers):
- Director of E-commerce / E-commerce Manager
- Director of Digital Marketing / Digital Marketing Manager
- Director of Content / Content Manager
- Director of Product Marketing
- Director of Visual Merchandising
- Director of Customer Experience
- Art Director
- Photography Director / Head of Photography

⚠️⚠️⚠️ CRITICAL DATE REQUIREMENT - ABSOLUTE RULE ⚠️⚠️⚠️
- ONLY include content from 2020, 2021, 2022, 2023, 2024 (ideally last 18-24 months)
- ❌ NEVER INCLUDE content from 2019 or earlier (2019, 2018, 2017, 2016, 2015, 2014, 2013, etc.)
- ❌ If publication date is before January 1, 2020 → DO NOT INCLUDE IT
- The business landscape pre-COVID (before 2020) is completely different and irrelevant
- This is a HARD CUTOFF - no exceptions, no "highly relevant" pre-2020 content

IMPORTANT: Provide ALL content in ENGLISH ONLY.

🔍 WEB SEARCH METHODOLOGY - MANAGEMENT INTERVIEWS:

You have access to web search. Use it EXTENSIVELY with MULTIPLE search patterns focused on PEOPLE and INTERVIEWS.

**SEARCH PATTERN 1 - Executive Interviews by Title:**
Target specific C-level and VP positions:
- "{company_name} CEO interview"
- "{company_name} CMO interview"
- "{company_name} Chief Digital Officer interview"
- "{company_name} VP E-commerce interview"
- "{company_name} Chief Marketing Officer"
- "{company_name} VP Digital"
- "{company_name} Creative Director interview"
- "{company_name} Chief Design Officer"
- "{company_name} President interview"

**SEARCH PATTERN 2 - Strategic Topics + Company:**
Find articles where executives discuss strategy:
- "{company_name} digital strategy"
- "{company_name} e-commerce strategy"
- "{company_name} marketing strategy"
- "{company_name} innovation strategy"
- "{company_name} technology roadmap"
- "{company_name} brand vision"
- "{company_name} customer experience strategy"
- "{company_name} visual content strategy"

**SEARCH PATTERN 3 - Speaking Engagements & Events:**
Executives often share insights at events:
- "{company_name} conference" OR "{company_name} keynote"
- "{company_name} speaker" OR "{company_name} panel"
- "{company_name} webinar"
- "{company_name} podcast"
- "{company_name} presentation"
- "{company_name} KBIS speaker"
- "{company_name} High Point Market speaker"

**SEARCH PATTERN 4 - Leadership & Vision:**
Articles about leadership and company direction:
- "{company_name} leadership"
- "{company_name} executive team"
- "{company_name} vision"
- "{company_name} CEO on"
- "{company_name} CMO on"
- "{company_name} leader profile"
- "{company_name} executive profile"

**SEARCH PATTERN 5 - Thought Leadership:**
Op-eds, guest articles, LinkedIn posts:
- "{company_name} LinkedIn"
- "{company_name} thought leadership"
- "{company_name} executive insights"
- "{company_name} opinion"
- "{company_name} perspective"

**SEARCH PATTERN 6 - Media Mentions:**
Interviews in major publications:
- "{company_name} Forbes interview"
- "{company_name} WWD interview"
- "{company_name} Business of Home interview"
- "{company_name} Furniture Today interview"
- "{company_name} Modern Retail interview"
- "{company_name} Retail Dive interview"

**SEARCH PATTERN 7 - Company Blog & Press:**
First-party content from the company:
- "site:{company_website} leadership" (if website provided)
- "site:{company_website} team" (if website provided)
- "{company_name} blog leadership"
- "{company_name} press interview"

⚡ MANDATORY SEARCH STRATEGY - MINIMUM 10-15 SEARCHES:

1️⃣ **Executive Interviews (4-5 searches):**
   - "{company_name} CEO interview"
   - "{company_name} CMO interview" OR "{company_name} Chief Marketing Officer"
   - "{company_name} CDO interview" OR "{company_name} Chief Digital Officer"
   - "{company_name} VP E-commerce" OR "{company_name} E-commerce Director"
   - "{company_name} Creative Director" OR "{company_name} Chief Design Officer"

2️⃣ **Strategic Topics (3-4 searches):**
   - "{company_name} digital strategy"
   - "{company_name} e-commerce strategy"
   - "{company_name} marketing strategy"
   - "{company_name} innovation"

3️⃣ **Media & Publications (2-3 searches):**
   - "{company_name} Forbes interview"
   - "{company_name} Business of Home interview"
   - "{company_name} WWD" OR "{company_name} Furniture Today"

4️⃣ **Events & Speaking (2 searches):**
   - "{company_name} conference" OR "{company_name} speaker"
   - "{company_name} podcast" OR "{company_name} webinar"

5️⃣ **Company Sources (2 searches):**
   - "{company_name} LinkedIn"
   - "{company_name} blog" OR "{company_name} leadership"

🎯 EXECUTION APPROACH:
- Start with C-LEVEL searches (CEO, CMO, CDO)
- Then search by STRATEGIC TOPICS (digital, e-commerce, marketing)
- Check TRADE PUBLICATIONS (they love interviewing executives!)
- Look for SPEAKING ENGAGEMENTS and conferences
- Mine COMPANY SOURCES (blog, LinkedIn)

📰 WHAT TO LOOK FOR:

✅ **DEFINITELY INCLUDE:**
- Executive interviews (any format: video, podcast, written)
- Conference talks and keynote speeches
- Panel discussions featuring company leaders
- Op-eds and thought leadership articles by executives
- Profile pieces about company leaders
- Strategic announcements with executive quotes
- LinkedIn posts by executives (if substantive)
- Podcast appearances
- Webinar presentations
- Award acceptance speeches with insights
- Executive quotes in major news articles about the company

✅ **CONTENT QUALITY:**
- Must contain ACTUAL INSIGHTS or STRATEGIC DIRECTION
- Must quote or feature a named executive (with title)
- Should reveal priorities, vision, challenges, or initiatives
- Look for quotes about: digital transformation, e-commerce growth, customer experience, technology adoption, innovation, brand strategy

❌ **IGNORE:**
- Pure hiring announcements with no strategic content
- Executive bios with no insights
- Generic company press releases without executive perspective
- Social media posts with no substance

🎯 RELEVANCE SCORING FOR MANAGEMENT INTERVIEWS:

- **8-10**: In-depth interview or talk with strategic insights directly relevant to Presti (e.g., discussing visual content, e-commerce scale, digital transformation, catalog challenges)
- **6-8**: Executive interview with relevant strategic topics (technology, innovation, customer experience, operational scale)
- **4-6**: Executive mention or quote in article about relevant topics
- **1-3**: Minimal executive insights or generic content

CRITICALLY IMPORTANT - QUALITY OVER QUANTITY:
- TARGET: 10-15 items, but ONLY with real URLs from web search results
- ⚠️ **NO HALLUCINATIONS**: If you can't find a real URL, don't include the item
- Focus on QUALITY over quantity - we want substantive interviews with verifiable sources
- Each item MUST feature a named executive with their title
- Each item MUST have a real, clickable URL (no placeholders, no brackets)
- Include the FULL NAME of the executive and their EXACT TITLE
- Extract SPECIFIC QUOTES or insights when possible
- Look for content from 2020 onwards (ideally LAST 18-24 MONTHS)
- Better to have 8 VERIFIED interviews than 15 hallucinated ones
- If an executive is quoted extensively in a company news article, include it (with real URL)

📰 HOW TO USE WEB SEARCH RESULTS - CRITICAL INSTRUCTIONS:
⚠️ **URLS ARE MANDATORY - NO EXCEPTIONS**:
- EVERY interview/article MUST have a COMPLETE, REAL URL (e.g., https://www.forbes.com/sites/...)
- DO NOT USE PLACEHOLDERS like "[Forbes article]" or "[article link]" - these are HALLUCINATIONS
- DO NOT write "[source article]" or any bracket notation - ONLY real clickable URLs
- If web search provides a URL, COPY IT EXACTLY as-is
- ⚠️ **CRITICAL**: If you cannot find a real URL for an item, DO NOT INCLUDE IT in your results
- No URL = No evidence = Hallucination = EXCLUDE from results

⚠️ **ONLY INCLUDE ITEMS WITH VERIFIED SOURCES**:
- Each item must be from a real web search result with a clickable URL
- If you're not sure an article exists or can't find the URL, DO NOT include it
- Better to return 8 items with real URLs than 15 items with fake placeholders
- Quality over quantity - only real, verifiable sources

Other requirements:
- Get ACTUAL publication dates (use specific dates like "Nov 02, 2023", not "recent")
- ⚠️ CRITICAL: Check the year - if before 2020, EXCLUDE IT (2019, 2018, 2017, 2016, 2015, 2014, 2013... = EXCLUDE)
- ⚠️ ONLY valid years: 2020, 2021, 2022, 2023, 2024
- Use EXACT titles from articles/videos/podcasts as they appear in search results
- Include the EXECUTIVE'S FULL NAME and EXACT TITLE as mentioned in the source
- Extract 2-3 KEY QUOTES or insights from the executive (only if found in the source)
- Note the FORMAT (interview, podcast, keynote, article, LinkedIn post, etc.)

REMINDER: Web search gives you real URLs - use them. If no URL is found, the source doesn't exist. Don't hallucinate.

IMPORTANT: Aim for 10-15 relevant items with REAL URLs. Use MULTIPLE SEARCH QUERIES to ensure comprehensive coverage.
However, ONLY include items where you have a real, clickable URL from web search results.
Better to return 8 high-quality items with real sources than 15 items with hallucinated/placeholder URLs.

⚠️ FINAL CHECK BEFORE RETURNING JSON:
- Go through each item and verify the published_date year
- If ANY item has year < 2020, REMOVE IT from the output
- Examples of INVALID years to exclude: 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, etc.
- ONLY valid years: 2020, 2021, 2022, 2023, 2024

Format your response in JSON with this structure:
{{
  "company_name": "{company_name}",
  "search_date": "2025-01-06",
  "management_items": [
    {{
      "title": "Exact title of interview/article/talk",
      "source": "Publication name or platform (e.g., Forbes, Business of Home, LinkedIn, Company Podcast)",
      "url": "https://www.example.com/full-real-url-here",
      "published_date": "Month DD, YYYY or YYYY-MM-DD",
      "format": "interview | podcast | keynote | article | panel | LinkedIn_post | webinar | profile",
      "executive_name": "Full name of executive",
      "executive_title": "Exact job title",
      "summary": "2-3 sentences summarizing the key insights (in English)",
      "key_quotes": ["Quote 1 from executive", "Quote 2 from executive", "Quote 3 from executive"],
      "topics_discussed": ["topic1", "topic2", "topic3"],
      "relevance_score": 8,
      "relevance_reason": "Why this is relevant for Presti sales approach (in English)",
      "sales_insights": ["Actionable insight 1 for sales", "Actionable insight 2", "Actionable insight 3"]
    }}
  ],
  "key_executives_identified": [
    {{
      "name": "Full name",
      "title": "Job title",
      "relevance": "Why this person is important for Presti",
      "content_count": 3
    }}
  ],
  "overall_assessment": {{
    "decision_maker_visibility": "high | medium | low - How visible are key decision-makers?",
    "strategic_priorities": ["Priority 1 based on executive statements", "Priority 2", "Priority 3"],
    "presti_entry_points": ["Specific angle 1 based on executive insights (8-12 words)", "Angle 2", "Angle 3"],
    "recommended_contact": "Which executive to target first and why (2-3 sentences, 30-50 words)"
  }}
}}

CRITICAL for overall_assessment:
- decision_maker_visibility: Assess how much strategic content is publicly available from executives
- strategic_priorities: Based on what executives are ACTUALLY saying, not generic assumptions
- presti_entry_points: Specific talking points based on their stated challenges/priorities
- recommended_contact: Concrete recommendation with reasoning

REMEMBER: 
- ALL TEXT MUST BE IN ENGLISH
- Focus on QUALITY interviews/insights with STRATEGIC RELEVANCE
- Must find 10-15 items minimum
- Each item MUST include executive name and title
- Extract ACTUAL QUOTES when available"""

    try:
        # Utilisation de la Responses API ASYNC avec web_search
        response = await client.responses.create(
            model="gpt-4o",
            tools=[
                {
                    "type": "web_search",
                    "external_web_access": True
                }
            ],
            tool_choice="auto",
            input=prompt,
            temperature=0.3,
            max_output_tokens=4000,
        )
        
        # Extraction du contenu de la Responses API
        result_text = response.output_text if hasattr(response, 'output_text') else ""
        
        if not result_text and hasattr(response, 'output'):
            for item in response.output:
                if hasattr(item, 'type') and item.type == 'message':
                    if hasattr(item, 'content'):
                        for content_item in item.content:
                            if hasattr(content_item, 'text'):
                                result_text += content_item.text
        
        if not result_text:
            raise ValueError("Aucun texte trouvé dans la réponse")
        
        # Tentative de parsing JSON
        try:
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                interviews_data = json.loads(json_str)
            else:
                raise ValueError("Pas de JSON trouvé dans la réponse")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Erreur de parsing JSON pour {company_name}: {e}")
            interviews_data = {
                "company_name": company_name,
                "search_date": datetime.now().strftime("%Y-%m-%d"),
                "management_items": [],
                "key_executives_identified": [],
                "overall_assessment": {
                    "decision_maker_visibility": "low",
                    "strategic_priorities": [],
                    "presti_entry_points": [],
                    "recommended_contact": "Analyse manuelle nécessaire"
                },
                "raw_response": result_text
            }
        
        # Ajout des métadonnées
        interviews_data["scrape_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "model": "gpt-4o",
            "success": len(interviews_data.get("management_items", [])) > 0,
            "web_search_used": True
        }
        
        print(f"✅ {len(interviews_data.get('management_items', []))} interviews trouvées pour {company_name}")
        
        return interviews_data
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche pour {company_name}: {e}")
        return {
            "company_name": company_name,
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "management_items": [],
            "key_executives_identified": [],
            "overall_assessment": {
                "decision_maker_visibility": "unknown",
                "strategic_priorities": [],
                "presti_entry_points": [],
                "recommended_contact": "Erreur lors de la recherche"
            },
            "error": str(e),
            "scrape_metadata": {
                "timestamp": datetime.now().isoformat(),
                "model": "gpt-4o",
                "success": False
            }
        }


async def process_single_company(company_name: str, company_info: Dict, semaphore: asyncio.Semaphore) -> tuple[str, Dict]:
    """
    Traite une seule entreprise avec limitation de concurrence
    """
    async with semaphore:
        interviews = await get_management_interviews(
            company_name=company_name,
            company_website=company_info.get("website", ""),
            industry=company_info.get("industry", "")
        )
        return company_name, interviews


def save_results_periodically(interviews_data: Dict, output_file: str):
    """
    Sauvegarde périodique des résultats
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(interviews_data, f, indent=2, ensure_ascii=False)


async def process_all_companies(input_file: str = "jobs_data.json", output_file: str = "management_interviews.json"):
    """
    Traite toutes les entreprises de manière ASYNCHRONE avec workers parallèles
    """
    
    print("🚀 Démarrage du scraping ASYNCHRONE des interviews management...")
    print(f"⚡ Mode: {MAX_CONCURRENT_REQUESTS} requêtes simultanées")
    
    # Chargement des données existantes
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    companies_list = data.get("companies", [])
    companies = {}
    for company_data in companies_list:
        if "company" in company_data and "name" in company_data["company"]:
            company_info = company_data["company"]
            companies[company_info["name"]] = company_info
    
    print(f"📊 {len(companies)} entreprises à analyser")
    
    # Chargement des résultats existants
    interviews_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                interviews_data = json.load(f)
            print(f"📂 {len(interviews_data)} interviews déjà récupérées")
        except:
            interviews_data = {}
    
    # Filtrer les entreprises déjà traitées avec succès
    companies_to_process = {
        name: info for name, info in companies.items()
        if name not in interviews_data or not interviews_data[name].get("scrape_metadata", {}).get("success")
    }
    
    print(f"🔄 {len(companies_to_process)} entreprises à traiter")
    
    if not companies_to_process:
        print("✅ Toutes les entreprises ont déjà été traitées!")
        return
    
    # Créer un semaphore pour limiter la concurrence
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    # Créer les tâches pour toutes les entreprises
    tasks = [
        process_single_company(name, info, semaphore)
        for name, info in companies_to_process.items()
    ]
    
    # Traiter les entreprises avec progression
    completed = 0
    total = len(tasks)
    
    for coro in asyncio.as_completed(tasks):
        try:
            company_name, company_interviews = await coro
            interviews_data[company_name] = company_interviews
            completed += 1
            
            # Sauvegarde incrémentale tous les 5 résultats
            if completed % 5 == 0 or completed == total:
                save_results_periodically(interviews_data, output_file)
                print(f"\n💾 Progression sauvegardée: {completed}/{total} entreprises")
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
            completed += 1
    
    # Sauvegarde finale
    save_results_periodically(interviews_data, output_file)
    
    print("\n✅ Scraping terminé!")
    print(f"📁 Résultats sauvegardés dans {output_file}")
    
    # Statistiques finales
    total_interviews = sum(len(company_data.get("management_items", [])) for company_data in interviews_data.values())
    successful = sum(1 for company_data in interviews_data.values() 
                     if company_data.get("scrape_metadata", {}).get("success"))
    
    print(f"\n📈 Statistiques:")
    print(f"   - Entreprises traitées: {len(interviews_data)}")
    print(f"   - Succès: {successful}")
    print(f"   - Total interviews: {total_interviews}")
    print(f"   - Moyenne par entreprise: {total_interviews/len(interviews_data):.1f}")


async def test_single_company(company_name: str = "California Closets"):
    """
    Test sur une seule entreprise pour validation (ASYNC)
    """
    
    print(f"🧪 Test ASYNC sur {company_name}...")
    
    # Chargement des infos de l'entreprise
    with open("jobs_data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    companies_list = data.get("companies", [])
    company_info = {}
    
    for company_data in companies_list:
        if "company" in company_data and "name" in company_data["company"]:
            if company_data["company"]["name"] == company_name:
                company_info = company_data["company"]
                break
    
    if not company_info:
        print(f"❌ Entreprise '{company_name}' non trouvée dans jobs_data.json")
        return
    
    # Récupération des interviews
    interviews = await get_management_interviews(
        company_name=company_name,
        company_website=company_info.get("website", ""),
        industry=company_info.get("industry", "")
    )
    
    # Sauvegarde du test
    with open("management_interviews_test.json", 'w', encoding='utf-8') as f:
        json.dump({company_name: interviews}, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Test terminé!")
    print(f"📁 Résultat sauvegardé dans management_interviews_test.json")
    print(f"\n📊 Résumé:")
    print(f"   - Interviews trouvées: {len(interviews.get('management_items', []))}")
    print(f"   - Executives identifiés: {len(interviews.get('key_executives_identified', []))}")
    print(f"   - Visibilité décideurs: {interviews.get('overall_assessment', {}).get('decision_maker_visibility', 'N/A')}")
    
    if interviews.get('management_items'):
        print(f"\n🎤 Aperçu des interviews:")
        for item in interviews['management_items'][:3]:
            print(f"   • {item.get('executive_name', 'N/A')} ({item.get('executive_title', 'N/A')})")
            print(f"     {item.get('title', 'N/A')} - Score: {item.get('relevance_score', 0)}/10")


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape management interviews')
    parser.add_argument('mode', nargs='?', default='full', help='Mode: test or full (default: full)')
    parser.add_argument('--company', type=str, help='Company name to scrape (for single company mode)')
    parser.add_argument('--days', type=int, help='Number of days to look back (e.g., 7, 30, 90)')
    parser.add_argument('test_company', nargs='?', help='Company name for test mode (positional arg)')
    
    args = parser.parse_args()
    
    # Handle different invocation styles
    if args.mode == "test" or args.company:
        # Mode test sur une seule entreprise
        company = args.company or args.test_company or "California Closets"
        
        # TODO: In future, pass days parameter to the scraping function
        # to modify the prompt with specific date range
        if args.days:
            print(f"🔍 Searching for interviews from last {args.days} days for {company}")
        
        asyncio.run(test_single_company(company))
    else:
        # Mode complet avec workers parallèles
        asyncio.run(process_all_companies())

