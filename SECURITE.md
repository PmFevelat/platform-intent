# 🔐 Sécurité - Configuration des clés API

## Configuration requise

Ce projet utilise plusieurs API qui nécessitent des clés d'authentification :
- **OpenAI API** : Pour les analyses et le scraping
- **Perplexity API** : Pour la recherche d'actualités
- **Mantiks API** : Pour l'enrichissement des offres d'emploi

## Installation

### 1. Créer le fichier .env

Copiez le fichier d'exemple et remplissez vos clés :

```bash
cd database
cp .env.example .env
```

### 2. Ajouter vos clés API dans database/.env

Éditez le fichier `database/.env` et ajoutez vos vraies clés :

```bash
PERPLEXITY_API_KEY=votre_clé_perplexity
OPENAI_API_KEY=votre_clé_openai
MANTIKS_API_KEY=votre_clé_mantiks
```

### 3. Installer python-dotenv

```bash
cd database
source venv/bin/activate  # ou venv_async/bin/activate
pip install -r requirements.txt
```

## ⚠️ IMPORTANT - Sécurité

- ❌ **Ne JAMAIS commiter le fichier `.env`** dans Git
- ✅ Le fichier `.env` est déjà dans `.gitignore`
- ✅ Utilisez `.env.example` pour documenter les variables nécessaires
- ✅ Partagez uniquement `.env.example`, jamais `.env`

## Vérification

Avant de faire un push Git, vérifiez que vos clés ne sont pas exposées :

```bash
# Vérifier qu'aucune clé n'est dans le code
git diff

# Vérifier que .env est ignoré
git status
# .env ne doit PAS apparaître dans les fichiers à commiter
```

## Scripts modifiés

Tous les scripts Python chargent automatiquement les variables depuis `.env` :
- `scrape_news_multi.py`
- `scrape_company_news_async.py`
- `scrape_news_hybrid.py`
- `scrape_company_news_hybrid_async.py`
- `scrape_company_news.py`
- `scrape_management_interviews.py`
- `enrich_jobs.py`
- `analyze_jobs_v2.py`
- `analyze_trends.py`
- `analyze_jobs_detailed.py`
- `analyze_jobs_openai.py`

## Utilisation

Les scripts chargent automatiquement les variables d'environnement. Vous n'avez plus besoin de les passer en ligne de commande :

```bash
# Avant (ancien)
OPENAI_API_KEY=xxx python3 scrape_company_news_async.py

# Maintenant (nouveau) - plus simple et sécurisé
python3 scrape_company_news_async.py
```

## En cas de fuite de clé

Si vous avez accidentellement commité une clé API :

1. **Révoquez immédiatement la clé** sur la plateforme concernée
2. **Générez une nouvelle clé**
3. **Mettez à jour votre fichier `.env`**
4. **Ne tentez pas de supprimer l'historique Git** - contactez l'équipe de sécurité

## Support

Pour toute question sur la sécurité, contactez l'administrateur du projet.


