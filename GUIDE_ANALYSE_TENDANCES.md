# 🎯 Guide d'Analyse des Tendances - Presti.ai

## Vue d'ensemble

Nous avons complètement repensé l'analyse des offres d'emploi pour **détecter des signaux d'intention d'achat** plutôt que d'analyser chaque job individuellement.

### Ce qui a changé

#### ✅ Ce qui reste inchangé
- **Tech Stack** : L'analyse et l'affichage restent identiques
- **Liste des jobs** : L'affichage classique dans l'onglet "Jobs"

#### 🔄 Ce qui a changé
- **"Value Proposition" → "Trends"** : Nouveau nom et nouvelle approche
- **Analyse collective** : On analyse tous les jobs d'une entreprise sur 3 mois ensemble
- **Détection de tendances** : Focus sur les évolutions, nouvelles apparitions, vélocité

## 🎓 Concept

### Contexte Presti.ai
- **Solution** : Génération automatique de mises en scène photoréalistiques pour meubles & décoration
- **Cibles** : Grandes entreprises (Enterprises)
- **Personas** : Marketing/Brand, E-commerce/Digital, Creative/Content/Design, Retail/Merchandising

### Objectif
Détecter des **initiatives business** en cours ou imminentes à partir des tendances de recrutement :
- Refonte / expansion du site e-commerce
- Accélération du marketing digital
- Lancement de nouveaux produits ou collections
- Industrialisation de la production de visuels
- Structuration d'une équipe créative / contenu

## 📊 Les 3 Catégories de Tendances

### A. Digital & E-commerce Acceleration
**Signaux recherchés :**
- Augmentation du volume de jobs e-commerce, web, CRO, content
- Mentions de refonte de site, scaling, internationalisation
- Transformation digitale, croissance e-commerce

**Exemple de signal :**
> L'entreprise recrute 4 rôles e-commerce manager et 2 digital marketing leads en 6 semaines
> → Probable expansion e-commerce nécessitant plus de visuels produits

### B. Visual Content & Creative Production
**Signaux recherchés :**
- Rôles liés à la création de visuels, content, design, brand
- Mentions de photos, visuals, assets, catalogs, product pages
- Production de contenu à l'échelle

**Exemple de signal :**
> Apparition soudaine de "content creator", "brand photographer", "visual merchandiser"
> → Probable industrialisation de la production de contenu visuel

### C. Product Launch & Merchandising
**Signaux recherchés :**
- Rôles liés au product marketing, merchandising, collections
- Vocabulaire autour de "new collections", "product launches"
- Campagnes saisonnières

**Exemple de signal :**
> 3 postes "Product Marketing Manager" mentionnant "new collection launch"
> → Lancement imminent nécessitant des visuels pour toute la collection

## 🚀 Utilisation Pratique

### Étape 1 : Collecte des données (existant)
```bash
cd database
source venv/bin/activate
# Script de collecte via API Mantiks (existant)
# Génère : jobs_data.json
```

### Étape 2 : Analyse des tendances (NOUVEAU)
```bash
python analyze_trends.py
```

**Ce que fait ce script :**
1. Lit tous les jobs de `jobs_data.json`
2. Regroupe les jobs par entreprise
3. Envoie à GPT-4 une analyse collective pour chaque entreprise
4. Génère `jobs_trends_analysis.json`

**Résultat :** Pour chaque entreprise, on obtient :
- Score de signal global (1-10)
- Analyse par catégorie (A, B, C)
- Évolutions détectées
- Nouveaux thèmes
- Vélocité d'embauche
- Initiatives business identifiées
- Recommandation d'approche commerciale

### Étape 3 : Conversion pour le frontend (NOUVEAU)
```bash
python convert_trends_to_frontend.py
```

**Ce que fait ce script :**
1. Fusionne `jobs_data.json` + `jobs_trends_analysis.json`
2. Génère `../public/data.json` au bon format pour le frontend
3. Préserve les jobs individuels pour l'onglet "Jobs"
4. Ajoute les analyses de tendances

### Étape 4 : Visualisation
Ouvrez l'application web et explorez l'onglet **"Trends"** pour chaque entreprise.

## 🎨 Interface "Trends"

### Synthèse globale
- **Score de signal** : 1-10 (Faible / Moyen / Fort)
- **Résumé** : 2-3 phrases sur les principaux signaux
- **Période d'analyse** : Dates de début/fin + nombre de jobs

### Cartes de catégories
Pour chaque catégorie (Digital, Visual, Product) :
- **Vélocité** : 🐌 Lente / 🚶 Modérée / 🏃 Rapide / 🚀 En accélération
- **Rôles clés** : Liste des titres de postes pertinents
- **Évolution** : Description des changements sur 3 mois
- **Nouveaux thèmes** : Sujets émergents
- **Preuves** : Citations des offres d'emploi
- **Pertinence Presti** : Pourquoi c'est important pour nous

