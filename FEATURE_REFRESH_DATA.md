# 🔄 Feature: Refresh Data (Re-scraping à la demande)

## Vue d'ensemble

Cette fonctionnalité permet aux utilisateurs de **relancer le scraping web** pour obtenir les informations les plus récentes sur une entreprise, directement depuis l'interface utilisateur.

## 🎯 Objectif

Permettre aux utilisateurs de vérifier s'il existe de nouvelles actualités ou interviews récentes sans avoir à attendre une mise à jour globale de la base de données.

## 📍 Localisation

Le bouton **"Refresh Data"** est disponible dans :
- **Tab "Company News"** - pour rescraper les actualités de l'entreprise
- **Tab "Management Interviews"** - pour rescraper les interviews du management

## 🎨 Interface Utilisateur

### Bouton Principal
- **Label**: "Refresh Data"
- **Icon**: 🔄 RefreshCw
- **Position**: En haut à droite, à côté des filtres de date et catégorie
- **Style**: Bouton outline, compact (size: sm, text: xs)

### Modal de Sélection
Au clic sur "Refresh Data", une modal s'ouvre avec :

**Titre**: "Refresh Company News" ou "Refresh Management Interviews"
**Description**: Explique que le système va scanner le web pour du contenu récent

**Options de période** (filtres granulaires) :
1. **Last 7 days** - Recherche sur la dernière semaine
2. **Last 30 days** - Recherche sur le dernier mois
3. **Last 3 months** - Recherche sur les 3 derniers mois
4. **Last 6 months** - Recherche sur les 6 derniers mois

### États du Bouton
- **Idle**: Bouton cliquable avec icône statique
- **Loading**: Icône qui tourne + message "Searching the web for recent content... This may take 30-60 seconds."
- **Error**: Message d'erreur en rouge si le scraping échoue
- **Success**: Fermeture de la modal + rechargement de la page avec les nouvelles données

## 🔧 Architecture Technique

### Frontend

#### 1. Composant RefreshDataButton
**Fichier**: `src/components/company/RefreshDataButton.tsx`

**Props**:
```typescript
interface RefreshDataButtonProps {
  companyName: string;           // Nom de l'entreprise
  dataType: "news" | "interviews"; // Type de données à rafraîchir
  onRefreshComplete?: () => void;  // Callback optionnel
}
```

**États**:
- `isOpen`: Boolean - Contrôle l'ouverture de la modal
- `isRefreshing`: Boolean - Indique si un scraping est en cours
- `selectedPeriod`: String | null - Période sélectionnée
- `error`: String | null - Message d'erreur éventuel

**Fonctionnalités**:
- Affiche une modal avec les options de période
- Appelle l'API `/api/refresh-data` avec les paramètres
- Gère les états de chargement et d'erreur
- Recharge la page après succès pour afficher les nouvelles données

#### 2. Intégration dans les Tabs

**NewsTab** (`src/components/company/NewsTab.tsx`):
```tsx
<RefreshDataButton 
  companyName={company.name}
  dataType="news"
/>
```

**ManagementInterviewsTab** (`src/components/company/ManagementInterviewsTab.tsx`):
```tsx
<RefreshDataButton 
  companyName={companyName}
  dataType="interviews"
/>
```

### Backend

#### 1. API Route
**Fichier**: `src/app/api/refresh-data/route.ts`

**Endpoint**: `POST /api/refresh-data`

**Request Body**:
```json
{
  "companyName": "California Closets",
  "dataType": "news",  // ou "interviews"
  "period": "30d",
  "days": 30
}
```

**Response (Success)**:
```json
{
  "success": true,
  "message": "Successfully refreshed news for California Closets",
  "period": "30d",
  "days": 30
}
```

**Response (Error)**:
```json
{
  "error": "Failed to refresh data",
  "details": "Error message"
}
```

**Workflow**:
1. Reçoit la requête avec les paramètres
2. Valide les paramètres (companyName, dataType, period, days)
3. Détermine quel script Python exécuter
4. Active l'environnement virtuel `venv_async`
5. Exécute le script avec les paramètres `--company` et `--days`
6. Copie le résultat dans le dossier `public/` pour le frontend
7. Retourne le statut de succès ou d'erreur

#### 2. Scripts Python Modifiés

**Fichiers**:
- `database/scrape_company_news_async.py`
- `database/scrape_management_interviews.py`

**Nouveaux Arguments CLI**:
```bash
# Mode single company avec période spécifique
python scrape_company_news_async.py --company "California Closets" --days 30

# Mode single company (hérité)
python scrape_company_news_async.py test "California Closets"

# Mode complet (tous les companies)
python scrape_company_news_async.py
```

**Paramètres**:
- `--company <name>`: Nom de l'entreprise à scraper (mode single)
- `--days <number>`: Nombre de jours à rechercher en arrière (7, 30, 90, 180)
- `mode` (positional): "test" pour mode single company

