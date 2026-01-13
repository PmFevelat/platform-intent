# 🔄 Workflow News - Guide Visuel

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESTI NEWS SYSTEM                           │
│                                                                 │
│  Collecte → Analyse → Insights → Visualisation → Action        │
└─────────────────────────────────────────────────────────────────┘
```

## 1️⃣ Collecte des Données

```bash
┌──────────────────────┐
│  jobs_data.json      │  ← Données source
│                      │
│  - 50 entreprises    │
│  - Infos de base     │
│  - Industrie         │
│  - Site web          │
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│  Script Python       │
│  scrape_company_news │
│                      │
│  → OpenAI GPT-4o     │
│  → Analyse IA        │
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│  company_news.json   │  ← Résultats
│                      │
│  - Actualités        │
│  - Scores            │
│  - Insights          │
└──────────────────────┘
```

## 2️⃣ Commandes Disponibles

### Test (1 entreprise)
```bash
cd database
PYTHONPATH="./venv/lib/python3.13/site-packages" \
  python3 scrape_company_news.py test "abc carpet & home"
```

**Résultat:**
```
🧪 Test sur abc carpet & home...
🔍 Recherche des actualités...
✅ 5 actualités trouvées
📊 Score Presti: 8/10
```

### Scraping Complet
```bash
cd database
PYTHONPATH="./venv/lib/python3.13/site-packages" \
  python3 scrape_company_news.py
```

**Résultat:**
```
🚀 Démarrage du scraping...
📊 50 entreprises à analyser

[1/50] Traitement de 1st Dibs
✅ 7 actualités trouvées
💾 Progression sauvegardée

[2/50] Traitement de abc carpet & home
✅ 5 actualités trouvées
💾 Progression sauvegardée

...

✅ Scraping terminé!
📈 Statistiques:
   - Entreprises traitées: 50
   - Succès: 48
   - Total actualités: 387
   - Moyenne: 8.1 actualités/entreprise
