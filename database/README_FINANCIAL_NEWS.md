# 💰 Financial News - Documentation

## Vue d'ensemble

La fonctionnalité **Financial News** permet de collecter et d'afficher les informations financières des entreprises cibles, incluant :

- 📊 **Earnings Calls & Transcripts** - Appels de résultats trimestriels
- 📄 **SEC Filings** - Rapports officiels (10-K, 10-Q)
- 📈 **Quarterly Results** - Résultats financiers par trimestre
- 📰 **Press Releases** - Communiqués de presse financiers
- 📊 **Analyst Reports** - Rapports et analyses d'analystes

## 🎯 Sources de données

Le script utilise **Perplexity API** pour rechercher des informations financières provenant de :

- **Yahoo Finance** - Données financières et résumés d'earnings
- **SEC Edgar** - Rapports officiels (sec.gov)
- **Sites Investor Relations** - Communications officielles des entreprises
- **SeekingAlpha** - Transcripts d'earnings calls
- **Médias financiers** - Reuters, Bloomberg, WSJ, etc.

## 🔧 Installation

Les dépendances sont déjà installées dans l'environnement virtuel `venv_async` :

```bash
cd database
source venv_async/bin/activate
```

## 📝 Configuration

Assurez-vous que votre fichier `.env` contient :

```bash
PERPLEXITY_API_KEY=your_perplexity_api_key
OPENAI_API_KEY=your_openai_api_key
```

## 🚀 Utilisation

### Scraper une entreprise individuelle

```bash
cd database
source venv_async/bin/activate
python3 scrape_financial_news.py --company "MillerKnoll"
```

**Résultat** : Un fichier `financial_MillerKnoll_results.json` sera créé.

### Mettre à jour toutes les entreprises

```bash
cd database
./update_financial_news.sh
```

**Résultat** : Le fichier `public/financial_news.json` sera mis à jour avec les données de toutes les entreprises.

**Durée estimée** : ~5-10 minutes pour 26 entreprises (2-3 secondes par entreprise + pause)

## 📊 Structure des données

### Format JSON

```json
{
  "MillerKnoll": {
    "company_name": "MillerKnoll",
    "financial_items": [
      {
        "title": "MillerKnoll, Inc. Q2 2025 Earnings Call Transcript",
        "source": "TMX Money",
        "url": "https://...",
        "published_date": "2024-11-30",
        "date": "2024-11-30",
        "period": "Q2 2025",
        "document_type": "earnings_call",
        "summary": "...",
        "key_metrics": [
          "Revenue: Increase reported",
          "Tariff impact: $5-7 million for Q4"
        ],
        "strategic_highlights": [
          "Mitigation of tariff impacts",
          "Focus on operational efficiency"
        ],
        "relevance_score": 9,
        "category": "earnings"
      }
    ],
    "search_date": "2026-01-13T09:22:40.301676",
    "scrape_metadata": {
      "timestamp": "2026-01-13T09:22:40.301688",
      "search_engine": "perplexity-sonar",
      "structuring_model": "gpt-4o",
      "success": true,
      "items_found": 10,
      "themes_searched": [
        "earnings_calls",
        "financial_reports",
        "quarterly_results",
        "financial_press",
        "analyst_coverage"
      ]
    }
  }
}
```

### Types de documents

- **earnings_call** - Transcripts d'appels de résultats
- **sec_filing** - Rapports SEC (10-K, 10-Q)
- **quarterly_results** - Annonces de résultats trimestriels
- **press_release** - Communiqués de presse financiers
- **analyst_report** - Rapports d'analystes

### Catégories

- **earnings** - Résultats trimestriels/annuels
- **financial_performance** - Performance financière globale
- **guidance** - Prévisions et orientations
- **sec_filing** - Documents réglementaires
- **analyst_coverage** - Analyses et recommandations

## 🎨 Interface Frontend

### Page Financial News

Accessible via `/financial-news`, la page offre :

- **Vue d'ensemble** - Liste des items financiers de toutes les entreprises
- **Filtres multiples** :
  - Par type de document (Earnings Calls, SEC Filings, etc.)
  - Par catégorie (Earnings, Financial Performance, etc.)
  - Par entreprise (barre de recherche)
- **Pagination** - 20 items par page
- **Détails** - Modal avec informations complètes

### Composants créés

1. **FinancialNewsCard** - Carte d'affichage d'un item financier
2. **FinancialNewsDetailModal** - Modal de détails avec métriques et highlights

## 📈 Métriques collectées

Pour chaque item financier, on extrait :

- **Métriques financières** : Revenue, profit, margins, EPS, guidance
- **Highlights stratégiques** : Initiatives, investissements, challenges
- **Période** : Q1/Q2/Q3/Q4 YYYY ou FY YYYY
- **Score de pertinence** : 1-10 basé sur la profondeur des insights

## 🔄 Workflow recommandé

### Mise à jour hebdomadaire

```bash
# Tous les vendredis
cd database
./update_financial_news.sh
```

### Suivi d'une entreprise spécifique

```bash
# Après une annonce de résultats
python3 scrape_financial_news.py --company "Company Name"

# Copier manuellement les données dans public/financial_news.json
```

## 🎯 Cas d'usage Sales

### Identifier les opportunités

1. **Croissance forte** → Capacité d'investissement
2. **Expansion internationale** → Besoins de contenu visuel
3. **Initiatives digitales** → Transformation e-commerce
4. **Défis supply chain** → Optimisation time-to-market
5. **Guidance positive** → Budget disponible

### Préparer un call commercial

1. Consulter les derniers earnings calls
2. Noter les métriques clés (croissance, marges)
3. Identifier les initiatives stratégiques mentionnées
4. Adapter le pitch Presti aux priorités financières

## 🐛 Dépannage

### Erreur : No module named 'aiohttp'

```bash
cd database
source venv_async/bin/activate
pip install -r requirements.txt
```

### Erreur : PERPLEXITY_API_KEY not found

```bash
# Créer/vérifier le fichier .env
cd database
cat .env
```

### Pas de résultats pour une entreprise

Causes possibles :
- Entreprise privée (pas de données publiques)
- Nom d'entreprise incorrect
- Pas de résultats récents

Solution : Vérifier le nom officiel de l'entreprise et réessayer.

## 📚 Ressources

- **Perplexity API** : https://docs.perplexity.ai/
- **SEC Edgar** : https://www.sec.gov/edgar
- **Yahoo Finance** : https://finance.yahoo.com/

## ✅ Checklist de test

Après scraping :

- [ ] Fichier `public/financial_news.json` créé
- [ ] Au moins 5-10 items par entreprise majeure
- [ ] Données récentes (2023-2026)
- [ ] Métriques financières présentes
- [ ] URLs valides et accessibles
- [ ] Page `/financial-news` accessible
- [ ] Filtres fonctionnels
- [ ] Modal de détails s'ouvre correctement

## 🎉 Résultat

Test réussi sur **MillerKnoll** :
- ✅ 10 items financiers collectés
- ✅ Mix de earnings calls, SEC filings, quarterly results
- ✅ Métriques financières détaillées
- ✅ Strategic highlights pertinents
- ✅ URLs directes vers les documents sources

---

**Créé le** : 13 janvier 2026  
**Testé sur** : MillerKnoll  
**Status** : ✅ Opérationnel
