# Interface Temporaire - Entreprises Pet Care

## Vue d'ensemble

Cette interface temporaire a été créée pour gérer l'ajout et le scraping de 4 nouvelles entreprises du secteur des animaux de compagnie :

- **Chewy** - https://www.chewy.com/
- **Petco** - https://www.petco.com/shop/en/petcostore
- **Petmate** - https://www.petmate.com/
- **Petsmart** - https://www.petsmart.com/

## Fonctionnalités

### 1. Interface Web
- **URL** : `/temp-companies`
- **Navigation** : Accessible via la sidebar "Pet Care (Temp)"
- **Fonctionnalités** :
  - Table des entreprises avec statuts en temps réel
  - Boutons d'action pour chaque script
  - Suivi des statuts (en attente, en cours, terminé, erreur)

### 2. Scripts Disponibles

#### Ajout à la base de données
- **Script** : `database/add_pet_care_companies.py`
- **Fonction** : Ajoute les entreprises au fichier `TAM.csv`
- **Sauvegarde** : Crée automatiquement une sauvegarde avant modification

#### Scripts de scraping
1. **Company News** : `scrape_company_news_async.py`
2. **Management Interviews** : `scrape_management_interviews.py`
3. **Job Offers** : `analyze_jobs_detailed.py`
4. **Financial News** : `scrape_financial_news_async.py`

### 3. API Endpoint
- **URL** : `/api/temp-scraping`
- **Méthode** : POST
- **Payload** :
```json
{
  "company": "Chewy",
  "website": "https://www.chewy.com/",
  "scriptType": "companyNews"
}
```

## Utilisation

### Étape 1 : Ajouter à la base de données
1. Cliquer sur le bouton "Ajouter à la DB"
2. Le script `add_pet_care_companies.py` s'exécute
3. Les entreprises sont ajoutées au fichier `TAM.csv`

### Étape 2 : Lancer les scripts de scraping
1. **Option A** : Lancer un script individuel
   - Cliquer sur le bouton ▶️ à côté du script désiré
2. **Option B** : Lancer tous les scripts d'une entreprise
   - Cliquer sur "Tout lancer" pour l'entreprise
3. **Option C** : Lancer tout le scraping
   - Cliquer sur "Lancer tout le scraping" (toutes entreprises, tous scripts)

## Structure des fichiers

```
src/
├── app/
│   ├── temp-companies/
│   │   └── page.tsx                    # Interface principale
│   └── api/
│       └── temp-scraping/
│           └── route.ts                # API endpoint
└── components/
    └── Sidebar.tsx                     # Navigation mise à jour

database/
└── add_pet_care_companies.py          # Script d'ajout à la DB
```

## Statuts des scripts

- 🟡 **En attente** : Script pas encore lancé
- 🔵 **En cours** : Script en cours d'exécution
- 🟢 **Terminé** : Script exécuté avec succès
- 🔴 **Erreur** : Erreur lors de l'exécution

## Données des entreprises

| Entreprise | Site Web | Secteur | Employés |
|------------|----------|---------|----------|
| Chewy | https://www.chewy.com/ | Pet Supplies E-commerce | 10,000+ |
| Petco | https://www.petco.com/shop/en/petcostore | Pet Retail | 25,000+ |
| Petmate | https://www.petmate.com/ | Pet Products Manufacturing | 500-1000 |
| Petsmart | https://www.petsmart.com/ | Pet Retail | 50,000+ |

## Notes techniques

- Les scripts s'exécutent en arrière-plan via `spawn`
- Les statuts sont mis à jour en temps réel dans l'interface
- Une sauvegarde automatique est créée avant modification de `TAM.csv`
- L'interface est responsive et optimisée pour tous les écrans

## Suppression

Cette interface est temporaire et peut être supprimée après traitement des entreprises :

1. Supprimer `/src/app/temp-companies/`
2. Supprimer `/src/app/api/temp-scraping/`
3. Retirer l'entrée "Pet Care (Temp)" de `Sidebar.tsx`
4. Supprimer `database/add_pet_care_companies.py`
5. Supprimer ce fichier README