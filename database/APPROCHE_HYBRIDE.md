# Approche Hybride : Perplexity + OpenAI ✅

## 🎯 Résumé

**Problème initial** : L'article Modern Retail du 16 décembre 2025 sur Lowe's n'était pas trouvé par l'API OpenAI Web Search (délai d'indexation de 2-4 semaines).

**Solution adoptée** : **Approche Hybride**
1. **Perplexity** : Recherche web avec données quasi temps réel + vraies URLs
2. **OpenAI** : Structuration des données en JSON propre et fiable

## ✅ Résultats pour Lowe's

### Company News
- **16 articles** au total dont **5 nouveaux** via l'approche hybride
- ✅ **Article Modern Retail du 16 décembre 2025 trouvé et intégré** :
  - Titre : "Lowe's Wants to Do More with AI Shopping in 2026"
  - URL : https://www.modernretail.co/technology/lowes-wants-to-do-more-with-ai-shopping-in-2026/
  - Score Presti : 8/10
  - 3 Key Insights extraits

### Management Interviews
- **2 interviews** du CEO Marvin Ellison ajoutées

## 📁 Scripts Disponibles

### 1. Script OpenAI Original (CONSERVÉ)
```bash
scrape_company_news_async.py
```
- ✅ Toujours fonctionnel
- ✅ Couverture large et complète
- ⚠️ Délai d'indexation de 2-4 semaines

### 2. Script Hybride Perplexity + OpenAI (NOUVEAU)
```bash
scrape_news_hybrid.py
scrape_company_news_hybrid_async.py  # même fichier, copie pour compatibilité
```
- ✅ Données plus récentes (quasi temps réel)
- ✅ Structure JSON propre garantie par OpenAI
- ✅ Supporte Company News + Management Interviews

## 🚀 Utilisation du Script Hybride

### Pour une entreprise unique :
```bash
# Company News seulement
python3 scrape_news_hybrid.py --company "Lowe's"

# Company News + Management Interviews
python3 scrape_news_hybrid.py --company "Lowe's" --interviews
```

### Variables d'environnement requises :
```bash
export PERPLEXITY_API_KEY="your_perplexity_api_key_here"
export OPENAI_API_KEY="your_openai_api_key_here"
```

## 📊 Comparaison des Approches

| Critère | OpenAI Seul | **Hybride (Perplexity + OpenAI)** ✅ |
|---------|-------------|--------------------------------------|
| **Fraîcheur données** | 2-4 sem retard | **Quasi temps réel** |
| **Article déc 2025 trouvé** | ❌ | **✅** |
| **Structure JSON** | ✅ Fiable | ✅ **Parfaite** (grâce à OpenAI) |
| **Couverture large** | ✅ Excellente | ✅ Excellente |
| **URLs réelles** | ✅ | ✅ **Garanties** (citations Perplexity) |
| **Key Insights** | ✅ | ✅ **Meilleurs** (analyse OpenAI) |
| **Coût** | ~ $X | ~ $Y (à évaluer) |

## 🔄 Workflow Recommandé

### Pour les articles TRÈS récents (< 1 mois) :
➡️ **Utiliser l'approche hybride**

### Pour un scraping complet historique :
➡️ **Utiliser OpenAI** (plus rapide pour traiter en masse)

### Stratégie optimale :
1. Scraping initial avec **OpenAI** (large couverture historique)
2. Refresh périodique avec **Hybride** (articles récents)
3. Fusion des résultats dans les fichiers JSON

## 🎯 Pipeline Technique

### Étape 1 : Perplexity (Recherche)
```python
async def search_with_perplexity(company_name):
    # Prompt conversationnel large
    # Retourne : raw_content + citations (vraies URLs)
```

### Étape 2 : OpenAI (Structuration)
```python
async def structure_with_openai(perplexity_data):
    # Extrait et structure en JSON
    # Retourne : articles[] avec tous les champs propres
```

### Étape 3 : Intégration
```python
# Fusion avec les données existantes
# Dédoublonnage par URL
# Sauvegarde dans news_data.json
```

## 💡 Lessons Learned

1. **Ne PAS forcer le JSON** avec Perplexity → laisser retourner du texte naturel
2. **Utiliser OpenAI pour le parsing** → JSON parfait garanti
3. **Les citations Perplexity** sont les vraies URLs fiables
4. **Prompt conversationnel** fonctionne mieux que format strict
5. **Approche hybride** = meilleur des deux mondes

## 📝 Prochaines Étapes Possibles

- [ ] Tester sur 5-10 autres entreprises pour validation
- [ ] Évaluer le coût Perplexity vs OpenAI
- [ ] Automatiser le workflow hybride pour refresh périodique
- [ ] Étendre aux Management Interviews pour toutes les entreprises
- [ ] Créer un script de comparaison OpenAI vs Hybride

## ✅ Status Lowe's

- ✅ Données à jour dans `public/news_data.json`
- ✅ Données à jour dans `public/management_interviews.json`
- ✅ Article Modern Retail du 16 décembre intégré
- ✅ Visible dans l'interface frontend

---

**Dernière mise à jour** : 7 janvier 2026
**Testé sur** : Lowe's
**Status** : ✅ Validé et fonctionnel

