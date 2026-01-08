# Module de Scraping des Interviews Management

Ce module utilise l'API OpenAI avec la fonctionnalité Web Search pour récupérer automatiquement les interviews et insights des décideurs clés des entreprises prospects.

## 🎯 Objectif

Identifier et collecter les interviews, talks, podcasts et articles des executives dans les fonctions clés pour comprendre leurs priorités stratégiques et adapter l'approche commerciale Presti.

**Fonctions ciblées :**
- 🛒 **E-commerce** : CDO, VP E-commerce, E-commerce Director
- 📢 **Marketing** : CMO, VP Marketing, Marketing Director
- 💻 **Digital** : Chief Digital Officer, VP Digital, Digital Director
- 🎨 **Design** : Chief Design Officer, VP Design, Design Director
- 🎨 **Creative** : Chief Creative Officer, Creative Director, VP Creative
- 🎨 **Art Direction** : Art Director, Photography Director

## 📋 Prérequis

```bash
# Installer les dépendances Python (si pas déjà fait)
cd database
pip install -r requirements.txt
```

## 🔑 Configuration

La clé API OpenAI est déjà configurée dans le script (identique à `scrape_company_news_async.py`).

## 🚀 Utilisation

### Test sur une seule entreprise

Pour tester le script sur une entreprise spécifique :

```bash
cd database
python scrape_management_interviews.py test "California Closets"
```

Résultat : `management_interviews_test.json`

### Traiter toutes les entreprises

Pour récupérer les interviews de toutes les entreprises du fichier `jobs_data.json` :

```bash
cd database
python scrape_management_interviews.py
```

Résultat : `management_interviews.json`

Le script :
- ✅ Traite **5 entreprises en parallèle** (configurable avec `MAX_CONCURRENT_REQUESTS`)
- ✅ Sauvegarde la progression de manière incrémentale (tous les 5 résultats)
- ✅ Skip les entreprises déjà traitées avec succès
- ✅ Peut être interrompu et repris à tout moment

## 📊 Structure des Données

### Format de sortie (`management_interviews.json`)

```json
{
  "Nom Entreprise": {
    "company_name": "Nom Entreprise",
    "search_date": "2025-01-06",
    "management_items": [
      {
        "title": "How We're Transforming E-commerce at ABC Corp",
        "source": "Forbes",
        "url": "https://...",
        "published_date": "2024-12-15",
        "format": "interview",
        "executive_name": "John Smith",
        "executive_title": "Chief Digital Officer",
        "summary": "John Smith discusses digital transformation...",
        "key_quotes": [
          "We're investing heavily in visual content...",
          "Our e-commerce platform needs to scale..."
        ],
        "topics_discussed": [
          "digital transformation",
          "e-commerce growth",
          "visual content strategy"
        ],
        "relevance_score": 9,
        "relevance_reason": "CDO directly mentions visual content challenges...",
        "sales_insights": [
          "Approach with e-commerce scaling solutions",
          "Emphasize time-to-market for visual content"
        ]
      }
    ],
    "key_executives_identified": [
      {
        "name": "John Smith",
        "title": "Chief Digital Officer",
        "relevance": "Key decision-maker for digital and visual content",
        "content_count": 3
      }
    ],
    "overall_assessment": {
      "decision_maker_visibility": "high",
      "strategic_priorities": [
        "E-commerce platform modernization",
        "Visual content production at scale"
      ],
      "presti_entry_points": [
        "Help scale visual content production for growing e-commerce",
        "Reduce time-to-market for new product launches"
      ],
      "recommended_contact": "Target John Smith (CDO) first - he's publicly discussing visual content challenges and has decision-making authority."
    }
  }
}
```

## 📂 Intégration Frontend

Une fois les interviews collectées, il faut copier le fichier JSON dans le dossier public :

```bash
cp database/management_interviews.json public/management_interviews.json
```

Le frontend chargera automatiquement les données depuis `/management_interviews.json`.

## 🎨 Pages Frontend

### Onglet "Management Interviews"
- **URL** : `/jobs/[company]` → onglet "Management Interviews"
- **Description** : Liste des interviews et insights des décideurs clés
- **Fonctionnalités** :
  - Vue d'ensemble des executives identifiés
  - Nombre total d'interviews trouvées
  - Score moyen de pertinence
  - Filtrage par format (interview, podcast, keynote, etc.)
  - Filtrage par date (7 jours, 30 jours, 3 mois, etc.)
  - Recherche par nom d'executive, titre, ou sujet
  - Cards cliquables avec modal détaillé
  - Citations clés extraites
  - Insights actionnables pour la vente

## 🏷️ Formats d'Interviews

- **💬 Interview** : Interview écrite ou vidéo
- **🎙️ Podcast** : Apparition dans un podcast
- **🎤 Keynote** : Discours lors d'événements
- **📝 Article** : Article ou op-ed par l'executive
- **👥 Panel** : Participation à un panel de discussion
- **💼 LinkedIn** : Post LinkedIn substantiel
- **🖥️ Webinar** : Présentation webinar
- **👤 Profile** : Article de profil sur l'executive

## 🔍 Méthodologie de Recherche

Le script utilise **6 patterns de recherche** distincts :

