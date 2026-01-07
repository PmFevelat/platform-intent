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
        prompt = f"""CONTEXT: Presti is an AI-powered platform that generates professional product lifestyle images and visual content for e-commerce companies. We help retailers automate photoshoots, scale their product catalogs, and improve their digital presence.

Search the web for recent news articles about {company_name} from 2024-2026 (prioritize last 6-12 months).

WHAT WE'RE LOOKING FOR (highly relevant to Presti AI):
- Digital transformation, e-commerce website launches/redesigns
- Product catalog expansions, new SKU launches, collection rollouts
- AI adoption, computer vision, 3D/AR/VR technology, automation
- Product photography initiatives, visual content production, imaging technology
- Marketing campaigns with strong visual components
- Customization/personalization programs (product configurators, visual tools)
- Marketplace launches, third-party platform integrations
- Supply chain improvements affecting time-to-market
- Store openings, international expansion
- Technology investments and innovations

DEPRIORITIZE (less relevant):
- Pure quarterly earnings reports (unless they contain strategic insights)
- Stock performance without operational context
- Executive compensation news

SOURCES TO CHECK (but search broadly):
- Modern Retail, Retail Dive, Digital Commerce 360
- Business of Home, Furniture Today (for furniture/home retailers)
- Forbes, Bloomberg, WWD, Business Insider, CNBC
- TechCrunch, The Verge, Wired
- Progressive Grocer, Supermarket News (for grocery retailers)
- Company press releases, blog, LinkedIn

Find AS MANY relevant articles as possible (aim for 15-25 articles). For each article, provide:
- Title
- Source/publication
- Complete URL
- Publication date
- Brief summary (2-3 sentences focusing on operational/strategic aspects)

Search broadly across the web and include articles with actionable insights about digital operations, technology adoption, catalog management, and visual content needs."""
    
    else:  # interviews
        print(f"\n🎤 [Perplexity] Recherche des interviews management pour {company_name}...")
        prompt = f"""CONTEXT: Presti is an AI-powered platform that generates professional product lifestyle images and visual content for e-commerce. We're looking for executive insights about digital transformation, visual content strategy, and technology adoption.

Search for executive interviews and leadership content from {company_name} (2024-2026, prioritize recent content).

TARGET EXECUTIVES (focus on these roles):
- Chief Digital Officer, VP E-commerce, VP Digital, VP Online
- CMO, VP Marketing, Chief Marketing Officer
- CTO, VP Technology, VP Innovation, Chief Innovation Officer
- CEO, President (especially when discussing digital/technology strategy)
- Chief Creative Officer, VP Brand, VP Product, VP Merchandising

WHAT WE'RE LOOKING FOR:
- Digital transformation strategy and roadmap
- E-commerce operations and growth initiatives
- Technology adoption (AI, automation, visual tech, personalization)
- Marketing strategy and visual content approaches
- Product catalog management and expansion
- Customer experience and omnichannel strategy
- Innovation initiatives and future plans
- Store/digital integration

CONTENT TYPES TO FIND:
- Executive interviews (in publications like Modern Retail, Forbes, Business of Home, etc.)
- Conference keynotes and panel discussions
- Earnings calls (ONLY if they include strategic discussion, not just financials)
- Thought leadership articles and op-eds
- Podcast interviews with strategic insights
- Company blog interviews with executives
- LinkedIn posts with substantial strategic content

DEPRIORITIZE:
- Pure quarterly earnings calls without strategic discussion
- Generic leadership profiles without operational/strategic insights
- Stock performance commentary without strategic context

SOURCES TO CHECK (but search broadly):
- Modern Retail, Retail Dive, Forbes, Business Insider
- Business of Home, Furniture Today, WWD
- TechCrunch, The Verge, Chain Store Age
- Industry conference websites, podcast platforms
- LinkedIn, company blogs, press releases

Find AS MANY relevant interviews as possible (aim for 10-15). For each, provide:
- Title
- Source/publication
- Complete URL
- Publication date
- Executive name (first and last name)
- Executive title (full title)
- Key insights discussed (focus on strategy, not just financial metrics)

Search broadly and prioritize content with actionable strategic insights about digital operations, technology, marketing, and innovation."""

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
        system_prompt = """You are an expert at extracting and structuring business news data for Presti AI.

CONTEXT: Presti is an AI platform that generates professional product lifestyle images for e-commerce. Articles are most relevant when they discuss:
- Digital transformation, e-commerce initiatives
- Product catalogs, SKU expansions, visual content needs
- AI adoption, technology innovations
- Marketing campaigns, brand initiatives
- Operational challenges that visual content could solve

Given raw text from a web search, extract and structure ALL relevant articles into clean JSON.

SCORING GUIDELINES (1-10):
- 9-10: Direct relevance to visual content, product photography, catalog scaling, AI/3D tech
- 7-8: Strong e-commerce, digital transformation, or marketing campaigns
- 5-6: General business performance with digital/operational insights
- 3-4: Tangential relevance (expansion, sustainability with visual component)
- 1-2: Financial reports only, no operational insights

IMPORTANT RULES:
1. Extract ALL articles mentioned (aim for 15-25 articles)
2. Use ONLY URLs explicitly provided in text or citations
3. Format ALL dates as "YYYY-MM-DD" (convert "January 15, 2025" → "2025-01-15")
4. Prioritize recent articles (2025-2026)
5. EXCLUDE pure financial reports without strategic insights
6. Extract 3-5 key insights per article (focus on digital/visual/operational aspects)
7. ALL text must be in ENGLISH
8. Remove duplicate articles (same title/URL)

Output format:
{
  "articles": [
    {
      "title": "Exact article title",
      "source": "Publication name",
      "url": "Complete URL",
      "published_date": "YYYY-MM-DD",
      "date": "YYYY-MM-DD",
      "summary": "2-3 sentences focusing on digital/visual/operational implications for e-commerce",
      "presti_score": <1-10>,
      "relevance_reason": "Specific reason why relevant to AI visual content platform",
      "key_insights": [
        "Actionable insight 1",
        "Actionable insight 2",
        "Actionable insight 3"
      ],
      "category": "digital_transformation|ecommerce_growth|catalog_expansion|visual_content|technology_innovation|marketing_campaigns|ai_adoption|international_expansion|sustainability|business_performance"
    }
  ]
}"""
        
        user_prompt = f"""Extract and structure ALL articles about {company_name} from this search result.

PRESTI CONTEXT: Presti helps e-commerce companies generate product lifestyle images with AI. Prioritize articles about digital transformation, e-commerce, catalog expansions, technology adoption, marketing campaigns, and visual content. Include general business news if it has operational insights. Deprioritize pure financial reports.

SEARCH RESULT:
{raw_content}

CITATIONS (verified URLs):
{json.dumps(citations, indent=2)}

INSTRUCTIONS:
1. Extract EVERY article mentioned (aim for 15-25 articles minimum)
2. Use ONLY URLs from citations list above
3. Convert all dates to YYYY-MM-DD format (e.g., "January 15, 2025" → "2025-01-15")
4. Score each article 1-10 based on relevance to Presti (see scoring guidelines in system prompt)
5. Extract 3-5 actionable insights per article
6. Remove duplicate articles (same URL)
7. Include financial reports ONLY if they contain strategic/operational insights

Return ONLY the JSON object, no other text."""
    
    else:  # interviews
        system_prompt = """You are an expert at extracting and structuring executive interview data for Presti AI.

CONTEXT: Presti is an AI platform for e-commerce visual content generation. We value interviews discussing:
- Digital transformation and e-commerce strategy
- Technology adoption (AI, automation, visual tech)
- Marketing and brand strategy
- Product catalog and customer experience
- Innovation roadmaps and future plans

Given raw text from a web search, extract and structure ALL relevant interviews into clean JSON.

SCORING GUIDELINES (1-10):
- 9-10: Deep insights on digital strategy, tech adoption, visual content, or e-commerce operations
- 7-8: Strong strategic insights on marketing, customer experience, or innovation
- 5-6: General business strategy with digital/operational elements
- 3-4: Tangential relevance (leadership philosophy with some operational insights)
- 1-2: Pure financial commentary, no strategic insights

IMPORTANT RULES:
1. Extract ALL interviews/articles mentioned (aim for 10-15)
2. Use ONLY URLs explicitly provided
3. SPLIT executive info into TWO fields:
   - "executive_name": First and last name only (e.g., "Ron Vachris")
   - "executive_title": Title only (e.g., "Chief Executive Officer" or "President and CEO")
4. Format ALL dates as "YYYY-MM-DD"
5. EXCLUDE pure earnings calls without strategic discussion
6. Extract 3-5 key strategic insights (not financial metrics)
7. ALL text must be in ENGLISH
8. Remove duplicates

REQUIRED FIELDS:
- title, source, url, published_date, date
- executive_name (string: "FirstName LastName")
- executive_title (string: "Title")
- format (string: "interview"|"podcast"|"keynote"|"article"|"earnings_call"|"panel"|"webinar"|"profile")
- summary (string: 2-3 sentences)
- key_quotes (array: direct quotes if available, empty array if none)
- topics_discussed (array: main topics covered)
- key_insights (array: 3-5 strategic insights)
- sales_insights (array: insights relevant to sales strategy, can be empty)
- relevance_reason (string: why relevant to Presti)
- relevance_score (number: 1-10, use scoring guidelines above)

Output format:
{
  "interviews": [
    {
      "title": "Article/interview title",
      "source": "Publication",
      "url": "Complete URL",
      "published_date": "YYYY-MM-DD",
      "date": "YYYY-MM-DD",
      "executive_name": "FirstName LastName",
      "executive_title": "Full Title",
      "format": "interview",
      "summary": "2-3 sentences about strategic insights",
      "key_quotes": ["Direct quote 1", "Direct quote 2"],
      "topics_discussed": ["Topic 1", "Topic 2"],
      "key_insights": ["Strategic insight 1", "Strategic insight 2", "Strategic insight 3"],
      "sales_insights": ["Sales-relevant insight 1"],
      "relevance_reason": "Specific reason for relevance to Presti",
      "relevance_score": 8
    }
  ]
}"""
        
        user_prompt = f"""Extract and structure ALL interviews/articles about {company_name} executives.

PRESTI CONTEXT: Presti helps e-commerce generate product visuals with AI. Prioritize interviews about digital transformation, e-commerce strategy, technology adoption, marketing vision, and innovation. Include earnings calls if they discuss strategy (not just financials).

SEARCH RESULT:
{raw_content}

CITATIONS (verified URLs):
{json.dumps(citations, indent=2)}

CRITICAL INSTRUCTIONS:
1. Extract EVERY interview/article mentioned (aim for 10-15 minimum)
2. SPLIT executive info into TWO separate fields:
   - "executive_name": First and last name only (e.g., "Ron Vachris")
   - "executive_title": Title only (e.g., "Chief Executive Officer")
3. Convert all dates to YYYY-MM-DD format
4. Score 1-10 based on strategic insights (see scoring guidelines in system prompt)
5. Include ALL required fields (title, source, url, published_date, date, executive_name, executive_title, format, summary, key_quotes, topics_discussed, key_insights, sales_insights, relevance_reason, relevance_score)
6. Remove duplicate interviews (same URL)
7. Include earnings calls/presentations ONLY if they contain strategic discussion beyond financials

Return ONLY the JSON object with the exact structure specified in the system prompt."""
    
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