### Initiatives business détectées
- **Nom de l'initiative** : Ex. "Refonte du site e-commerce"
- **Confiance** : Faible / Moyenne / Élevée
- **Preuves** : Citations supportant cette hypothèse
- **Catégories impliquées** : Quelles tendances convergent

### Approche recommandée
Suggestion d'approche commerciale basée sur les tendances détectées.

## 💡 Exemples de Détection

### Exemple 1 : Signal Fort
**Entreprise :** Ashley Furniture

**Tendances détectées :**
- Digital & E-commerce : 8/10 (5 jobs, vélocité "accélération")
  - Évolution : "Forte augmentation des rôles e-commerce"
  - Nouveaux thèmes : "Internationalisation", "Mobile-first"
  
- Visual Content : 9/10 (4 jobs, vélocité "rapide")
  - Évolution : "Création d'une équipe dédiée au contenu visuel"
  - Nouveaux thèmes : "Product photography at scale", "Brand consistency"

**Initiative détectée :**
- "Refonte complète de l'expérience e-commerce" (Confiance : Élevée)
- Preuves : Multiple mentions de "site redesign", "UX improvement", "catalog expansion"

**Signal global :** 9/10 → **Compte hautement prioritaire**

**Approche recommandée :**
> "Ashley est en pleine transformation e-commerce avec un fort focus sur le contenu visuel. 
> Approcher le Head of E-commerce et le Creative Director avec un cas d'usage sur la production 
> de visuels à l'échelle pour leur catalogue en expansion."

### Exemple 2 : Signal Modéré
**Entreprise :** West Elm

**Tendances détectées :**
- Product Launch : 6/10 (3 jobs, vélocité "modérée")
  - Évolution : "Augmentation des rôles merchandising"
  - Nouveaux thèmes : "Seasonal collections"

**Signal global :** 5/10 → **Compte à monitorer**

## 🎯 Priorisation des Comptes

### Score ≥ 7/10 : 🔴 Priorité Haute
→ Signaux forts, contacter immédiatement

### Score 4-6/10 : 🟡 Priorité Moyenne
→ Signaux intéressants, à surveiller

### Score ≤ 3/10 : ⚪ Priorité Basse
→ Peu de signaux actuellement

## 📈 Workflow Complet

```
1. API Mantiks
   ↓
2. jobs_data.json (données brutes)
   ↓
3. analyze_trends.py
   ↓
4. jobs_trends_analysis.json (analyses)
   ↓
5. convert_trends_to_frontend.py
   ↓
6. public/data.json (frontend)
   ↓
7. Interface web → Onglet "Trends"
```

## 🔧 Configuration

### Variables importantes dans `analyze_trends.py`
```python
OPENAI_API_KEY = "..."  # Votre clé API OpenAI
NUM_WORKERS = 4         # Nombre de requêtes parallèles
OUTPUT_FILE = "jobs_trends_analysis.json"
```

### Coûts estimés
- Modèle : GPT-4o-mini
- Prix : ~$0.15 par million de tokens
- Estimation : ~$0.50-2.00 pour 50 entreprises

## ⚠️ Notes importantes

1. **Minimum de jobs requis** : L'analyse est plus pertinente avec au moins 2-3 jobs par entreprise
2. **Période de 3 mois** : Les jobs doivent être récents pour détecter des tendances actuelles
3. **Sauvegarde incrémentale** : Le script sauvegarde tous les 2 analyses pour éviter les pertes
4. **Reprise automatique** : Si le script s'arrête, il reprend là où il s'est arrêté

## 🆘 Dépannage

### Problème : Aucune analyse de tendances affichée
**Solution :** Vérifiez que :
1. `jobs_trends_analysis.json` existe et contient des données
2. `convert_trends_to_frontend.py` a été exécuté
3. `public/data.json` contient le champ `trends_analysis`

### Problème : Erreur OpenAI rate limit
**Solution :** Réduire `NUM_WORKERS` de 4 à 2 dans `analyze_trends.py`

### Problème : Script Python ne trouve pas les modules
**Solution :**
```bash
cd database
source venv/bin/activate
pip install -r requirements.txt  # Si ce fichier existe
# Ou installer manuellement :
pip install openai
```

## 🚀 Prochaines améliorations possibles

1. **Timeline visuelle** : Graphique montrant l'évolution temporelle des recrutements
2. **Comparaison inter-entreprises** : Benchmarking des tendances du marché
3. **Alertes automatiques** : Notifications sur les signaux forts émergents
4. **Export PDF** : Génération de rapports pour les commerciaux
5. **Filtres avancés** : Par industrie, taille d'entreprise, signal strength

## 📞 Support

Pour toute question sur cette nouvelle méthode d'analyse, référez-vous aux fichiers :
- `database/README_TRENDS.md` : Documentation technique
- `database/analyze_trends.py` : Code source avec commentaires
- `src/components/company/TrendsTab.tsx` : Interface utilisateur

---

**Bon prospecting ! 🎯**