### 1. Executive Interviews by Title
Recherche ciblée par fonction :
- "{company} CEO interview"
- "{company} CMO interview"
- "{company} Chief Digital Officer interview"
- etc.

### 2. Strategic Topics
Recherche par thématique stratégique :
- "{company} digital strategy"
- "{company} e-commerce strategy"
- "{company} innovation strategy"
- etc.

### 3. Speaking Engagements
Recherche d'interventions publiques :
- "{company} conference"
- "{company} keynote"
- "{company} speaker"
- "{company} podcast"
- etc.

### 4. Leadership & Vision
Recherche de contenu leadership :
- "{company} leadership"
- "{company} vision"
- "{company} CEO on"
- etc.

### 5. Thought Leadership
Recherche de contenu expertise :
- "{company} LinkedIn"
- "{company} thought leadership"
- "{company} executive insights"
- etc.

### 6. Media Mentions
Recherche dans publications majeures :
- "{company} Forbes interview"
- "{company} Business of Home interview"
- "{company} WWD interview"
- etc.

## 🎯 Critères de Pertinence

### Score 8-10 : Haute Pertinence
- Interview approfondie avec insights stratégiques directement pertinents pour Presti
- Discussion de visual content, e-commerce scale, digital transformation, challenges catalogue

### Score 6-8 : Moyenne Pertinence
- Interview avec sujets stratégiques pertinents (technologie, innovation, customer experience, opérations)

### Score 4-6 : Pertinence Contextuelle
- Mention d'executive ou citation dans article sur sujets pertinents

### Score 1-3 : Faible Pertinence
- Insights minimaux ou contenu générique

## 📈 Exemple de Statistiques

```
📈 Statistiques:
   - Entreprises traitées: 45
   - Succès: 43
   - Total interviews: 523
   - Moyenne par entreprise: 11.6
```

## 🔄 Workflow Complet

### 1. **Collecter les interviews** :
```bash
cd database
python scrape_management_interviews.py
```

### 2. **Copier les données vers le frontend** :
```bash
cp database/management_interviews.json public/management_interviews.json
```

### 3. **Accéder aux interviews** :
- Ouvrir l'application web
- Sélectionner une entreprise
- Naviguer vers l'onglet "Management Interviews"
- Explorer les interviews et insights des décideurs

## 🎯 Cas d'Usage Commercial

### Identification des Décideurs
- **Qui sont les key decision-makers** dans les fonctions pertinentes ?
- **Combien de contenu** chaque executive a publié (indicateur de visibilité)

### Compréhension des Priorités
- **Quelles sont leurs priorités stratégiques** mentionnées publiquement ?
- **Quels challenges** rencontrent-ils ?
- **Quelle est leur vision** de la transformation digitale ?

### Personnalisation de l'Approche
- **Angles d'approche** spécifiques basés sur leurs déclarations
- **Contact recommandé** : Quel executive cibler en premier et pourquoi
- **Points d'entrée** : Sujets à aborder basés sur leurs préoccupations

### Préparation aux Conversations
- **Citations clés** à référencer dans les emails/appels
- **Contexte** sur leur parcours et expertise
- **Crédibilité** : Montrer qu'on a fait ses devoirs

## ⚙️ Fonctionnalité OpenAI Web Search

✅ Le script utilise la **vraie fonctionnalité Web Search d'OpenAI** via la Responses API qui permet de :

- 🔍 Effectuer des recherches web **en temps réel**
- 🎤 Accéder aux interviews et talks **récents et vérifiés**
- 🎯 Trouver des sources **authentiques** (Forbes, LinkedIn, podcasts, conférences)
- 🧠 Extraire et structurer automatiquement les insights
- 🔗 Fournir des URLs et citations **réelles**

Configuration dans le code :
```python
response = await client.responses.create(
    model="gpt-4o",
    tools=[{
        "type": "web_search",
        "external_web_access": True
    }],
    input=prompt,
    temperature=0.3,
)
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
4. **Mise à jour** : Relancer régulièrement pour obtenir les interviews les plus récentes
5. **Combinaison** : Utiliser en combinaison avec "Company News" pour une vue 360° complète

## 🆚 Différence avec Company News

| Aspect | Company News | Management Interviews |
|--------|--------------|----------------------|
| **Focus** | Actualités de l'entreprise | Décideurs et leurs insights |
| **Format** | Articles de presse | Interviews, podcasts, keynotes |
| **Contenu** | Annonces, initiatives, projets | Vision, priorités, challenges |
| **Usage** | Identifier les signaux d'opportunité | Identifier les décideurs et personnaliser l'approche |
| **Objectif** | QUOI : Que se passe-t-il ? | QUI : Qui décide ? Quelle est leur vision ? |

## 🎯 Complémentarité

Les deux modules sont **complémentaires** :

1. **Company News** → Identifier les opportunités (e.g., "Expansion e-commerce +150%")
2. **Management Interviews** → Identifier qui contacter (e.g., "CDO parle de challenges visuels")
3. **Combinaison** → Approche ultra-personnalisée et informée

## 📞 Support

Pour toute question ou problème :
- Vérifier les logs de la console
- Consulter le fichier `management_interviews.json` pour voir les erreurs
- Valider la clé API OpenAI

---

**Créé le** : 6 janvier 2026
**Dernière mise à jour** : 6 janvier 2026



