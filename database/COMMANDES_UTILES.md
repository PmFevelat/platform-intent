# 🔧 Commandes Utiles - Gestion des Entreprises

## 📊 Vérifier les Statistiques

```bash
cd database

# Statistiques complètes
python3 -c "
import json

with open('jobs_data.json', 'r') as f:
    jobs = json.load(f)
    print(f'📊 jobs_data.json: {jobs[\"total_companies\"]} entreprises')

with open('company_news.json', 'r') as f:
    news = json.load(f)
    total_news = sum(len(company.get('news_items', [])) for company in news.values())
    successful = sum(1 for company in news.values() if company.get('scrape_metadata', {}).get('success'))
    print(f'📰 company_news.json: {len(news)} entreprises')
    print(f'   ✅ Succès: {successful}')
    print(f'   📰 Total actualités: {total_news}')
    print(f'   📈 Moyenne: {total_news/len(news):.1f} actualités/entreprise')
"
```

## 🔍 Rechercher une Entreprise Spécifique

```bash
cd database

# Voir les actualités d'une entreprise
python3 -c "
import json
import sys

company_name = 'Pottery Barn'  # Changer le nom ici

with open('company_news.json', 'r') as f:
    news = json.load(f)
    
if company_name in news:
    company = news[company_name]
    print(f'🏢 {company_name}')
    print(f'   Score Presti: {company.get(\"overall_assessment\", {}).get(\"presti_fit_score\")}/10')
    print(f'   Actualités: {len(company.get(\"news_items\", []))}')
    print()
    for item in company.get('news_items', []):
        print(f'   • {item[\"title\"]} ({item[\"relevance_score\"]}/10)')
else:
    print(f'❌ {company_name} non trouvé')
"
```

## 📥 Mettre à Jour les Actualités (avec API OpenAI)

```bash
cd database

# Activer l'environnement virtuel
source venv_async/bin/activate

# Option 1: Tester une seule entreprise
OPENAI_API_KEY=your_key python3 scrape_company_news_async.py test "Company Name"

# Option 2: Scraper toutes les entreprises
OPENAI_API_KEY=your_key python3 scrape_company_news_async.py

# Déployer vers le frontend
cp company_news.json ../public/news_data.json
```

## ➕ Ajouter de Nouvelles Entreprises

### Méthode 1: Sans API (données manuelles)

```bash
cd database

# 1. Modifier generate_new_companies_data.py
# Ajouter les entreprises dans NEW_COMPANIES_DATA

# 2. Exécuter
python3 generate_new_companies_data.py

# 3. Mettre à jour jobs_data.json manuellement ou créer un script

# 4. Déployer vers le frontend
cp company_news.json ../public/news_data.json
```

### Méthode 2: Avec API OpenAI (recommandé)

```bash
cd database

# 1. Ajouter entreprises à jobs_data.json
# Créer un script add_companies.py:
cat > add_companies.py << 'EOF'
import json

with open('jobs_data.json', 'r') as f:
    data = json.load(f)

new_companies = [
    {
        "success": True,
        "jobs": [],
        "nb_jobs": 0,
        "company": {
            "name": "New Company",
            "website": "https://...",
            "industry": "Furniture",
            "employees": "500-1000"
        }
    }
]

data['companies'].extend(new_companies)
data['total_companies'] = len(data['companies'])

with open('jobs_data.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ {len(new_companies)} entreprises ajoutées")
EOF

python3 add_companies.py

# 2. Scraper les actualités
source venv_async/bin/activate
OPENAI_API_KEY=your_key python3 scrape_company_news_async.py

# 3. Déployer
cp company_news.json ../public/news_data.json
```

## 🔄 Workflow Complet de Mise à Jour

```bash
cd database

# 1. Activer l'environnement
source venv_async/bin/activate

# 2. Mettre à jour les actualités
OPENAI_API_KEY=your_key python3 scrape_company_news_async.py

# 3. Déployer vers le frontend
cp company_news.json ../public/news_data.json

# 4. Vérifier
python3 -c "
import json
with open('../public/news_data.json', 'r') as f:
    data = json.load(f)
    print(f'✅ {len(data)} entreprises disponibles dans le frontend')
"

# 5. Redémarrer l'app (si nécessaire)
# L'app Next.js détecte automatiquement les changements
```

