#!/bin/bash
# Script pour compléter automatiquement le pipeline après l'analyse des jobs

set -e

cd "/Users/pierremariefevelat/Desktop/Presti /Intent/database"
source venv_async/bin/activate

echo "=============================================================================="
echo "🤖 AUTO-COMPLETION DU PIPELINE"
echo "=============================================================================="
echo ""
echo "Attente de la fin de l'analyse des jobs..."
echo ""

# Attendre que l'analyse soit terminée (vérifier si le processus analyze_jobs_openai.py existe)
while pgrep -f "analyze_jobs_openai.py" > /dev/null; do
    # Compter le nombre de jobs analysés
    ANALYZED=$(python3 -c "
import json
try:
    with open('jobs_data.json', 'r') as f:
        data = json.load(f)
    analyzed = sum(1 for c in data['companies'] for j in c.get('jobs', []) if j.get('analysis'))
    total = sum(len(c.get('jobs', [])) for c in data['companies'])
    print(f'{analyzed}/{total}')
except:
    print('0/0')
" 2>/dev/null || echo "?/?")
    
    echo -ne "\r⏳ Analyse en cours... Jobs analysés: $ANALYZED"
    sleep 10
done

echo -e "\n✅ Analyse des jobs terminée!\n"

# Liste des 14 nouvelles entreprises
COMPANIES=(
    "Millerknoll"
    "Palliser Furniture Ltd."
    "Rooms to Go"
    "Article"
    "American Leather"
    "Serena & Lily"
    "Rowe Furniture"
    "Room & Board"
    "Bassett Furniture"
    "Living Spaces"
    "Jonathan Louis"
    "Theodore Alexander"
    "Kimball International"
    "Saks Global"
)

echo "=============================================================================="
echo "ÉTAPE 3/5 : SCRAPING DES COMPANY NEWS"
echo "=============================================================================="
echo ""

# Scraper les news pour chaque nouvelle entreprise
for i in "${!COMPANIES[@]}"; do
    company="${COMPANIES[$i]}"
    num=$((i+1))
    echo "[$num/${#COMPANIES[@]}] 📰 $company..."
    
    python3 scrape_company_news_hybrid_async.py --company "$company" 2>&1 | grep -E "(✅|articles|Perplexity|OpenAI)" || true
    
    sleep 2
done

echo ""
echo "✅ Company news scrapées"
echo ""

echo "=============================================================================="
echo "ÉTAPE 4/5 : SCRAPING DES MANAGEMENT INTERVIEWS"
echo "=============================================================================="
echo ""

# Scraper les interviews pour chaque nouvelle entreprise
for i in "${!COMPANIES[@]}"; do
    company="${COMPANIES[$i]}"
    num=$((i+1))
    echo "[$num/${#COMPANIES[@]}] 🎤 $company..."
    
    python3 scrape_management_interviews.py test "$company" 2>&1 | grep -E "(✅|interviews|Perplexity|OpenAI)" || true
    
    sleep 2
done

echo ""
echo "✅ Management interviews scrapées"
echo ""

echo "=============================================================================="
echo "ÉTAPE 5/5 : MISE À JOUR DU FRONTEND"
echo "=============================================================================="
echo ""

# Copier les fichiers vers public/
if [ -f "company_news.json" ]; then
    cp company_news.json ../public/news_data.json
    echo "✅ news_data.json copié"
fi

if [ -f "management_interviews.json" ]; then
    cp management_interviews.json ../public/management_interviews.json
    echo "✅ management_interviews.json copié"
fi

# Conversion des jobs pour le frontend
echo "🔄 Conversion jobs_analysis.json..."
python3 convert_v2_to_frontend.py

echo ""
echo "=============================================================================="
echo "✅ PIPELINE COMPLÈTE TERMINÉE !"
echo "=============================================================================="
echo ""

# Statistiques finales
python3 check_pipeline_status.py

echo ""
echo "=============================================================================="

