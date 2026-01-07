#!/usr/bin/env python3
"""
Script de scraping MULTI-RECHERCHES : plusieurs requêtes thématiques en parallèle
Pour maximiser le nombre d'articles trouvés (objectif : 15-25 articles)
"""

import json
import os
import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any
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

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


def normalize_date_for_sorting(date_str: str) -> str:
    """
    Convertir la date en format YYYY-MM-DD pour le tri chronologique.
    Garde published_date dans son format original.
    
    Args:
        date_str: Date au format "December 2025", "2025-12-15", "2025", etc.
    
    Returns:
        Date normalisée au format YYYY-MM-DD
    """
    if not date_str or date_str == "N/A":
        return "2025-01-01"
    
    # Déjà au format YYYY-MM-DD
    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        return date_str
    
    # Format "Month YYYY" (ex: "December 2025")
    months = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }
    
    for month_name, month_num in months.items():
        if month_name.lower() in date_str.lower():
            # Extraire l'année
            parts = date_str.split()
            year = parts[-1] if len(parts) > 0 else "2025"
            return f"{year}-{month_num}-01"
    
    # Juste une année "2025"
    if len(date_str) == 4 and date_str.isdigit():
        return f"{date_str}-01-01"
    
    # Fallback
    return "2025-01-01"


async def search_perplexity_theme(
    session: aiohttp.ClientSession,
    company_name: str,
    theme: str,
    search_type: str = "news"
) -> Dict[str, Any]:
    """
    Recherche ciblée sur un thème spécifique
    """
    
    # Définition des thèmes pour NEWS
    news_themes = {
        "digital": {
            "keywords": "digital transformation, e-commerce, website redesign, online sales, digital sales, app, mobile",
            "description": "Digital & E-commerce"
        },
        "tech": {
            "keywords": "AI, artificial intelligence, automation, 3D, AR, VR, computer vision, technology innovation",
            "description": "Technology & AI"
        },
        "expansion": {
            "keywords": "new stores, warehouse openings, expansion, international markets, new locations",
            "description": "Expansion & Growth"
        },
        "catalog": {
            "keywords": "product catalog, new products, SKU, collections, assortment, merchandise",
            "description": "Products & Catalog"
        },
        "marketing": {
            "keywords": "marketing campaign, advertising, brand, visual content, photography, content production",
            "description": "Marketing & Brand"
        }
    }
    
    # Définition des thèmes pour INTERVIEWS
    interview_themes = {
        "digital_leaders": {
            "roles": "Chief Digital Officer, VP E-commerce, VP Digital, VP Online",
            "description": "Digital & E-commerce Leaders"
        },
        "marketing_leaders": {
            "roles": "CMO, Chief Marketing Officer, VP Marketing, VP Brand",
            "description": "Marketing Leaders"
        },
        "tech_leaders": {
            "roles": "CTO, Chief Technology Officer, VP Technology, VP Innovation",
            "description": "Technology Leaders"
        },
        "ceo_strategic": {
            "roles": "CEO, President, Chief Executive",
            "description": "CEO & Strategic Leadership"
        }
    }
    
    if search_type == "news":
        theme_data = news_themes.get(theme, news_themes["digital"])
        print(f"  📍 Recherche thématique: {theme_data['description']}")
        
        prompt = f"""Search for recent news articles about {company_name} (2024-2026, prioritize 2025-2026) focused on: {theme_data['keywords']}.

CRITICAL: For EACH article found, you MUST identify and include the EXACT publication date from the article.

Find 4-6 relevant articles and for EACH provide:
- Title (exact)
- Source (publication name)
- URL (complete)
- **Publication date (EXACT date from article, format: "Month DD, YYYY" or "YYYY-MM-DD")**
- Brief summary

When listing each article, start with: "Article published on [EXACT DATE]:" then provide the details.

Focus on articles discussing: {theme_data['keywords']}"""
    
    else:  # interviews
        theme_data = interview_themes.get(theme, interview_themes["ceo_strategic"])
        print(f"  🎤 Recherche thématique: {theme_data['description']}")
        
        prompt = f"""Search for executive interviews from {company_name} (2024-2026) featuring: {theme_data['roles']}.

CRITICAL: For EACH interview found, you MUST identify and include the EXACT publication date from the article.

Find 2-3 relevant interviews and for EACH provide:
- Title (exact)
- Source (publication name)
- URL (complete)
- **Publication date (EXACT date from article, format: "Month DD, YYYY" or "YYYY-MM-DD")**
- Executive name and title (from article)
- Key insights discussed

When listing each interview, start with: "Interview published on [EXACT DATE]:" then provide the details.

Focus on these roles: {theme_data['roles']}"""
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a research expert. Search the web and provide detailed information with real URLs."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 3000,
        "temperature": 0.2,
        "return_citations": True
    }
    
    try:
        async with session.post(PERPLEXITY_URL, headers=headers, json=payload, timeout=90) as response:
            if response.status != 200:
                print(f"    ⚠️ Erreur {response.status} pour thème {theme}")
                return {"theme": theme, "content": "", "citations": []}
            
            result = await response.json()
            content = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            print(f"    ✓ {len(citations)} citations trouvées")
            
            return {
                "theme": theme,
                "content": content,
                "citations": citations
            }
    
    except Exception as e:
        print(f"    ❌ Erreur pour thème {theme}: {e}")
        return {"theme": theme, "content": "", "citations": []}


