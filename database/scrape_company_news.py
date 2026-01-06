"""
Script pour scraper les actualités des entreprises en utilisant OpenAI Web Search
Ce script récupère les actualités pertinentes pour évaluer la pertinence du produit Presti
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from openai import OpenAI

# Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
client = OpenAI(api_key=OPENAI_API_KEY)

def get_company_news(company_name: str, company_website: str = "", industry: str = "") -> Dict[str, Any]:
    """
    Récupère les actualités d'une entreprise en utilisant OpenAI Web Search
    
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

IMPORTANT: Use web search to find REAL and RECENT news (last 18-24 months maximum).
IMPORTANT: Provide ALL content in ENGLISH ONLY.

MISSION: Search BROADLY for any news about {company_name} that could indicate opportunities for Presti. Cast a WIDE NET and include:

✅ **DEFINITELY INCLUDE** (any of these topics):
- **E-commerce & Digital**: Website launches/redesigns, e-commerce growth, online sales expansion, digital channel improvements
- **Catalog & Product**: New collections, product launches, catalog expansions, SKU increases, product line extensions
- **Visual & Content**: Product imagery, photography, content production, 3D visualization, AR/VR, view-in-room features
- **Digital Transformation**: Post-crisis recovery, digital initiatives, technology investments, modernization, replatforming
- **Customization & Personalization**: Custom products, made-to-order, personalization programs, configurators
- **Omnichannel & Multi-channel**: Integrated online/offline, unified commerce, consistent brand experience
- **International & Expansion**: New markets, regional expansion, geographic growth, multi-market strategies
- **Supply Chain & Operations**: Production challenges, inventory issues, time-to-market improvements, operational efficiency
- **Marketing & Campaigns**: Seasonal campaigns, promotional content, brand storytelling, social media strategies
- **Private Label & Own Brand**: Exclusive collections, in-house brands, proprietary product lines
- **Technology & Innovation**: AI/ML adoption, automation, platform migrations, tech stack improvements
- **Sustainability & ESG**: Environmental initiatives, waste reduction, carbon footprint (relevant because Presti reduces physical photoshoots)
- **Business Performance**: Revenue growth, market positioning, competitive advantages that require visual content

✅ **ALSO CONSIDER** (broader context):
- Company restructuring or recovery (bankruptcy exit, new leadership, strategic pivots)
- Store openings IF they mention online content needs or catalog updates
- Partnerships with tech/platform providers
- Customer experience improvements requiring visual content
- M&A activity that might consolidate/expand product catalogs

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

Sources to explore (search MULTIPLE queries to find different angles):
- Company's official blog
- Company's LinkedIn posts
- Trade publications (Furniture Today, Business of Home, Modern Retail, etc.)
- Business news (Forbes, WWD, etc.)
- Press releases
- Executive interviews
- Technology/e-commerce focused articles

SEARCH QUERIES TO TRY:
- "{company_name} e-commerce growth"
- "{company_name} website redesign"
- "{company_name} digital transformation"
- "{company_name} online sales"
- "{company_name} catalog"
- "{company_name} product imagery"
- "{company_name} technology"
- "{company_name} after bankruptcy" (if applicable)
- "{company_name} recovery"
- "{company_name} new strategy"

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

REMINDER: You MUST find 15-20 news items minimum. Do NOT provide fewer than 15 articles unless there is genuinely no content available (which is unlikely for any company). Cast a WIDE NET across multiple sources and topics.

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

Find AT LEAST 15-20 relevant news items. This is a MINIMUM, not a target. Use MULTIPLE SEARCH QUERIES to ensure comprehensive coverage:

MANDATORY SEARCH STRATEGY:
1. Search for "{company_name} e-commerce" OR "{company_name} online sales"
2. Search for "{company_name} digital transformation" OR "{company_name} website"
3. Search for "{company_name} new products" OR "{company_name} catalog" OR "{company_name} collection"
4. Search for "{company_name} technology" OR "{company_name} innovation"
5. Search for "{company_name} expansion" OR "{company_name} growth"
6. Search for "{company_name} marketing" OR "{company_name} brand"
7. Search for company blog posts and LinkedIn announcements
8. Search for press releases and trade publication articles
9. If company had challenges/bankruptcy: search "{company_name} recovery" OR "{company_name} reinvention"

CRITICALLY IMPORTANT - YOU MUST FIND 15-20 ARTICLES:
- Include articles about digital transformation, website launches/redesigns, e-commerce growth
- Include articles about post-crisis recovery, company reinvention, strategic pivots
- Include articles with specific numbers/metrics (e.g., "e-commerce grew 157%", "launched 500 SKUs")
- Include articles from various sources: trade publications, business news, company blog, LinkedIn, tech sites
- Look for articles from the LAST 18-24 MONTHS
- Include articles about new stores IF they mention online/digital aspects
- Include articles about partnerships, technology investments, hiring in digital/creative roles
- Include seasonal campaigns, product launches, sustainability initiatives
- DO NOT STOP at 8-10 articles - keep searching until you have 15-20 items
- Better to include MORE articles than fewer - COMPREHENSIVE coverage is the goal

