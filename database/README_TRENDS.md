# Analyse des Tendances - Nouvelle Méthode

## 🎯 Objectif

Cette nouvelle approche d'analyse permet de détecter des **signaux d'intention d'achat** en analysant les tendances de recrutement sur 3 mois, plutôt que d'analyser chaque offre d'emploi individuellement.

L'objectif est d'identifier des initiatives business en cours ou imminentes chez les comptes cibles (manufacturers et retailers de meubles & produits de décoration).

## 📊 Catégories de Tendances

L'analyse se concentre sur 3 catégories majeures :

### A. Digital & E-commerce Acceleration
Détecte les signaux d'expansion digitale :
- Augmentation des recrutements e-commerce, web, CRO, content
- Mentions de refonte de site, scaling, internationalisation
- Transformation digitale

### B. Visual Content & Creative Production
Identifie les besoins en production de contenu visuel :
- Rôles liés à la création de visuels, content, design, brand
- Mentions de photos, visuals, assets, catalogs, product pages
- Production de contenu à l'échelle

### C. Product Launch & Merchandising
Repère les lancements de produits :
- Rôles liés au product marketing, merchandising, collections
- Vocabulaire autour de "new collections", "product launches"
- Campagnes saisonnières

## 🔍 Ce qui est détecté

Pour chaque catégorie, l'analyse identifie :

1. **Évolution** : augmentation/diminution du volume de jobs, changements de focus
2. **Nouveaux thèmes** : apparition de nouveaux sujets
3. **Vélocité d'embauche** : lente / modérée / rapide / en accélération
4. **Initiatives business** : projets détectés avec niveau de confiance

## 🚀 Utilisation

### 1. Analyse des tendances

```bash
cd database
source venv/bin/activate
python analyze_trends.py
```

Ce script :
- Lit `jobs_data.json` (données brutes des jobs)
- Agrège tous les jobs par entreprise
- Analyse les tendances sur 3 mois avec GPT-4
- Génère `jobs_trends_analysis.json`

### 2. Conversion pour le frontend

```bash
python convert_trends_to_frontend.py
```

Ce script :
- Lit `jobs_data.json` et `jobs_trends_analysis.json`
- Fusionne les données
- Génère `../public/data.json` pour le frontend

### 3. Visualisation

Ouvrez l'interface web et naviguez vers l'onglet **"Trends"** pour chaque entreprise.

## 📁 Structure des fichiers

```
database/
├── analyze_trends.py           # Nouveau script d'analyse des tendances
├── convert_trends_to_frontend.py  # Conversion vers format frontend
├── jobs_data.json              # Données brutes (inchangé)
├── jobs_trends_analysis.json   # Résultats d'analyse (généré)
└── README_TRENDS.md           # Ce fichier

public/
└── data.json                   # Données pour le frontend (généré)
```

## 🔄 Workflow complet

1. **Collecte des jobs** (existant) : `jobs_data.json` via API Mantiks
2. **Analyse des tendances** (nouveau) : `analyze_trends.py` → `jobs_trends_analysis.json`
3. **Conversion frontend** (nouveau) : `convert_trends_to_frontend.py` → `public/data.json`
4. **Visualisation** : Interface web, onglet "Trends"

## 💡 Exemples de signaux détectés

- **Signal fort** : Entreprise recrute 5 rôles e-commerce + 3 rôles content en 2 mois
  → Probable refonte du site et augmentation de la production de visuels
  
- **Initiative détectée** : "Expansion internationale" (confiance élevée)
  → Multiple mentions de "international", "EMEA", "localization" dans les jobs

- **Nouvelle tendance** : Apparition soudaine de termes "UGC", "product videos", "lifestyle imagery"
  → Nouveau focus sur le contenu lifestyle

## 🎨 Interface utilisateur

L'onglet **"Trends"** remplace l'ancien onglet "Value Proposition" et affiche :

- Synthèse globale avec score de signal (1-10)
- 3 cartes de catégories avec détails (rôles clés, évolution, nouveaux thèmes)
- Initiatives business détectées avec niveau de confiance
- Approche commerciale recommandée

## ⚠️ Important

- L'ancien système d'analyse job-par-job reste disponible mais n'est plus utilisé dans l'interface
- La Tech Stack continue d'être analysée job-par-job (inchangé)
- Les fichiers `analyze_jobs_v2.py` et `analyze_jobs_openai.py` restent pour référence

## 🔮 Prochaines étapes possibles

- Ajouter une visualisation temporelle (timeline des recrutements)
- Détecter des patterns cross-entreprises (tendances du marché)
- Scoring automatique de priorisation des comptes
- Alertes sur les signaux forts émergents

