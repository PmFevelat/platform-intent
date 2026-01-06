# Database Scripts - Presti Intent

Scripts d'analyse des offres d'emploi pour détecter les signaux d'intention d'achat.

## Configuration

### Variables d'environnement

Créez un fichier `.env` dans le dossier `database/` avec votre clé API OpenAI :

```bash
cp .env.example .env
```

Puis éditez le fichier `.env` et ajoutez votre clé API :

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## Scripts disponibles

### Analyse complète

```bash
./run_full_analysis.py
```

Exécute l'analyse complète de tous les jobs et génère les données pour le frontend.

### Test sur une entreprise

```bash
./test_single_company.py
```

Teste l'analyse sur California Closets uniquement.

### Analyse des tendances

```bash
./analyze_trends.py
```

Analyse les tendances d'embauche sur 3 mois pour détecter les signaux d'intention.

## Notes

- Tous les scripts nécessitent la variable d'environnement `OPENAI_API_KEY`
- Les analyses utilisent GPT-4o-mini pour optimiser les coûts
- Le traitement est asynchrone avec 4-6 workers parallèles