**Implémentation**:
Utilisation de `argparse` pour gérer les arguments de ligne de commande :
```python
parser = argparse.ArgumentParser(description='Scrape company news')
parser.add_argument('mode', nargs='?', default='full')
parser.add_argument('--company', type=str)
parser.add_argument('--days', type=int)
parser.add_argument('test_company', nargs='?')
```

**Note**: Le paramètre `--days` est actuellement reconnu et affiché, mais pas encore utilisé pour filtrer les résultats de recherche. Implémentation future : modifier le prompt OpenAI pour cibler spécifiquement la période demandée.

## 🔐 Sécurité & Performance

### Limitations
- **Timeout**: 60 secondes maximum pour un scraping
- **Buffer**: 10MB maximum pour la sortie du script
- **Rate Limiting**: Pas encore implémenté (à considérer pour la production)

### Validation
- Validation stricte du `dataType` (uniquement "news" ou "interviews")
- Vérification de l'existence des scripts Python
- Gestion des erreurs à chaque étape

## 📊 Flux de Données

```
1. User clicks "Refresh Data" button
   ↓
2. Modal opens with period options
   ↓
3. User selects a period (e.g., "Last 30 days")
   ↓
4. Frontend sends POST to /api/refresh-data
   {
     companyName: "California Closets",
     dataType: "news",
     period: "30d",
     days: 30
   }
   ↓
5. API activates venv and runs Python script
   python scrape_company_news_async.py --company "California Closets" --days 30
   ↓
6. Python script:
   - Calls OpenAI API with web search
   - Scrapes recent articles/interviews
   - Saves to database/company_news_test.json
   ↓
7. API copies result to public/company_news.json
   ↓
8. API returns success response
   ↓
9. Frontend reloads page
   ↓
10. User sees updated data with new articles/interviews
```

## 🧪 Tests

### Test Manuel
1. Ouvrir une page entreprise (ex: California Closets)
2. Aller dans la tab "Company News"
3. Cliquer sur "Refresh Data"
4. Sélectionner "Last 7 days"
5. Attendre 30-60 secondes
6. Vérifier que la page se recharge avec de nouvelles données

### Test API Direct
```bash
curl -X POST http://localhost:3000/api/refresh-data \
  -H "Content-Type: application/json" \
  -d '{
    "companyName": "California Closets",
    "dataType": "news",
    "period": "30d",
    "days": 30
  }'
```

## 🚀 Améliorations Futures

### Court terme
1. **Intégrer `--days` dans le prompt** : Modifier les prompts OpenAI pour cibler spécifiquement la période demandée (ex: "search for news from last 7 days")
2. **Cache intelligent** : Ne pas rescraper si les données ont été mises à jour il y a moins de X heures
3. **WebSocket/SSE** : Notifications en temps réel de la progression du scraping

### Moyen terme
4. **Rate limiting** : Limiter le nombre de refresh par utilisateur/entreprise
5. **Queue system** : File d'attente pour gérer plusieurs requêtes simultanées
6. **Historique** : Garder un historique des refresh pour tracking
7. **Refresh partiel** : Option pour rafraîchir seulement certaines catégories

### Long terme
8. **Auto-refresh** : Système automatique qui refresh les entreprises populaires
9. **Analytics** : Tracking des refresh pour identifier les entreprises les plus consultées
10. **Email notifications** : Notifier l'utilisateur quand le refresh est terminé (pour les longs scraping)

## 📝 Notes Techniques

### Pourquoi reload() ?
Actuellement, on utilise `window.location.reload()` après un refresh réussi car :
- Les données sont stockées dans des fichiers JSON statiques (`public/company_news.json`)
- Next.js sert ces fichiers de manière statique
- Un reload force le re-fetch des données

**Alternative future** : Utiliser une mutation React Query ou un état global pour mettre à jour les données sans reload.

### Environnement Virtuel
Le script utilise `venv_async` qui contient :
- `openai` - Pour l'API OpenAI avec web search
- `httpx` - Client HTTP asynchrone
- Autres dépendances listées dans `database/requirements.txt`

## ✅ Checklist d'Implémentation

- [x] Créer le composant RefreshDataButton
- [x] Intégrer dans NewsTab
- [x] Intégrer dans ManagementInterviewsTab
- [x] Créer l'API route /api/refresh-data
- [x] Modifier scrape_company_news_async.py pour argparse
- [x] Modifier scrape_management_interviews.py pour argparse
- [x] Gérer les états de chargement et erreur
- [x] Copier les résultats vers public/
- [x] Tester le flux complet
- [ ] Implémenter le filtrage par `--days` dans les prompts
- [ ] Ajouter le rate limiting
- [ ] Ajouter le cache intelligent




