#!/usr/bin/env python3
"""
Script HYBRIDE : Perplexity (recherche) + OpenAI (structuration)
- Perplexity : Trouve les articles récents avec vraies URLs
- OpenAI : Structure les données en JSON propre
"""

import json
import os
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
import argparse
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Configuration
PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")
if not PERPLEXITY_API_KEY:
    raise ValueError("PERPLEXITY_API_KEY environment variable is required")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

MAX_CONCURRENT_REQUESTS = 3
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def search_with_perplexity(
    session: aiohttp.ClientSession,
    company_name: str,
    company_website: str = "",
    industry: str = "",
    search_type: str = "news"
) -> Optional[Dict[str, Any]]:
    """
    ÉTAPE 1 : Recherche avec Perplexity (données fraîches + vraies URLs)
    """
    
    if search_type == "news":
        print(f"\n🔍 [Perplexity] Recherche des actualités pour {company_name}...")
        prompt = f"""Search the web for recent news articles about {company_name} from 2024-2026 (last 6-12 months priority).

TOPICS (cast wide net):
- E-commerce growth, website redesigns, digital transformation
- Product catalog expansions, new collections, SKU increases
- AI adoption, visualization tech, AR/VR, 3D, imaging technology
- Product photography, content production initiatives
- Marketplace launches, third-party platforms
- Customization, personalization programs
- Marketing campaigns, brand initiatives
- Supply chain improvements, time-to-market
- International expansion, new markets
- Sustainability initiatives

SOURCES:
- Trade publications: Furniture Today, Business of Home, Modern Retail, Retail Dive
- Business news: Forbes, Bloomberg, WWD, Business Insider
- Tech news: TechCrunch, The Verge, Wired
- Company sources: {company_name} blog, press releases, LinkedIn

Find 10-15 articles with REAL URLs. List each with:
- Title
- Source/publication
- Complete URL
- Publication date
- Brief summary (2-3 sentences)

Search extensively across all these sources."""
    
    else:  # interviews
        print(f"\n🎤 [Perplexity] Recherche des interviews management pour {company_name}...")
        prompt = f"""Search the web for executive interviews and leadership content from {company_name} (2024-2026).

TARGET EXECUTIVES:
- CEO, President, CMO, Chief Digital Officer, VP E-commerce
- CTO, Chief Creative Officer, VP Marketing, VP Innovation
- VP Brand, VP Product, Directors (Digital, E-commerce, Marketing)

CONTENT TYPES:
- Executive interviews (Forbes, Modern Retail, Business of Home, Furniture Today, WWD)
- Conference talks (KBIS, High Point Market, keynotes, panels)
- Thought leadership (LinkedIn, op-eds, guest articles)
- Podcasts, webinars, industry events
- Company blog, press interviews

TOPICS:
- Digital transformation, e-commerce strategy
- Technology roadmap, AI adoption
- Marketing vision, brand strategy
- Customer experience, innovation
- Visual content approaches
- Future plans 2025-2026

Find 8-12 articles/interviews with REAL URLs. List each with:
- Title
- Source
- Complete URL
- Date
- Executive name and title
- Key insights from the executive

Search extensively."""

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a research expert. Search the web thoroughly and provide detailed information with real URLs from your search results."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 4000,
        "temperature": 0.2,
        "return_citations": True,
        "return_images": False
    }
    
    try:
        async with session.post(PERPLEXITY_URL, headers=headers, json=payload, timeout=90) as response:
            if response.status != 200:
                error_text = await response.text()
                print(f"❌ Erreur Perplexity (status {response.status})")
                return None
            
            result = await response.json()
            
            if 'choices' not in result or len(result['choices']) == 0:
                print(f"⚠️ Aucun résultat Perplexity")
                return None
            
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            print(f"✅ Perplexity : {len(content)} caractères, {len(citations)} citations")
            
            return {
                "raw_content": content,
                "citations": citations,
                "company_name": company_name
            }
    
    except Exception as e:
        print(f"❌ Erreur Perplexity: {e}")
        return None