CRITICAL for overall_assessment:
- recommended_approach: 2-3 sentences (30-50 words total), explaining the specific angle to take with this company based on their actual initiatives from the news
- key_opportunities: 3-4 bullets (each 8-12 words), specific to what you found in the articles, NOT generic Presti features
- Be concrete: mention specific initiatives, numbers, or projects from the news
- Focus on what makes THIS company unique and what specific need Presti can address

REMEMBER: ALL TEXT MUST BE IN ENGLISH."""

    try:
        # Utilisation de la Responses API avec web_search
        # Documentation: https://platform.openai.com/docs/guides/tools-web-search
        response = client.responses.create(
            model="gpt-4o",
            tools=[
                {
                    "type": "web_search",
                    "external_web_access": True  # Active l'accès web en temps réel
                }
            ],
            tool_choice="auto",  # Le modèle décide s'il doit utiliser la recherche web
            input=prompt,
            temperature=0.3,
            max_output_tokens=4000,  # Augmenté pour permettre plus d'articles (15-20)
        )
        
        # Extraction du contenu de la Responses API
        # La Responses API retourne un attribut output_text directement
        result_text = response.output_text if hasattr(response, 'output_text') else ""
        
        if not result_text and hasattr(response, 'output'):
            # Fallback: chercher le texte dans les output items
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
            # Chercher le JSON dans la réponse
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                news_data = json.loads(json_str)
            else:
                raise ValueError("Pas de JSON trouvé dans la réponse")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Erreur de parsing JSON: {e}")
            # Fallback: structure minimale
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
        
        # Ajout des métadonnées et sources web
        news_data["scrape_metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "model": "gpt-4o",
            "success": len(news_data.get("news_items", [])) > 0,
            "web_search_used": True
        }
        
        # Extraction des sources web si disponibles
        try:
            if hasattr(response, 'output') and response.output:
                web_sources = []
                for output_item in response.output:
                    if hasattr(output_item, 'type') and output_item.type == 'web_search_call':
                        if hasattr(output_item, 'action') and hasattr(output_item.action, 'sources'):
                            web_sources.extend(output_item.action.sources)
                
                if web_sources:
                    news_data["scrape_metadata"]["web_sources_count"] = len(web_sources)
                    news_data["scrape_metadata"]["web_sources"] = web_sources[:10]  # Garder les 10 premières
        except Exception as e:
            print(f"⚠️  Impossible d'extraire les sources web: {e}")
        
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


def process_all_companies(input_file: str = "jobs_data.json", output_file: str = "company_news.json"):
    """
    Traite toutes les entreprises du fichier jobs_data.json
    
    Args:
        input_file: Fichier source contenant les données des entreprises
        output_file: Fichier de sortie pour les actualités
    """
    
    print("🚀 Démarrage du scraping des actualités...")
    
    # Chargement des données existantes
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # jobs_data.json a une structure où companies est une liste
    companies_list = data.get("companies", [])
    
    # Convertir en dict pour faciliter le traitement
    companies = {}
    for company_data in companies_list:
        if "company" in company_data and "name" in company_data["company"]:
            company_info = company_data["company"]
            companies[company_info["name"]] = company_info
    
    print(f"📊 {len(companies)} entreprises à analyser")
    
    # Chargement des résultats existants si le fichier existe
    news_data = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            print(f"📂 {len(news_data)} actualités déjà récupérées")
        except:
            news_data = {}
    
    # Traitement de chaque entreprise
    for idx, (company_name, company_info) in enumerate(companies.items(), 1):
        print(f"\n[{idx}/{len(companies)}] Traitement de {company_name}")
        
        # Skip si déjà traité
        if company_name in news_data and news_data[company_name].get("scrape_metadata", {}).get("success"):
            print(f"⏭️  {company_name} déjà traité, passage au suivant")
            continue
        
        # Récupération des actualités
        company_news = get_company_news(
            company_name=company_name,
            company_website=company_info.get("website", ""),
            industry=company_info.get("industry", "")
        )
        
        # Sauvegarde
        news_data[company_name] = company_news
        
        # Sauvegarde incrémentale
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Progression sauvegardée ({idx}/{len(companies)})")
    
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


def test_single_company(company_name: str = "California Closets"):
    """
    Test sur une seule entreprise pour validation
    
    Args:
        company_name: Nom de l'entreprise à tester
    """
    
    print(f"🧪 Test sur {company_name}...")
    
    # Chargement des infos de l'entreprise
    with open("jobs_data.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # jobs_data.json a une structure où companies est une liste
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
    news = get_company_news(
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
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Mode test sur une seule entreprise
        company = sys.argv[2] if len(sys.argv) > 2 else "California Closets"
        test_single_company(company)
    else:
        # Mode complet
        process_all_companies()

