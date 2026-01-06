"""
Script ASYNCHRONE pour scraper les actualités des entreprises en utilisant OpenAI Web Search
Version optimisée avec workers parallèles pour traiter plusieurs entreprises simultanément
"""

import json
import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
# aiofiles not needed - using sync file operations

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
MAX_CONCURRENT_REQUESTS = 5  # Nombre de requêtes simultanées
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def get_company_news(company_name: str, company_website: str = "", industry: str = "") -> Dict[str, Any]:
    """
    Récupère les actualités d'une entreprise en utilisant OpenAI Web Search (ASYNC)
    
    Args:
        company_name: Nom de l'entreprise
        company_website: Site web de l'entreprise (optionnel)
        industry: Industrie de l'entreprise (optionnel)
        
    Returns:
        Dict contenant les actualités structurées
    """
    
    print(f"\n🔍 Recherche des actualités pour {company_name}...")
    
    # Build the prompt to target relevant news
    prompt = f"""You are an expert in researching company news for business analysis.

Target company: {company_name}
Industry: {industry if industry else "Not specified"}
Website: {company_website if company_website else "Not specified"}

Context: Presti is an AI solution that helps home & furniture companies generate lifestyle product images at scale, independently of their supply chain. Key benefits:
- Generate hundreds/thousands of product visuals quickly without physical photoshoots
- Create visuals before products are physically available (no supply chain dependency)
- Perfect for large catalogs with many SKUs, multiple angles, colors, and contexts
- Reduce time-to-market, costs, and carbon footprint of traditional photography
- Ideal for: e-commerce catalogs, websites, marketing campaigns, social media, A/B testing

⚠️⚠️⚠️ CRITICAL DATE REQUIREMENT - ABSOLUTE RULE ⚠️⚠️⚠️
- ONLY include news from 2020, 2021, 2022, 2023, 2024 (ideally last 18-24 months)
- ❌ NEVER INCLUDE news from 2019 or earlier (2019, 2018, 2017, 2016, 2015, 2014, 2013, etc.)
- ❌ If publication date is before January 1, 2020 → DO NOT INCLUDE IT
- The business landscape pre-COVID (before 2020) is completely different and irrelevant
- This is a HARD CUTOFF - no exceptions, no "highly relevant" pre-2020 content

IMPORTANT: Provide ALL content in ENGLISH ONLY.

MISSION: Search BROADLY for any news about {company_name} that could indicate opportunities for Presti. Cast a WIDE NET and include:

✅ **DEFINITELY INCLUDE** (any of these topics):
- **E-commerce & Digital**: Website launches/redesigns, e-commerce growth, online sales expansion, digital channel improvements
- **Catalog & Product**: New collections, product launches, catalog expansions, SKU increases, product line extensions, new materials/finishes/colors, new references
- **Visual & Content**: Product imagery, photography, content production, 3D visualization, AR/VR, view-in-room features, generative AI for visuals, visual technology
- **Digital Transformation**: Post-crisis recovery, digital initiatives, technology investments, modernization, replatforming
- **Customization & Personalization**: Custom products, made-to-order, personalization programs, configurators, modular products with multiple configurations
- **Omnichannel & Multi-channel**: Integrated online/offline, unified commerce, consistent brand experience
- **International & Expansion**: New markets, regional expansion, geographic growth, multi-market strategies
- **Supply Chain & Operations**: Production challenges, inventory issues, time-to-market improvements, operational efficiency, scaling operations
- **Marketing & Campaigns**: Seasonal campaigns, promotional content, brand storytelling, social media strategies, marketing automation
- **Private Label & Own Brand**: Exclusive collections, in-house brands, proprietary product lines
- **Technology & Innovation**: AI/ML adoption, Generative AI, automation, platform migrations, tech stack improvements
- **Sustainability & ESG**: Environmental initiatives, waste reduction, carbon footprint (relevant because Presti reduces physical photoshoots)
- **Business Performance**: Revenue growth, market positioning, competitive advantages that require visual content to stay at the top
- **Brand Strategy**: Brand repositioning, premiumization, luxury positioning, brand elevation, moving upmarket, quality upgrades
- **Physical Presence & Events**: Trade shows participation (KBIS, High Point Market, Maison&Objet, IMM Cologne), showrooms opening/redesign, pop-up stores, temporary exhibitions, design weeks (requiring marketing materials and consistent visuals)

✅ **ALSO CONSIDER** (broader context):
- Company restructuring or recovery (bankruptcy exit, new leadership, strategic pivots)
- Store openings/showrooms IF they mention online content needs, catalog updates, or omnichannel consistency
- Partnerships with tech/platform providers
- Customer experience improvements requiring visual content
- M&A activity that might consolidate/expand product catalogs
- Trade show participation or design weeks (need for marketing materials, product showcases)
- New finishes, materials, or color options (each requires new product visuals)

❌ **IGNORE ONLY**:
- Pure physical store news with NO digital/online angle
- HR/workplace culture news (unless about hiring digital/creative teams)
- Financial results with no strategic implications
- Legal issues or controversies

SCORING GUIDANCE (but be flexible - good digital transformation stories can score 8-10 even if not in "high priority"):
- **8-10**: Strong immediate need for visual content at scale
- **6-8**: Clear opportunity with digital/catalog angle
- **4-6**: Relevant context, potential future opportunity
- **1-3**: Weak relevance

IMPORTANT: Be INCLUSIVE rather than exclusive. If unsure, INCLUDE the article - better to have more relevant news than to miss important signals.

🔍 WEB SEARCH METHODOLOGY - CRITICAL INSTRUCTIONS:

You have access to web search. Use it EXTENSIVELY with MULTIPLE search patterns to find comprehensive coverage.

**SEARCH PATTERN 1 - General News & Announcements:**
From mainstream and business news outlets, try these exact queries:
- "{company_name} recent news"
- "{company_name} news 2024"
- "{company_name} news 2025"
- "{company_name} announcements"
- "{company_name} press release"
- "{company_name} latest updates"

**SEARCH PATTERN 2 - Company-Owned Content:**
Direct from the company's communication channels:
- "{company_name} blog"
- "{company_name} LinkedIn posts"
- "{company_name} company updates"
- "site:{company_website} news" (if website provided)
- "site:{company_website} blog" (if website provided)

**SEARCH PATTERN 3 - Trade Publications (CRITICAL for B2B):**
Industry-specific sources are GOLD for relevant insights:
- "{company_name} Furniture Today"
- "{company_name} Business of Home"
- "{company_name} Modern Retail"
- "{company_name} Retail Dive"
- "{company_name} Interior Design magazine"
- "{company_name} Forbes"
- "{company_name} WWD"

**SEARCH PATTERN 4 - Thematic Searches (use ALL themes):**
🎯 E-commerce & Digital:
  - "{company_name} e-commerce growth"
  - "{company_name} website redesign" OR "{company_name} website relaunch"
  - "{company_name} digital transformation"
  - "{company_name} online sales"
  - "{company_name} digital strategy"

📦 Catalog & Product:
  - "{company_name} catalog" OR "{company_name} new collection"
  - "{company_name} new products" OR "{company_name} product launch"
  - "{company_name} new materials" OR "{company_name} new finishes" OR "{company_name} new colors"
  - "{company_name} SKU expansion" OR "{company_name} product range"

🎨 Visual & Content:
  - "{company_name} product imagery"
  - "{company_name} 3D visualization" OR "{company_name} AR" OR "{company_name} VR"
  - "{company_name} content production"
  - "{company_name} visual technology"

⚙️ Customization & Tech:
  - "{company_name} modular" OR "{company_name} customization" OR "{company_name} personalization"
  - "{company_name} configurator"
  - "{company_name} technology" OR "{company_name} innovation"
  - "{company_name} AI" OR "{company_name} automation"
  - "{company_name} generative AI"

🌍 Expansion & Growth:
  - "{company_name} expansion" OR "{company_name} international"
  - "{company_name} new market"
  - "{company_name} growth strategy"

🏆 Brand & Positioning:
  - "{company_name} brand repositioning" OR "{company_name} premium" OR "{company_name} luxury"
  - "{company_name} brand strategy"
  - "{company_name} rebranding"

🎪 Events & Physical Presence:
  - "{company_name} trade show" OR "{company_name} KBIS" OR "{company_name} High Point Market"
  - "{company_name} showroom" OR "{company_name} pop-up"
  - "{company_name} Maison&Objet" OR "{company_name} design week"

⏱️ Operations & Performance:
  - "{company_name} time to market" OR "{company_name} speed"
  - "{company_name} scaling operations"
  - "{company_name} operational efficiency"

🔄 Recovery & Strategy (if applicable):
  - "{company_name} after bankruptcy"
  - "{company_name} recovery"
  - "{company_name} new strategy" OR "{company_name} reinvention"
  - "{company_name} turnaround"

**SEARCH PATTERN 5 - Time-Based Searches:**
Use date filters to get recent content:
- "{company_name} 2024"
- "{company_name} 2025"
- "{company_name} last 12 months"
- "{company_name} recent developments"

**SEARCH PATTERN 6 - Executive & Leadership:**
Leaders often share strategic insights:
- "{company_name} CEO interview"
- "{company_name} leadership"
- "{company_name} executive"

CRITICAL: Use web search MULTIPLE TIMES with DIFFERENT query patterns. Don't stop after one search - try at least 10-15 different searches to find comprehensive coverage.

For each relevant news item, provide:
1. Exact title (in English)
2. Source (site/publication name)
3. Full URL
4. Publication date (format: "Month DD, YYYY" or "YYYY-MM-DD")
5. Short summary (2-3 sentences, in English)
6. Relevance score (1-10) - Use the priority levels above as guide
7. Why it's relevant for Presti (in English)
8. Key actionable insights for sales approach (in English)
9. Category based on the PRIMARY signal detected

TARGET: 15-20 relevant news items with REAL URLs. Use MULTIPLE SEARCH QUERIES to ensure comprehensive coverage.
⚠️ IMPORTANT: ONLY include items where you have a real, clickable URL from web search results.
Better to return 12 high-quality items with real sources than 20 items with hallucinated/placeholder URLs.

⚡ MANDATORY SEARCH STRATEGY - YOU MUST USE WEB SEARCH MULTIPLE TIMES:

DO NOT rely on a single web search. Execute MULTIPLE searches (minimum 10-15 searches) using these patterns:

1️⃣ **General News Discovery (3-4 searches):**
   - "{company_name} recent news"
   - "{company_name} news 2024" OR "{company_name} news 2025"
   - "{company_name} announcements"
   - "{company_name} press release"

2️⃣ **Trade Publications (2-3 searches):**
   - "{company_name} Furniture Today"
   - "{company_name} Business of Home"
   - "{company_name} Modern Retail" OR "{company_name} Retail Dive"

3️⃣ **Thematic Deep Dives (6-8 searches, pick most relevant themes):**
   - "{company_name} e-commerce" OR "{company_name} digital transformation"
   - "{company_name} new products" OR "{company_name} catalog"
   - "{company_name} technology" OR "{company_name} AI"
   - "{company_name} expansion" OR "{company_name} international"
   - "{company_name} customization" OR "{company_name} modular"
   - "{company_name} trade show" OR "{company_name} KBIS"
   - "{company_name} premium" OR "{company_name} luxury"
   - "{company_name} new materials" OR "{company_name} new finishes"

4️⃣ **Company-Owned Content (2 searches):**
   - "{company_name} blog"
   - "{company_name} LinkedIn"

5️⃣ **Special Cases (if applicable):**
   - If bankruptcy/crisis: "{company_name} recovery" OR "{company_name} reinvention"
   - If major brand: "{company_name} CEO interview" OR "{company_name} strategy"

🎯 EXECUTION APPROACH:
- Start BROAD (general news, press releases) to get overview
- Then go SPECIFIC (thematic searches) to find targeted articles
- Use TRADE PUBLICATIONS for B2B insights (they're goldmines!)
- Check COMPANY SOURCES for first-party content
- Vary your search terms - different words = different results

📰 HOW TO USE WEB SEARCH RESULTS - CRITICAL INSTRUCTIONS:
⚠️ **URLS ARE MANDATORY - NO EXCEPTIONS**:
- EVERY news item MUST have a COMPLETE, REAL URL (e.g., https://www.forbes.com/...)
- DO NOT USE PLACEHOLDERS like "[Forbes article]" or "[article link]" - these are HALLUCINATIONS
- ⚠️ **CRITICAL**: If you cannot find a real URL for an item, DO NOT INCLUDE IT in your results
- No URL = No evidence = Hallucination = EXCLUDE from results
- Each item must be from a real web search result with a clickable URL

Other requirements:
- Get ACTUAL publication dates (format: "Month DD, YYYY" or "YYYY-MM-DD")
- ⚠️ CRITICAL: Check the year - if before 2020, EXCLUDE IT (2019, 2018, 2017, 2016, 2015, 2014, 2013... = EXCLUDE)
- ⚠️ ONLY valid years: 2020, 2021, 2022, 2023, 2024
- Use EXACT titles from the articles found in search results
- Read enough of each article to write an accurate 2-3 sentence summary
- Prioritize articles from the LAST 18-24 MONTHS
- If you find 10+ articles from one search, GREAT - include the best 3-5 and move to next search
- If a search yields few results, try rephrasing the query

REMINDER: Web search gives you real URLs - use them. If no URL is found, the source doesn't exist. Don't hallucinate.

CRITICALLY IMPORTANT - QUALITY WITH REAL SOURCES:
- TARGET: 15-20 articles, but ONLY with real URLs from web search results
- ⚠️ **NO HALLUCINATIONS**: If you can't find a real URL, don't include the article
- Include articles about digital transformation, website launches/redesigns, e-commerce growth
- Include articles about post-crisis recovery, company reinvention, strategic pivots
- Include articles with specific numbers/metrics (e.g., "e-commerce grew 157%", "launched 500 SKUs")
- Include articles from various sources: trade publications, business news, company blog, LinkedIn, tech sites
- Look for articles from 2020 onwards (ideally LAST 18-24 MONTHS)
- Include articles about new stores/showrooms IF they mention online/digital aspects or omnichannel consistency
- Include articles about partnerships, technology investments, hiring in digital/creative roles
- Include seasonal campaigns, product launches, sustainability initiatives
- Include articles about NEW MATERIALS, FINISHES, COLORS (each requires new product visuals)
- Include articles about MODULAR/CUSTOMIZABLE products (multiple configurations = many visuals needed)
- Include articles about TRADE SHOWS participation (KBIS, High Point Market, Maison&Objet, etc.) - need for marketing materials
- Include articles about BRAND REPOSITIONING, premiumization, moving upmarket (need for premium-quality visuals)
- Include articles about CATALOG EXPANSIONS, new references, SKU growth (direct need for product imagery at scale)
- Keep searching until you have 15-20 items with REAL URLs
- Better to have 12 VERIFIED articles than 20 hallucinated ones - COMPREHENSIVE coverage with REAL sources

REMINDER: Target 15-20 news items with REAL URLs from web search results. Cast a WIDE NET across multiple sources and topics.
⚠️ CRITICAL: Only include items with verifiable URLs. No URL = Don't include it. Quality over quantity.

⚠️ FINAL CHECK BEFORE RETURNING JSON:
- Go through each item and verify the published_date year
- If ANY item has year < 2020, REMOVE IT from the output
- Examples of INVALID years to exclude: 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, etc.
- ONLY valid years: 2020, 2021, 2022, 2023, 2024

Format your response in JSON with this structure:
{{
  "company_name": "{company_name}",
  "search_date": "2025-01-02",
  "news_items": [
    {{
      "title": "...",
      "source": "...",
      "url": "...",
      "published_date": "...",
      "summary": "...",
      "relevance_score": 8,
      "relevance_reason": "...",
      "key_insights": ["insight1", "insight2", "insight3"],
      "category": "digital_transformation | catalog_expansion | ecommerce_growth | visual_content_strategy | supply_chain_challenges | international_expansion | time_to_market | large_catalog_operations | omnichannel_strategy | product_customization | private_label | technology_innovation | sustainability_initiative | cost_optimization | merger_acquisition | platform_migration | marketing_campaigns | ai_adoption | product_innovation | partnership"
    }}
  ],
  "overall_assessment": {{
    "presti_fit_score": 8,
    "key_opportunities": ["Specific opportunity 1 (8-12 words)", "Specific opportunity 2 (8-12 words)", "Specific opportunity 3 (8-12 words)"],
    "recommended_approach": "2-3 sentences (30-50 words total) explaining the specific sales approach based on the news found."
  }}
}}

CRITICAL for overall_assessment:
- recommended_approach: 2-3 sentences (30-50 words total), explaining the specific angle to take with this company based on their actual initiatives from the news
- key_opportunities: 3-4 bullets (each 8-12 words), specific to what you found in the articles, NOT generic Presti features
- Be concrete: mention specific initiatives, numbers, or projects from the news
- Focus on what makes THIS company unique and what specific need Presti can address

REMEMBER: ALL TEXT MUST BE IN ENGLISH."""

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
                news_data = json.loads(json_str)
            else:
                raise ValueError("Pas de JSON trouvé dans la réponse")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Erreur de parsing JSON pour {company_name}: {e}")
            news_data = {
                "company_name": company_name,
                "search_date": datetime.now().strftime("%Y-%m-%d"),
                "news_items": [],
                "overall_assessment": {
                    "presti_fit_score": 0,
                    "key_opportunities": [],
                    "recommended_approach": "Analyse manuelle nécessaire"
                },
                "raw_response": result_text
            }
        
        # Ajout des métadonnées
        news_data["scrape_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "model": "gpt-4o",
            "success": len(news_data.get("news_items", [])) > 0,
            "web_search_used": True
        }
        
        print(f"✅ {len(news_data.get('news_items', []))} actualités trouvées pour {company_name}")
        
        return news_data
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche pour {company_name}: {e}")
        return {
            "company_name": company_name,
            "search_date": datetime.now().strftime("%Y-%m-%d"),
            "news_items": [],
            "overall_assessment": {
                "presti_fit_score": 0,
                "key_opportunities": [],
                "recommended_approach": "Erreur lors de la recherche"
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
        news = await get_company_news(
            company_name=company_name,
            company_website=company_info.get("website", ""),
            industry=company_info.get("industry", "")
        )
        return company_name, news


def save_results_periodically(news_data: Dict, output_file: str):
    """
    Sauvegarde périodique des résultats (synchrone car file I/O est rapide)
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, indent=2, ensure_ascii=False)


async def process_all_companies(input_file: str = "jobs_data.json", output_file: str = "company_news.json"):
    """
    Traite toutes les entreprises de manière ASYNCHRONE avec workers parallèles
    """
    
    print("🚀 Démarrage du scraping ASYNCHRONE des actualités...")
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
    news_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            print(f"📂 {len(news_data)} actualités déjà récupérées")
        except:
            news_data = {}
    
    # Filtrer les entreprises déjà traitées avec succès
    companies_to_process = {
        name: info for name, info in companies.items()
        if name not in news_data or not news_data[name].get("scrape_metadata", {}).get("success")
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
            company_name, company_news = await coro
            news_data[company_name] = company_news
            completed += 1
            
            # Sauvegarde incrémentale tous les 5 résultats
            if completed % 5 == 0 or completed == total:
                save_results_periodically(news_data, output_file)
                print(f"\n💾 Progression sauvegardée: {completed}/{total} entreprises")
                
        except Exception as e:
            print(f"❌ Erreur lors du traitement: {e}")
            completed += 1
    
    # Sauvegarde finale
    save_results_periodically(news_data, output_file)
    
    print("\n✅ Scraping terminé!")
    print(f"📁 Résultats sauvegardés dans {output_file}")
    
    # Statistiques finales
    total_news = sum(len(company_data.get("news_items", [])) for company_data in news_data.values())
    successful = sum(1 for company_data in news_data.values() 
                     if company_data.get("scrape_metadata", {}).get("success"))
    
    print(f"\n📈 Statistiques:")
    print(f"   - Entreprises traitées: {len(news_data)}")
    print(f"   - Succès: {successful}")
    print(f"   - Total actualités: {total_news}")
    print(f"   - Moyenne par entreprise: {total_news/len(news_data):.1f}")


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
    
    # Récupération des news
    news = await get_company_news(
        company_name=company_name,
        company_website=company_info.get("website", ""),
        industry=company_info.get("industry", "")
    )
    
    # Sauvegarde du test
    with open("company_news_test.json", 'w', encoding='utf-8') as f:
        json.dump({company_name: news}, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Test terminé!")
    print(f"📁 Résultat sauvegardé dans company_news_test.json")
    print(f"\n📊 Résumé:")
    print(f"   - Actualités trouvées: {len(news.get('news_items', []))}")
    print(f"   - Score Presti: {news.get('overall_assessment', {}).get('presti_fit_score', 0)}/10")
    
    if news.get('news_items'):
        print(f"\n📰 Aperçu des actualités:")
        for item in news['news_items'][:3]:
            print(f"   • {item.get('title', 'N/A')} ({item.get('relevance_score', 0)}/10)")


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape company news')
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
            print(f"🔍 Searching for news from last {args.days} days for {company}")
        
        asyncio.run(test_single_company(company))
    else:
        # Mode complet avec workers parallèles
        asyncio.run(process_all_companies())

