# Module de Scraping des Actualités d'Entreprises

Ce module utilise l'API OpenAI avec la fonctionnalité Web Search pour récupérer automatiquement les actualités pertinentes des entreprises prospects.

## 🎯 Objectif

Collecter et analyser les actualités récentes des entreprises pour évaluer la pertinence du produit Presti (solution d'IA pour la création de contenu visuel) en détectant :

- 🤖 Investissements dans l'IA et la transformation digitale
- 🛒 Expansion e-commerce et nouveaux canaux de vente
- 📸 Initiatives de contenu visuel, photographie, catalogue produit
- 📈 Croissance, nouveaux marchés, expansion internationale
- 👥 Recrutements dans le marketing digital, e-commerce, créatif
- 🤝 Partenariats technologiques
- 💡 Innovations produit nécessitant du contenu visuel

## 📋 Prérequis

```bash
# Installer les dépendances Python
cd database
pip install -r requirements.txt
```

## 🔑 Configuration

La clé API OpenAI doit être configurée via une variable d'environnement :
```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

Ou créez un fichier `.env` dans le dossier `database/` :
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

Vous pouvez aussi la définir comme variable d'environnement :
```bash
export OPENAI_API_KEY="votre-clé-api"
```

## 🚀 Utilisation

### Test sur une seule entreprise

Pour tester le script sur une entreprise spécifique :

```bash
cd database
python scrape_company_news.py test "California Closets"
```

Résultat : `company_news_test.json`

### Traiter toutes les entreprises

Pour récupérer les actualités de toutes les entreprises du fichier `jobs_data.json` :

```bash
cd database
python scrape_company_news.py
```

Résultat : `company_news.json`

Le script :
- ✅ Sauvegarde la progression de manière incrémentale
- ✅ Skip les entreprises déjà traitées avec succès
- ✅ Peut être interrompu et repris à tout moment

## 📊 Structure des Données

### Format d'entrée (`jobs_data.json`)

```json
{
  "companies": {
    "Nom Entreprise": {
      "name": "Nom Entreprise",
      "website": "https://...",
      "industry": "Retail",
      "employees": "1000-5000",
      "jobs": [...]
    }
  }
}
```

### Format de sortie (`company_news.json`)

```json
{
  "Nom Entreprise": {
    "company_name": "Nom Entreprise",
    "search_date": "2025-01-02",
    "news_items": [
      {
        "title": "Titre de l'actualité",
        "source": "TechCrunch",
        "url": "https://...",
        "published_date": "2024-12-15",
        "summary": "Résumé de l'article...",
        "relevance_score": 8,
        "relevance_reason": "Pourquoi c'est pertinent pour Presti",
        "key_insights": [
          "Insight 1 pour l'approche commerciale",
          "Insight 2..."
        ],
        "category": "ai_investment"
      }
    ],
    "overall_assessment": {
      "presti_fit_score": 8,
      "key_opportunities": [
        "Opportunité 1",
        "Opportunité 2"
      ],
      "recommended_approach": "Recommandation pour l'approche commerciale"
    },
    "scrape_metadata": {
      "timestamp": "2025-01-02T10:30:00",
      "model": "gpt-4o",
      "success": true
    }
  }
}
```

## 📂 Intégration Frontend

Une fois les actualités collectées, il faut copier le fichier JSON dans le dossier public :

```bash
cp database/company_news.json public/news_data.json
```

Le frontend chargera automatiquement les données depuis `/news_data.json`.

## 🎨 Pages Frontend

### Liste des entreprises
- **URL** : `/news`
- **Description** : Vue d'ensemble de toutes les entreprises avec accès aux actualités

### Actualités d'une entreprise
- **URL** : `/news/[company]`
- **Description** : Affichage des actualités spécifiques à une entreprise
- **Fonctionnalités** :
  - Filtrage par catégorie
  - Score de pertinence pour Presti
  - Évaluation globale et opportunités
  - Cards cliquables avec modal détaillé
  - Liens vers les articles sources

## 🏷️ Catégories d'Actualités

- **digital_transformation** : Transformation Digitale
- **ecommerce_growth** : Croissance E-commerce
- **visual_content** : Contenu Visuel
- **ai_investment** : Investissement IA
- **hiring** : Recrutement
- **partnership** : Partenariat
- **product_innovation** : Innovation Produit

## 🔄 Workflow Complet

1. **Collecter les actualités** :
   ```bash
   cd database
   python scrape_company_news.py
   ```

2. **Copier les données vers le frontend** :
   ```bash
   cp database/company_news.json public/news_data.json
   ```

3. **Accéder aux actualités** :
   - Ouvrir l'application web
   - Naviguer vers l'onglet "News" dans la sidebar
   - Sélectionner une entreprise
   - Explorer les actualités et insights

## ⚙️ Fonctionnalité OpenAI Web Search

✅ Le script utilise la **vraie fonctionnalité Web Search d'OpenAI** via la Responses API qui permet de :

- 🔍 Effectuer des recherches web **en temps réel**
- 📰 Accéder aux actualités **récentes et vérifiées** (pas limitées aux données d'entraînement)
- 🎯 Trouver des sources **authentiques** (blogs d'entreprise, LinkedIn, presse)
- 🧠 Analyser et structurer automatiquement les résultats
- 🔗 Fournir des URLs et citations **réelles**

Configuration dans le code :
```python
response = client.responses.create(
    model="gpt-4o",
    tools=[{
        "type": "web_search",
        "external_web_access": True  # Active l'accès web en temps réel
    }],
    input=prompt,
    temperature=0.3,
)
```

**Documentation officielle :** https://platform.openai.com/docs/guides/tools-web-search

## 📈 Exemple de Statistiques

```
📈 Statistiques:
   - Entreprises traitées: 45
   - Succès: 43
   - Total actualités: 387
   - Moyenne par entreprise: 8.6
```

## 🐛 Gestion des Erreurs

Le script gère automatiquement :
- ❌ Erreurs d'API (sauvegarde du message d'erreur)
- ⏸️ Interruptions (reprise possible)
- 🔄 Retry automatique sur les entreprises échouées
- 📝 Logs détaillés de chaque étape

## 💡 Conseils

1. **Test d'abord** : Toujours tester sur une entreprise avant de lancer le traitement complet
2. **Surveillance** : Surveiller les premières entreprises pour valider la qualité des résultats
3. **Quotas API** : Être conscient des limites de l'API OpenAI (rate limits)
4. **Mise à jour** : Relancer régulièrement pour obtenir les actualités les plus récentes

## 📞 Support

Pour toute question ou problème :
- Vérifier les logs de la console
- Consulter le fichier `company_news.json` pour voir les erreurs
- Valider la clé API OpenAI