```

### Déploiement Frontend
```bash
cp database/company_news.json public/news_data.json
```

**Ou tout en une commande:**
```bash
cd database
./update_news.sh full
```

## 3️⃣ Structure d'une Actualité

```json
{
  "title": "ABC Carpet & Home Launches AI-Driven Interior Design Tool",
  "source": "Furniture Today",
  "url": "https://www.furnituretoday.com/...",
  "published_date": "2024-11-15",
  "summary": "ABC Carpet & Home has introduced...",
  "relevance_score": 9,  ← Score 1-10
  "relevance_reason": "Direct opportunity for AI integration",
  "key_insights": [
    "Potential partnership for AI integration",
    "Enhancing customer experience through technology"
  ],
  "category": "ai_investment"  ← Une des 7 catégories
}
```

## 4️⃣ Catégories d'Actualités

```
🤖 ai_investment          → Investissements IA, ML, automation
🛒 ecommerce_growth       → Expansion e-commerce, marketplace
📸 visual_content         → Photos, vidéos, 3D, staging virtuel
🔄 digital_transformation → Modernisation IT, cloud, digital
👥 hiring                 → Recrutements marketing, tech, créatif
🤝 partnership            → Partenariats technologiques
💡 product_innovation     → Nouveaux produits, R&D
```

## 5️⃣ Interface Frontend

### Page Liste (/news)
```
┌──────────────────────────────────────────────────────┐
│  News                                   [═] [▦]      │
│  Actualités et insights des entreprises prospects    │
├──────────────────────────────────────────────────────┤
│  Company              │ Industry  │ Status           │
├──────────────────────────────────────────────────────┤
│  🏢 1st Dibs          │ Furniture │ 📰 À analyser   │
│  🏢 abc carpet & home │ Retail    │ 📰 À analyser   │
│  🏢 Albany Industries │ Furniture │ 📰 À analyser   │
│  ...                                                  │
└──────────────────────────────────────────────────────┘
```

### Page Entreprise (/news/[company])
```
┌────────────────────────────────────────────────────────────┐
│  ← Retour aux actualités                                   │
│                                                             │
│  🏢 abc carpet & home                                       │
│  Retail · 200-500 employees · 🌐 Website · 💼 LinkedIn    │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ ⭐ Évaluation globale                       [8/10]   │ │
│  │                                                       │ │
│  │ Presti should focus on leveraging its expertise...  │ │
│  │                                                       │ │
│  │ 📈 Opportunités:                                     │ │
│  │ • Collaboration on AI-driven visual tools            │ │
│  │ • Providing virtual staging and 3D rendering         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  [Toutes (5)] [🤖 IA (1)] [🛒 E-commerce (1)] ...        │
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐       │
│  │ AI-Driven Interior   │  │ Expands E-commerce   │       │
│  │ Design Tool          │  │ Platform              │       │
│  │                      │  │                       │       │
│  │ Furniture Today      │  │ Retail Dive           │       │
│  │ 📅 Nov 15, 2024     │  │ 📅 Oct 22, 2024      │       │
│  │                      │  │                       │       │
│  │ [🤖 AI Investment]  │  │ [🛒 E-commerce]      │       │
│  │                      │  │                       │       │
│  │ Score: [9/10]       │  │ Score: [8/10]        │       │
│  │                      │  │                       │       │
│  │ The launch of an    │  │ The expansion...      │       │
│  │ AI-driven tool...    │  │                       │       │
│  │                      │  │                       │       │
│  │ 💡 Insights:        │  │ 💡 Insights:         │       │
│  │ • Partnership for   │  │ • Virtual staging    │       │
│  │   AI integration    │  │   opportunity        │       │
│  │                      │  │                       │       │
│  │ [🔗 Lire l'article] │  │ [🔗 Lire l'article]  │       │
│  └──────────────────────┘  └──────────────────────┘       │
└────────────────────────────────────────────────────────────┘
```

## 6️⃣ Modal de Détail

```
┌─────────────────────────────────────────────────────────┐
│  ABC Carpet & Home Launches AI-Driven Tool  [Score: 9] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [🤖 AI Investment]  📅 15 novembre 2024  Furniture Today│
│                                                          │
│  📄 Résumé                                              │
│  ABC Carpet & Home has introduced a new AI-driven...    │
│                                                          │
│  ✨ Pertinence pour Presti                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ The launch of an AI-driven tool aligns with      │  │
│  │ Presti's focus on AI for visual content creation,│  │
│  │ presenting a direct opportunity for collaboration.│  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  💡 Insights clés pour l'approche commerciale           │
│  1️⃣ Potential partnership for AI integration           │
│  2️⃣ Enhancing customer experience through technology   │
│                                                          │
│  [🔗 Lire l'article complet sur Furniture Today]       │
└─────────────────────────────────────────────────────────┘
```

## 7️⃣ Workflow Utilisateur

```
1. 👤 User ouvre l'app
   │
   ├─→ Clique sur "News" dans la sidebar
   │
2. 📋 Voit la liste des entreprises
   │
   ├─→ Peut filtrer/trier
   │
   ├─→ Clique sur une entreprise
   │
3. 📰 Voit les actualités de l'entreprise
   │
   ├─→ Voit l'évaluation globale Presti
   │
   ├─→ Peut filtrer par catégorie
   │
   ├─→ Clique sur une actualité
   │
4. 🔍 Modal de détail s'ouvre
   │
   ├─→ Lit le résumé complet
   │
   ├─→ Voit les insights commerciaux
   │
   ├─→ Clique pour lire l'article source
   │
5. 🎯 Utilise les insights pour son approche commerciale
```

## 8️⃣ Cas d'Usage

### Pour un Sales
```
1. Recherche "abc carpet & home" dans News
2. Voit score Presti: 8/10 → Prospect chaud! 🔥
3. Découvre: "AI-Driven Interior Design Tool" (score 9/10)
4. Insight: "Potential partnership for AI integration"
5. Action: Prépare un pitch sur l'intégration Presti avec leur outil IA
```

### Pour un Manager
```
1. Parcourt la liste des entreprises
2. Filtre par catégorie "🤖 AI Investment"
3. Identifie les 10 entreprises avec le plus d'actualités IA
4. Priorise ces prospects pour l'équipe sales
```

### Pour un Marketing
```
1. Analyse les tendances dans les actualités
2. Identifie que 70% des prospects investissent dans l'IA
3. Adapte le messaging Presti pour mettre en avant l'IA
4. Crée du contenu ciblé sur ces thématiques
```

## 9️⃣ Métriques et KPIs

```
📊 Tableau de bord (à venir)

┌─────────────────────────────────────────────────┐
│  Total entreprises analysées:        50         │
│  Total actualités collectées:        387        │
│  Moyenne par entreprise:             8.1        │
│                                                  │
│  Score Presti moyen:                 7.2/10     │
│  Prospects hot (score ≥8):           22 (44%)   │
│  Prospects warm (score 6-7):         18 (36%)   │
│  Prospects cold (score <6):          10 (20%)   │
│                                                  │
│  Catégories les plus fréquentes:                │
│  1. 🤖 AI Investment          (32%)             │
│  2. 🛒 E-commerce Growth      (28%)             │
│  3. 🔄 Digital Transformation (18%)             │
└─────────────────────────────────────────────────┘
```

## 🎯 Prochaines Étapes

1. **Lancer le scraping complet**
   ```bash
   cd database
   ./update_news.sh full
   ```

2. **Consulter les résultats**
   - Ouvrir http://localhost:3000/news
   - Explorer les entreprises
   - Identifier les opportunités

3. **Utiliser les insights**
   - Briefer l'équipe sales
   - Prioriser les prospects chauds
   - Adapter les approches commerciales

4. **Itérer**
   - Relancer le scraping régulièrement (hebdo/mensuel)
   - Affiner les catégories si besoin
   - Ajouter de nouvelles sources d'actualités

## 💡 Tips & Tricks

### Trouver les meilleurs prospects
```
Filtrer par score Presti ≥8 + catégorie "AI Investment"
→ Ce sont vos prospects les plus chauds!
```

### Préparer un pitch
```
1. Lire les 3-5 dernières actualités de l'entreprise
2. Noter tous les insights clés
3. Identifier les pain points mentionnés
4. Adapter le pitch Presti en conséquence
```

### Suivre les tendances
```
Analyser la distribution des catégories d'actualités
→ Adapter votre stratégie marketing/produit
```

## 🎉 Vous êtes prêt !

Tout est en place pour exploiter les actualités des entreprises et convertir ces insights en opportunités commerciales ! 🚀