async def scrape_company_news_multi(
    company_name: str
) -> Dict[str, Any]:
    """
    Scrape company news avec PLUSIEURS recherches thématiques
    """
    
    print(f"\n{'='*80}")
    print(f"📰 SCRAPING MULTI-THÉMATIQUE : Company News pour {company_name}")
    print(f"{'='*80}")
    
    async with aiohttp.ClientSession() as session:
        # Lancer 5 recherches en parallèle
        themes = ["digital", "tech", "expansion", "catalog", "marketing"]
        
        print(f"\n🔍 Lancement de {len(themes)} recherches parallèles...")
        tasks = [
            search_perplexity_theme(session, company_name, theme, "news")
            for theme in themes
        ]
        
        all_results = await asyncio.gather(*tasks)
        
        # Combiner tous les contenus et citations
        combined_content = "\n\n---THEME SEPARATOR---\n\n".join([
            f"THEME: {r['theme']}\n{r['content']}"
            for r in all_results if r['content']
        ])
        
        all_citations = []
        for r in all_results:
            all_citations.extend(r['citations'])
        
        print(f"\n✅ {len(all_results)} recherches terminées")
        print(f"📊 Total: {len(combined_content)} caractères, {len(all_citations)} citations")
        
        # Structurer avec OpenAI
        print(f"\n📊 [OpenAI] Structuration de tous les articles...")
        
        system_prompt = """You are an expert at extracting and structuring business news data for Presti AI.

CONTEXT: Presti is an AI platform that generates professional product lifestyle images for e-commerce. We work with retailers selling:
✅ CORE RELEVANT SECTORS:
- Furniture & Home Decor (sofas, tables, beds, lighting, rugs, etc.)
- Fashion & Apparel (clothing, shoes, accessories)
- Home Improvement & DIY (tools, building materials, home renovation)
- Home & Kitchen (appliances, kitchenware, home goods)
- Beauty & Personal Care (cosmetics, skincare)
- Electronics & Technology (computers, phones, gadgets)
- Jewelry & Watches
- Sports & Outdoor Equipment

🔄 MULTI-CATEGORY RETAILERS (Walmart, Target, Costco, Amazon, etc.):
- INCLUDE articles about digital/e-commerce/technology strategy
- INCLUDE articles about omnichannel, app, website, personalization
- INCLUDE articles about general merchandise, furniture, home, fashion, electronics
- EXCLUDE ONLY pure food product launches (e.g., "12 new snacks coming in January")
- INCLUDE if mixed product categories (e.g., "New product launches include furniture and food")

WHAT MAKES AN ARTICLE RELEVANT:
- Digital transformation, e-commerce website launches/redesigns
- Product catalog expansions in ANY non-food category
- AI/3D/AR/VR technology for product visualization or shopping
- Product photography, visual content production, content marketing
- Marketplace launches, omnichannel strategies, BOPIS, delivery
- Store designs, visual merchandising, display innovations
- Marketing campaigns with strong visual components
- Technology investments in e-commerce infrastructure

SUMMARY REQUIREMENTS:
- Write 4-5 sentences (not 2-3)
- First sentence: What is the article about?
- Next sentences: Key strategic/operational details relevant to Presti
- Final sentence: Why this matters for visual content/e-commerce
- If article is about food/grocery launches, mention it clearly and score LOW

SCORING GUIDELINES (1-10):
- 9-10: Visual content, product photography, 3D/AR/VR, catalog scaling, or strong digital transformation
- 7-8: E-commerce growth, website/app launches, omnichannel, technology adoption, or relevant product categories (furniture, fashion, electronics, home improvement)
- 5-6: General business with digital/operational insights, store expansions, marketing campaigns
- 3-4: Tangential relevance (some relevant elements but limited depth)
- 1-2: Not relevant (pure food launches) OR pure financial reports without insights

IMPORTANT RULES:
1. Extract articles (aim for 15-20 high-quality articles)
2. EXCLUDE pure food/grocery product launches
3. INCLUDE food retailers if discussing digital/tech/e-commerce strategy
4. Remove duplicates (same title or URL)
5. **DATE PARSING (CRITICAL - READ CAREFULLY)**:
   - Look for ANY date mentioned in the search results for each article
   - Common date formats to look for:
     * Near title: "December 15, 2025", "Dec 15, 2025", "15 Dec 2025"
     * With phrases: "Published on...", "Posted...", "Updated..."
     * In byline: "By Author Name | December 15, 2025"
     * Standalone: Just a date without descriptive text
   - Extract the MOST SPECIFIC date you can find
   - If multiple dates, prefer the publication/posted date over update dates
   - Convert to appropriate format based on specificity:
     * Specific date: "December 15, 2025" → "2025-12-15"
     * Specific date: "Dec 7, 2025" → "2025-12-07"
     * Month only: "November 2025" → "November 2025" (keep as is, don't add day)
     * Month only: "Dec 2025" → "December 2025"
     * Quarter: "Q4 2025" → "Q4 2025" or "October 2025"
     * Year only: "2025" → "2025"
   - If NO date found, use "2025" as fallback
   - DON'T invent days when only month/year is known
6. Write detailed 4-5 sentence summaries
7. Extract 3-5 actionable insights per article
8. ALL text must be in ENGLISH

Output format:
{
  "articles": [
    {
      "title": "Exact article title",
      "source": "Publication name",
      "url": "Complete URL",
      "published_date": "YYYY-MM-DD",
      "date": "YYYY-MM-DD",
      "summary": "4-5 sentences explaining what the article is about, key details, and why it matters for visual content/e-commerce. Be specific about products/sectors mentioned.",
      "presti_score": <1-10>,
      "relevance_reason": "Specific reason why relevant to Presti (mention sector and visual content angle)",
      "key_insights": [
        "Actionable insight 1",
        "Actionable insight 2",
        "Actionable insight 3"
      ],
      "category": "digital_transformation|ecommerce_growth|catalog_expansion|visual_content|technology_innovation|marketing_campaigns|ai_adoption|store_design|international_expansion|sustainability|business_performance"
    }
  ]
}"""
        
        user_prompt = f"""Extract and structure relevant articles about {company_name} from these search results.

PRESTI CONTEXT: We generate product lifestyle images for e-commerce. Relevant articles discuss digital/e-commerce/tech, OR product categories like furniture, home decor, fashion, electronics, home improvement, etc.

COMBINED SEARCH RESULTS:
{combined_content}

ALL CITATIONS:
{json.dumps(list(set(all_citations)), indent=2)}

CRITICAL INSTRUCTIONS:
1. Extract unique articles (aim for 15-20 articles)
2. INCLUDE:
   ✅ Any digital transformation, e-commerce, website, app, technology article
   ✅ Articles about furniture, home decor, fashion, electronics, home improvement
   ✅ AI/AR/VR, personalization, visual tech, photography initiatives
   ✅ Omnichannel, marketplace, delivery, BOPIS strategies
   ✅ Store designs, visual merchandising, catalog expansions
   ✅ Multi-category articles (even if some food is mentioned)
3. EXCLUDE ONLY:
   ❌ Pure food product launches with NO other product categories
   ❌ Pure restaurant/food service news
   ❌ Pure financial reports without operational insights
4. Write 4-5 sentence summaries explaining:
   - What is the article about?
   - Key strategic/operational details
   - Product categories OR digital initiatives mentioned
   - Why it matters for visual content/e-commerce
5. Remove duplicates (same title/URL)
6. Use ONLY URLs from citations
7. **DATE EXTRACTION (CRITICAL)**:
   - Look for ANY date near article title or in content snippets
   - Check for: "December 15, 2025", "Dec 15, 2025", "15 Dec 2025", or standalone dates
   - Also check phrases: "Published...", "Posted...", "Updated..." but don't require them
   - Extract the MOST SPECIFIC date mentioned
   - Convert based on specificity:
     * Specific date: "December 15, 2025" → "2025-12-15"
     * Month only: "November 2025" → "November 2025" (keep month, don't add day)
     * Year only: "2025" → "2025"
   - Fallback if NO date: "2025"
   - IMPORTANT: Don't invent days when only month is known
8. Score based on: digital/tech angle (9-10), relevant product categories (7-8), mixed relevance (5-6)

FILTERING EXAMPLES:
✅ INCLUDE: "Costco's digital transformation drives 20% e-commerce growth" (digital strategy)
✅ INCLUDE: "Costco expands furniture and home decor offerings" (relevant products)
✅ INCLUDE: "Costco opens 28 new warehouses in 2026" (expansion, visual merchandising)
❌ EXCLUDE: "Costco adds 13 new food items: snacks, beverages, frozen meals" (pure food)
✅ INCLUDE: "Major changes at Costco: self-checkout, app updates" (digital/tech)

Return ONLY the JSON object."""
        
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        structured_data = json.loads(response.choices[0].message.content)
        articles = structured_data.get('articles', [])
        
        # Post-processing: Ajouter champ "date" normalisé pour le tri, garder published_date original
        for article in articles:
            original_date = article.get('published_date', '')
            # published_date garde le format original (ex: "December 2025")
            # date est normalisé pour le tri (ex: "2025-12-01")
            article['date'] = normalize_date_for_sorting(original_date)
        
        print(f"✅ {len(articles)} articles uniques structurés")
        
        return {
            "company_name": company_name,
            "news_items": articles,
            "search_date": datetime.now().isoformat(),
            "scrape_metadata": {
                "timestamp": datetime.now().isoformat(),
                "search_engine": "perplexity-sonar",
                "structuring_model": "gpt-4o",
                "success": True,
                "articles_found": len(articles),
                "themes_searched": themes
            }
        }


