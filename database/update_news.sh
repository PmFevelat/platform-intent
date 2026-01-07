#!/bin/bash

# Script helper pour gérer les actualités des entreprises
# Usage: ./update_news.sh [command]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATABASE_DIR="$SCRIPT_DIR"
PUBLIC_DIR="$SCRIPT_DIR/../public"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 n'est pas installé"
        exit 1
    fi
}

check_venv() {
    if [ ! -d "$DATABASE_DIR/venv" ]; then
        print_info "Environnement virtuel non trouvé, création..."
        python3 -m venv "$DATABASE_DIR/venv"
        source "$DATABASE_DIR/venv/bin/activate"
        pip install -r "$DATABASE_DIR/requirements.txt"
        print_success "Environnement virtuel créé"
    fi
}

activate_venv() {
    source "$DATABASE_DIR/venv/bin/activate"
}

test_company() {
    print_header "Test sur une entreprise"
    
    check_python
    check_venv
    activate_venv
    
    COMPANY_NAME=${1:-"California Closets"}
    
    print_info "Test sur : $COMPANY_NAME"
    python3 "$DATABASE_DIR/scrape_company_news.py" test "$COMPANY_NAME"
    
    if [ -f "$DATABASE_DIR/company_news_test.json" ]; then
        print_success "Test terminé avec succès"
        print_info "Résultats dans : database/company_news_test.json"
    else
        print_error "Erreur lors du test"
        exit 1
    fi
}

scrape_all() {
    print_header "Scraping de toutes les entreprises"
    
    check_python
    check_venv
    activate_venv
    
    print_info "Lancement du scraping..."
    python3 "$DATABASE_DIR/scrape_company_news.py"
    
    if [ -f "$DATABASE_DIR/company_news.json" ]; then
        print_success "Scraping terminé avec succès"
        
        # Afficher les statistiques
        echo ""
        print_info "Statistiques :"
        python3 -c "
import json
with open('$DATABASE_DIR/company_news.json', 'r') as f:
    data = json.load(f)
    total = len(data)
    total_news = sum(len(company.get('news_items', [])) for company in data.values())
    successful = sum(1 for company in data.values() if company.get('scrape_metadata', {}).get('success'))
    print(f'   📊 Entreprises traitées: {total}')
    print(f'   ✅ Succès: {successful}')
    print(f'   📰 Total actualités: {total_news}')
    if total > 0:
        print(f'   📈 Moyenne: {total_news/total:.1f} actualités/entreprise')
"
    else
        print_error "Erreur lors du scraping"
        exit 1
    fi
}

deploy_to_frontend() {
    print_header "Déploiement vers le frontend"
    
    if [ ! -f "$DATABASE_DIR/company_news.json" ]; then
        print_error "Fichier company_news.json non trouvé"
        print_info "Lancez d'abord le scraping avec : ./update_news.sh scrape"
        exit 1
    fi
    
    # Créer le dossier public si nécessaire
    mkdir -p "$PUBLIC_DIR"
    
    # Copier le fichier
    cp "$DATABASE_DIR/company_news.json" "$PUBLIC_DIR/news_data.json"
    
    print_success "Fichier copié vers public/news_data.json"
    print_info "Le frontend peut maintenant accéder aux actualités"
}

full_update() {
    print_header "Mise à jour complète"
    
    scrape_all
    echo ""
    deploy_to_frontend
    
    echo ""
    print_success "Mise à jour complète terminée !"
    print_info "Vous pouvez maintenant consulter les actualités dans l'application"
}

show_help() {
    echo "Usage: ./update_news.sh [command]"
    echo ""
    echo "Commands:"
    echo "  test [company]    Test sur une seule entreprise (défaut: California Closets)"
    echo "  scrape            Scraper toutes les entreprises"
    echo "  deploy            Déployer les données vers le frontend"
    echo "  full              Mise à jour complète (scrape + deploy)"
    echo "  help              Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  ./update_news.sh test \"California Closets\""
    echo "  ./update_news.sh scrape"
    echo "  ./update_news.sh deploy"
    echo "  ./update_news.sh full"
}

# Main
case "${1:-help}" in
    test)
        test_company "$2"
        ;;
    scrape)
        scrape_all
        ;;
    deploy)
        deploy_to_frontend
        ;;
    full)
        full_update
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Commande inconnue: $1"
        echo ""
        show_help
        exit 1
        ;;
esac