## 📤 Exporter les Données

```bash
cd database

# Export CSV des scores Presti
python3 -c "
import json
import csv

with open('company_news.json', 'r') as f:
    news = json.load(f)

with open('presti_scores.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Entreprise', 'Score Presti', 'Nb Actualités', 'Opportunités'])
    
    for company_name, data in sorted(news.items()):
        score = data.get('overall_assessment', {}).get('presti_fit_score', 0)
        nb_news = len(data.get('news_items', []))
        opps = '; '.join(data.get('overall_assessment', {}).get('key_opportunities', []))
        writer.writerow([company_name, score, nb_news, opps])

print('✅ Export créé: presti_scores.csv')
"
```

## 🔍 Filtrer par Score

```bash
cd database

# Entreprises avec score >= 8
python3 -c "
import json

with open('company_news.json', 'r') as f:
    news = json.load(f)

high_scores = {
    name: data for name, data in news.items()
    if data.get('overall_assessment', {}).get('presti_fit_score', 0) >= 8
}

print(f'🎯 {len(high_scores)} entreprises avec score >= 8:')
for name, data in sorted(high_scores.items(), 
                         key=lambda x: x[1].get('overall_assessment', {}).get('presti_fit_score', 0),
                         reverse=True):
    score = data.get('overall_assessment', {}).get('presti_fit_score')
    print(f'   {score}/10 - {name}')
"
```

## 🧹 Nettoyage

```bash
cd database

# Supprimer les fichiers temporaires
rm -f *_test.json
rm -f presti_scores.csv

# Sauvegarder avant nettoyage complet
cp company_news.json company_news_backup.json
cp jobs_data.json jobs_data_backup.json
```

## 📋 Checklist Ajout Entreprise

- [ ] Ajouter à `database/jobs_data.json`
- [ ] Générer/Scraper actualités vers `database/company_news.json`
- [ ] Copier vers `public/news_data.json`
- [ ] Ajouter à `public/data.json` si nécessaire
- [ ] Vérifier affichage dans l'interface web
- [ ] Documenter dans CHANGEMENTS_EFFECTUES.md

## 🆘 Dépannage

### Les actualités n'apparaissent pas

```bash
# Vérifier que news_data.json existe
ls -lh public/news_data.json

# Vérifier le contenu
python3 -c "
import json
with open('public/news_data.json', 'r') as f:
    data = json.load(f)
    print(f'{len(data)} entreprises')
"

# Recopier depuis database
cp database/company_news.json public/news_data.json
```

### Entreprise manquante

```bash
# Vérifier dans tous les fichiers
python3 -c "
import json

company = 'Pottery Barn'  # Nom à chercher

print(f'Recherche de: {company}')

# jobs_data.json
with open('database/jobs_data.json', 'r') as f:
    jobs = json.load(f)
    found = any(c.get('company', {}).get('name') == company for c in jobs['companies'])
    print(f'  jobs_data.json: {\"✅\" if found else \"❌\"}')

# company_news.json
with open('database/company_news.json', 'r') as f:
    news = json.load(f)
    found = company in news
    print(f'  company_news.json: {\"✅\" if found else \"❌\"}')

# public/data.json
with open('public/data.json', 'r') as f:
    data = json.load(f)
    found = company.lower() in data.get('companies', {})
    print(f'  public/data.json: {\"✅\" if found else \"❌\"}')

# public/news_data.json
with open('public/news_data.json', 'r') as f:
    news_front = json.load(f)
    found = company in news_front
    print(f'  public/news_data.json: {\"✅\" if found else \"❌\"}')
"
```

## 🚀 Scripts Utiles Conservés

- `database/generate_new_companies_data.py` - Générer données manuelles
- `database/scrape_company_news_async.py` - Scraper avec OpenAI
- `database/update_news.sh` - Workflow complet actualités

## 📚 Documentation

- `NOUVELLES_ENTREPRISES.md` - Documentation ajout 8 entreprises
- `NOUVELLES_ENTREPRISES_RESUME.md` - Résumé exécutif
- `README_NEWS.md` - Documentation système actualités
- `CHANGEMENTS_EFFECTUES.md` - Historique des modifications



