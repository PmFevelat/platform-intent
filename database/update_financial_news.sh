#!/bin/bash

# Script pour mettre à jour les données financières pour toutes les entreprises
# Usage: ./update_financial_news.sh

set -e

# Couleurs pour le terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Mise à jour Financial News${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Activer l'environnement virtuel
source venv_async/bin/activate

# Liste des entreprises (mêmes que pour Company News)
companies=(
    "La-Z-Boy"
    "Williams Sonoma"
    "Millerknoll"
    "Palliser Furniture Ltd."
    "Rooms to Go"
    "Article"
    "American Leather"
    "Serena & Lily"
    "Anthropologie Home"
    "Rowe Furniture"
    "Room & Board"
    "Bassett Furniture"
    "Living Spaces"
    "Jonathan Louis"
    "Theodore Alexander"
    "Kimball International"
    "Ballard Designs"
    "Design Within Reach"
    "Saks Global"
    "Costco"
    "Target"
    "Home Depot"
    "California Closets"
    "Balsam Brands"
    "Ashley Furniture Industries"
    "Arhaus"
)

# Fichier de sortie consolidé
OUTPUT_FILE="../public/financial_news.json"

echo -e "${YELLOW}Début du scraping pour ${#companies[@]} entreprises...${NC}\n"

# Initialiser le fichier JSON
echo "{" > "$OUTPUT_FILE"
first=true

# Scraper chaque entreprise
for company in "${companies[@]}"; do
    echo -e "${GREEN}→ Scraping: ${company}${NC}"
    
    # Lancer le script
    python3 scrape_financial_news.py --company "$company" 2>&1 | grep -E "(✅|💰|❌|⚠️)"
    
    # Nom du fichier de résultat
    safe_name=$(echo "$company" | sed 's/ /_/g')
    result_file="financial_${safe_name}_results.json"
    
    # Si le fichier existe, l'ajouter au fichier consolidé
    if [ -f "$result_file" ]; then
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$OUTPUT_FILE"
        fi
        
        # Ajouter l'entrée pour cette entreprise
        echo "  \"$company\": $(cat "$result_file" | tail -n +2 | head -n -1)" >> "$OUTPUT_FILE"
        
        # Supprimer le fichier temporaire
        rm "$result_file"
        
        echo -e "${GREEN}✓ Complété: ${company}${NC}\n"
    else
        echo -e "${YELLOW}⚠ Aucun résultat pour ${company}${NC}\n"
    fi
    
    # Petite pause entre les requêtes
    sleep 2
done

# Fermer le JSON
echo "}" >> "$OUTPUT_FILE"

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Mise à jour terminée !${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Fichier généré: ${OUTPUT_FILE}"
echo -e "Total entreprises: ${#companies[@]}"