async def scrape_management_interviews_multi(
    company_name: str
) -> Dict[str, Any]:
    """
    Scrape management interviews avec PLUSIEURS recherches thématiques
    """
    
    print(f"\n{'='*80}")
    print(f"🎤 SCRAPING MULTI-THÉMATIQUE : Management Interviews pour {company_name}")
    print(f"{'='*80}")
    
    async with aiohttp.ClientSession() as session:
        # Lancer 4 recherches en parallèle
        themes = ["digital_leaders", "marketing_leaders", "tech_leaders", "ceo_strategic"]
        
        print(f"\n🔍 Lancement de {len(themes)} recherches parallèles...")
        tasks = [
            search_perplexity_theme(session, company_name, theme, "interviews")
            for theme in themes
        ]
        
        all_results = await asyncio.gather(*tasks)
        
        # Combiner tous les contenus
        combined_content = "\n\n---THEME SEPARATOR---\n\n".join([
            f"THEME: {r['theme']}\n{r['content']}"
            for r in all_results if r['content']
        ])
        
        all_citations = []
        for r in all_results:
            all_citations.extend(r['citations'])
        
        print(f"\n✅ {len(all_results)} recherches terminées")
        print(f"📊 Total: {len(combined_content)} caractères, {len(all_citations)} citations")
        
        # Structurer avec OpenAI
        print(f"\n📊 [OpenAI] Structuration de toutes les interviews...")
        
        system_prompt = """You are an expert at extracting and structuring executive interview data for Presti AI.

CONTEXT: Presti is an AI platform that generates product lifestyle images for e-commerce in: Furniture, Home Decor, Fashion, Home Improvement, Electronics, Beauty.

WHAT MAKES AN INTERVIEW RELEVANT:
- Digital transformation, e-commerce strategy, omnichannel initiatives
- Technology adoption (AI, AR/VR, 3D, automation, personalization)
- Marketing strategy, visual content approach, brand building
- Product catalog management, merchandising, assortment strategy
- Customer experience, UX/UI, app/website enhancements
- Innovation roadmaps, future plans for digital/visual
- Supply chain & operations (if related to product availability/catalog)

EXCLUDE:
- Pure financial commentary without strategic insights
- Generic leadership profiles without operational depth
- Earnings calls that only discuss financial metrics

SUMMARY REQUIREMENTS:
- Write 3-4 sentences summarizing executive's key strategic insights
- Focus on digital, technology, marketing, or innovation topics
- Mention specific initiatives or future plans discussed
- Explain why these insights matter for Presti's business

SCORING GUIDELINES (1-10):
- 9-10: Deep insights on digital strategy, tech adoption, visual content, or e-commerce ops
- 7-8: Strong strategic insights on marketing, customer experience, or innovation
- 5-6: General business strategy with some digital/operational elements
- 3-4: Tangential relevance or limited strategic depth
- 1-2: Pure financial commentary without strategic insights

IMPORTANT RULES:
1. Extract unique interviews (aim for 10-12 HIGH-QUALITY interviews)
2. Remove duplicates (same title/URL)
3. SPLIT executive info into TWO fields:
   - "executive_name": First and last name only (e.g., "Marvin Ellison")
   - "executive_title": Title only (e.g., "President and Chief Executive Officer")
4. **DATE PARSING (CRITICAL)**:
   - Look for ANY date mentioned near the interview title or in content
   - Common formats: "December 15, 2025", "Dec 15, 2025", "15 Dec 2025"
   - Check phrases: "Published...", "Posted...", or standalone dates
   - Extract the MOST SPECIFIC date you can find
   - Convert based on specificity:
     * Specific date: "December 15, 2025" → "2025-12-15"
     * Month only: "November 2025" → "November 2025" (don't add day)
     * Year only: "2025" → "2025"
   - If NO date found, use "2025" as fallback
   - DON'T invent days when only month/year is known
5. Write detailed 3-4 sentence summaries
6. Include all required fields
7. ALL text must be in ENGLISH

REQUIRED FIELDS:
- title, source, url, published_date, date
- executive_name (string: "FirstName LastName")
- executive_title (string: "Title")
- format (string: "interview"|"podcast"|"keynote"|"article"|"earnings_call"|"panel"|"webinar"|"profile")
- summary (string: 3-4 sentences about strategic insights)
- key_quotes (array: direct quotes if available, empty array if none)
- topics_discussed (array: main topics covered)
- key_insights (array: 3-5 strategic insights, NOT financial metrics)
- sales_insights (array: insights relevant to sales strategy, can be empty)
- relevance_reason (string: why relevant to Presti)
- relevance_score (number: 1-10, use scoring guidelines above)

Output format:
{
  "interviews": [
    {
      "title": "Interview title",
      "source": "Publication",
      "url": "Complete URL",
      "published_date": "YYYY-MM-DD",
      "date": "YYYY-MM-DD",
      "executive_name": "FirstName LastName",
      "executive_title": "Full Title",
      "format": "interview",
      "summary": "3-4 sentences explaining executive's strategic insights, specific initiatives discussed, and why they matter for Presti.",
      "key_quotes": ["Direct quote 1", "Direct quote 2"],
      "topics_discussed": ["Topic 1", "Topic 2", "Topic 3"],
      "key_insights": ["Strategic insight 1", "Strategic insight 2", "Strategic insight 3"],
      "sales_insights": ["Sales-relevant insight 1"],
      "relevance_reason": "Specific reason for relevance to Presti",
      "relevance_score": 8
    }
  ]
}"""
        
        user_prompt = f"""Extract and structure relevant interviews about {company_name} executives.

PRESTI FOCUS: Interviews discussing digital transformation, e-commerce, technology adoption, marketing strategy, visual content, product catalog management, or innovation.

COMBINED SEARCH RESULTS:
{combined_content}

ALL CITATIONS:
{json.dumps(list(set(all_citations)), indent=2)}

CRITICAL INSTRUCTIONS:
1. Extract unique interviews (aim for 10-12 HIGH-QUALITY interviews)
2. EXCLUDE pure earnings calls that only discuss financial metrics
3. INCLUDE earnings calls if they discuss strategic initiatives
4. Write 3-4 sentence summaries explaining:
   - Executive's key strategic insights
   - Specific initiatives or plans discussed
   - Why these insights matter for Presti (visual content/e-commerce platform)
5. SPLIT executive info into "executive_name" (name only) and "executive_title" (title only)
6. Remove duplicates (same title/URL)
7. Use ONLY URLs from citations
8. **DATE EXTRACTION (CRITICAL)**:
   - Look for ANY date near interview title or in content
   - Check for: "December 15, 2025", "Dec 15, 2025", or standalone dates
   - Extract the MOST SPECIFIC date mentioned
   - Convert based on specificity:
     * Specific date: "December 15, 2025" → "2025-12-15"
     * Month only: "November 2025" → "November 2025" (keep month, don't add day)
     * Year only: "2025" → "2025"
   - Fallback if NO date: "2025"
   - IMPORTANT: Don't invent days when only month is known
9. Include ALL required fields (see system prompt)
10. Score 1-10 based on depth of strategic insights (not financial commentary)

FILTERING EXAMPLES:
✅ INCLUDE: "CMO discusses digital marketing transformation and visual content strategy"
✅ INCLUDE: "CEO on AI adoption for product personalization and e-commerce growth"
❌ EXCLUDE: "Q4 earnings call" (if only discussing revenue/profit without strategy)
✅ INCLUDE: "Q4 earnings call highlights digital transformation roadmap"

Return ONLY the JSON object with the exact structure specified in the system prompt."""
        
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        structured_data = json.loads(response.choices[0].message.content)
        interviews = structured_data.get('interviews', [])
        
        # Post-processing: Ajouter champ "date" normalisé pour le tri, garder published_date original
        for interview in interviews:
            original_date = interview.get('published_date', '')
            # published_date garde le format original (ex: "December 2025")
            # date est normalisé pour le tri (ex: "2025-12-01")
            interview['date'] = normalize_date_for_sorting(original_date)
            
            # S'assurer que relevance_score existe (frontend l'attend)
            if 'relevance_score' not in interview:
                interview['relevance_score'] = interview.get('presti_score', 5)
            
            # S'assurer que les champs requis existent
            if 'key_quotes' not in interview:
                interview['key_quotes'] = []
            if 'topics_discussed' not in interview:
                interview['topics_discussed'] = []
            if 'sales_insights' not in interview:
                interview['sales_insights'] = []
        
        print(f"✅ {len(interviews)} interviews uniques structurées")
        
        return {
            "company_name": company_name,
            "interviews": interviews,
            "management_items": interviews,  # Pour le frontend
            "search_date": datetime.now().isoformat(),
            "scrape_metadata": {
                "timestamp": datetime.now().isoformat(),
                "search_engine": "perplexity-sonar",
                "structuring_model": "gpt-4o",
                "success": True,
                "interviews_found": len(interviews),
                "themes_searched": themes
            }
        }


async def main():
    parser = argparse.ArgumentParser(description='Scraper MULTI-THÉMATIQUE')
    parser.add_argument('--company', type=str, required=True, help='Nom de l\'entreprise')
    parser.add_argument('--interviews', action='store_true', help='Inclure management interviews')
    
    args = parser.parse_args()
    
    print(f"\n{'='*80}")
    print(f"🚀 SCRAPING MULTI-THÉMATIQUE")
    print(f"{'='*80}")
    print(f"🏢 Entreprise : {args.company}")
    print(f"{'='*80}")
    
    results = {}
    
    # Company News
    news = await scrape_company_news_multi(args.company)
    results['news'] = news
    
    # Management Interviews
    if args.interviews:
        interviews = await scrape_management_interviews_multi(args.company)
        results['interviews'] = interviews
    
    # Sauvegarder
    output_file = f'multi_{args.company.replace(" ", "_")}_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"✅ Résultats sauvegardés dans {output_file}")
    print(f"{'='*80}")
    print(f"📰 Company News : {len(news['news_items'])} articles")
    if args.interviews:
        print(f"🎤 Management Interviews : {len(interviews['interviews'])} interviews")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())