async def structure_with_openai(
    perplexity_data: Dict[str, Any],
    search_type: str = "news"
) -> Optional[Dict[str, Any]]:
    """
    ÉTAPE 2 : Structuration avec OpenAI (JSON propre et fiable)
    """
    
    company_name = perplexity_data['company_name']
    raw_content = perplexity_data['raw_content']
    citations = perplexity_data['citations']
    
    print(f"\n📊 [OpenAI] Structuration des données pour {company_name}...")
    
    if search_type == "news":
        system_prompt = """You are an expert at extracting and structuring business news data.

Given raw text from a web search about company news, extract and structure the information into clean JSON.

IMPORTANT RULES:
1. Extract ALL articles mentioned in the text
2. Use ONLY the URLs that are explicitly provided in the text or citations
3. Format dates as "YYYY-MM-DD" when possible, or keep original format
4. Assign relevance scores 1-10 based on relevance for an AI visual content company (generates product lifestyle images)
5. Extract key insights (3-5 bullet points per article)
6. Categorize each article appropriately
7. ALL text must be in ENGLISH

Output format:
{
  "articles": [
    {
      "title": "Exact article title",
      "source": "Publication name",
      "url": "Complete URL (must be from the provided text/citations)",
      "published_date": "Month DD, YYYY or YYYY-MM-DD",
      "date": "YYYY-MM-DD",
      "summary": "2-3 sentence summary focusing on digital/visual implications",
      "presti_score": <1-10>,
      "relevance_reason": "Why relevant for AI visual content company",
      "key_insights": [
        "Insight 1",
        "Insight 2",
        "Insight 3"
      ],
      "category": "technology_innovation|ecommerce_growth|catalog_expansion|visual_content|digital_transformation|marketing_campaigns|supply_chain_challenges|international_expansion|sustainability|business_performance"
    }
  ]
}"""
        
        user_prompt = f"""Extract and structure ALL articles about {company_name} from this search result.

SEARCH RESULT:
{raw_content}

CITATIONS (verified URLs):
{json.dumps(citations, indent=2)}

Extract every article mentioned. Ensure all URLs are from the citations list above.
Return ONLY the JSON object, no other text."""
    
    else:  # interviews
        system_prompt = """You are an expert at extracting and structuring executive interview data.

Given raw text from a web search about executive interviews, extract and structure the information into clean JSON.

IMPORTANT RULES:
1. Extract ALL interviews/articles mentioned
2. Use ONLY the URLs explicitly provided
3. Extract executive names and titles when mentioned
4. Format dates as "YYYY-MM-DD" when possible
5. Extract key insights from each executive
6. ALL text must be in ENGLISH

Output format:
{
  "interviews": [
    {
      "title": "Article/interview title",
      "source": "Publication",
      "url": "Complete URL",
      "published_date": "Month DD, YYYY or YYYY-MM-DD",
      "date": "YYYY-MM-DD",
      "executive": "Name and Title",
      "summary": "2-3 sentences about the executive's insights",
      "key_insights": [
        "Key point 1",
        "Key point 2",
        "Key point 3"
      ],
      "presti_score": <1-10>
    }
  ]
}"""
        
        user_prompt = f"""Extract and structure ALL interviews/articles about {company_name} executives.

SEARCH RESULT:
{raw_content}

CITATIONS (verified URLs):
{json.dumps(citations, indent=2)}

Return ONLY the JSON object."""
    
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        structured_data = json.loads(content)
        
        if search_type == "news":
            articles = structured_data.get('articles', [])
            print(f"✅ OpenAI : {len(articles)} articles structurés")
            return articles
        else:
            interviews = structured_data.get('interviews', [])
            print(f"✅ OpenAI : {len(interviews)} interviews structurées")
            return interviews
    
    except Exception as e:
        print(f"❌ Erreur OpenAI: {e}")
        return None


async def scrape_company_news(
    session: aiohttp.ClientSession,
    company_name: str,
    company_website: str = "",
    industry: str = ""
) -> Optional[Dict[str, Any]]:
    """
    Pipeline complet : Perplexity → OpenAI pour Company News
    """
    
    # Étape 1 : Recherche Perplexity
    perplexity_result = await search_with_perplexity(
        session, company_name, company_website, industry, "news"
    )
    
    if not perplexity_result:
        return None
    
    # Étape 2 : Structuration OpenAI
    structured_articles = await structure_with_openai(perplexity_result, "news")
    
    if not structured_articles:
        return None
    
    return {
        "company_name": company_name,
        "news_items": structured_articles,
        "search_date": datetime.now().isoformat(),
        "scrape_metadata": {
            "timestamp": datetime.now().isoformat(),
            "search_engine": "perplexity-sonar",
            "structuring_model": "gpt-4o",
            "success": True,
            "articles_found": len(structured_articles)
        }
    }


async def scrape_management_interviews(
    session: aiohttp.ClientSession,
    company_name: str,
    company_website: str = "",
    industry: str = ""
) -> Optional[Dict[str, Any]]:
    """
    Pipeline complet : Perplexity → OpenAI pour Management Interviews
    """
    
    # Étape 1 : Recherche Perplexity
    perplexity_result = await search_with_perplexity(
        session, company_name, company_website, industry, "interviews"
    )
    
    if not perplexity_result:
        return None
    
    # Étape 2 : Structuration OpenAI
    structured_interviews = await structure_with_openai(perplexity_result, "interviews")
    
    if not structured_interviews:
        return None
    
    return {
        "company_name": company_name,
        "interviews": structured_interviews,
        "search_date": datetime.now().isoformat(),
        "scrape_metadata": {
            "timestamp": datetime.now().isoformat(),
            "search_engine": "perplexity-sonar",
            "structuring_model": "gpt-4o",
            "success": True,
            "interviews_found": len(structured_interviews)
        }
    }


async def scrape_company(
    company_name: str,
    company_website: str = "",
    industry: str = "",
    include_interviews: bool = False
) -> Dict[str, Any]:
    """
    Scrape complet d'une entreprise (news + optionnellement interviews)
    """
    async with aiohttp.ClientSession() as session:
        results = {}
        
        # Company News
        news = await scrape_company_news(session, company_name, company_website, industry)
        if news:
            results['news'] = news
        
        # Management Interviews (optionnel)
        if include_interviews:
            interviews = await scrape_management_interviews(session, company_name, company_website, industry)
            if interviews:
                results['interviews'] = interviews
        
        return results


async def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Scraper HYBRIDE : Perplexity + OpenAI')
    parser.add_argument('--company', type=str, help='Nom d\'une entreprise')
    parser.add_argument('--interviews', action='store_true', help='Inclure management interviews')
    
    args = parser.parse_args()
    
    if not args.company:
        print("❌ Veuillez spécifier --company <nom>")
        parser.print_help()
        return
    
    print(f"\n{'='*80}")
    print(f"🚀 SCRAPING HYBRIDE : Perplexity (recherche) + OpenAI (structuration)")
    print(f"{'='*80}")
    print(f"🏢 Entreprise : {args.company}")
    print(f"{'='*80}\n")
    
    # Charger les infos de l'entreprise
    company_info = {'name': args.company, 'website': '', 'industry': ''}
    try:
        with open('jobs_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for company_data in data.get('companies', []):
                if company_data['company']['name'] == args.company:
                    company_info = {
                        'name': company_data['company']['name'],
                        'website': company_data['company'].get('website', ''),
                        'industry': company_data['company'].get('industry', '')
                    }
                    break
    except:
        pass
    
    results = await scrape_company(
        company_info['name'],
        company_info['website'],
        company_info['industry'],
        args.interviews
    )
    
    # Sauvegarder
    output_file = f'hybrid_{args.company.replace(" ", "_")}_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ Résultats sauvegardés dans {output_file}")
    print(f"{'='*80}")
    
    if 'news' in results:
        print(f"📰 Company News : {len(results['news']['news_items'])} articles")
        print(f"\n📝 Aperçu des articles:")
        for i, article in enumerate(results['news']['news_items'][:5], 1):
            print(f"   {i}. {article.get('title', 'N/A')[:70]}...")
            print(f"      📰 {article.get('source')} | ⭐ {article.get('presti_score')}/10")
    
    if 'interviews' in results:
        print(f"\n🎤 Management Interviews : {len(results['interviews']['interviews'])} interviews")
        for i, interview in enumerate(results['interviews']['interviews'][:5], 1):
            print(f"   {i}. {interview.get('title', 'N/A')[:70]}...")
            print(f"      👤 {interview.get('executive', 'N/A')}")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())

