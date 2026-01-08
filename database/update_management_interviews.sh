#!/bin/bash

# Script pour scraper les interviews management et mettre à jour le frontend
# Usage: ./update_management_interviews.sh [test|full] [company_name]

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}║         🎤 Management Interviews Scraper 🎤              ║${NC}"
echo -e "${BLUE}║                                                          ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}\n"

# Check if virtual environment exists
if [ ! -d "venv_async" ]; then
    echo -e "${RED}❌ Virtual environment 'venv_async' not found!${NC}"
    echo -e "${YELLOW}Please create it with: python3 -m venv venv_async${NC}"
    echo -e "${YELLOW}Then install dependencies: ./venv_async/bin/pip install -r requirements.txt${NC}"
    exit 1
fi

MODE="${1:-full}"
COMPANY_NAME="${2}"

if [ "$MODE" == "test" ]; then
    if [ -z "$COMPANY_NAME" ]; then
        COMPANY_NAME="California Closets"
    fi
    
    echo -e "${YELLOW}🧪 Mode TEST : Scraping interviews for \"${COMPANY_NAME}\"${NC}\n"
    
    # Run test scraping
    echo -e "${BLUE}📡 Starting web search for management interviews...${NC}"
    ./venv_async/bin/python3 scrape_management_interviews.py test "$COMPANY_NAME"
    
    if [ -f "management_interviews_test.json" ]; then
        echo -e "\n${GREEN}✅ Test completed successfully!${NC}"
        echo -e "${BLUE}📁 Results saved to: management_interviews_test.json${NC}\n"
        
        # Show summary
        echo -e "${YELLOW}📊 Summary:${NC}"
        ./venv_async/bin/python3 -c "
import json
with open('management_interviews_test.json', 'r') as f:
    data = json.load(f)
    for company, info in data.items():
        items = info.get('management_items', [])
        execs = info.get('key_executives_identified', [])
        visibility = info.get('overall_assessment', {}).get('decision_maker_visibility', 'N/A')
        print(f'   - Company: {company}')
        print(f'   - Interviews found: {len(items)}')
        print(f'   - Executives identified: {len(execs)}')
        print(f'   - Decision-maker visibility: {visibility}')
        if items:
            print(f'\n   📰 Top 3 interviews:')
            for i, item in enumerate(items[:3], 1):
                print(f'      {i}. {item.get(\"executive_name\", \"N/A\")} ({item.get(\"executive_title\", \"N/A\")})')
                print(f'         {item.get(\"title\", \"N/A\")} - Score: {item.get(\"relevance_score\", 0)}/10')
"
        
        echo -e "\n${YELLOW}💡 To process all companies, run: ./update_management_interviews.sh full${NC}"
    else
        echo -e "\n${RED}❌ Test failed - no output file generated${NC}"
        exit 1
    fi
    
elif [ "$MODE" == "full" ]; then
    echo -e "${YELLOW}🚀 Mode FULL : Scraping interviews for ALL companies${NC}\n"
    
    # Confirm before running
    echo -e "${YELLOW}⚠️  This will process all companies in jobs_data.json${NC}"
    echo -e "${YELLOW}⚠️  This may take 10-15 minutes and consume OpenAI API credits${NC}"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Aborted.${NC}"
        exit 0
    fi
    
    echo -e "\n${BLUE}📡 Starting web search for all companies...${NC}"
    echo -e "${BLUE}Processing 5 companies in parallel...${NC}\n"
    
    # Run full scraping
    ./venv_async/bin/python3 scrape_management_interviews.py
    
    if [ -f "management_interviews.json" ]; then
        echo -e "\n${GREEN}✅ Scraping completed successfully!${NC}"
        echo -e "${BLUE}📁 Results saved to: management_interviews.json${NC}\n"
        
        # Show statistics
        echo -e "${YELLOW}📊 Statistics:${NC}"
        ./venv_async/bin/python3 -c "
import json
with open('management_interviews.json', 'r') as f:
    data = json.load(f)
    total_interviews = sum(len(info.get('management_items', [])) for info in data.values())
    total_execs = sum(len(info.get('key_executives_identified', [])) for info in data.values())
    successful = sum(1 for info in data.values() if info.get('scrape_metadata', {}).get('success'))
    high_visibility = sum(1 for info in data.values() if info.get('overall_assessment', {}).get('decision_maker_visibility') == 'high')
    
    print(f'   - Companies processed: {len(data)}')
    print(f'   - Successful: {successful}')
    print(f'   - Total interviews: {total_interviews}')
    print(f'   - Average per company: {total_interviews/len(data):.1f}')
    print(f'   - Total executives identified: {total_execs}')
    print(f'   - Companies with high exec visibility: {high_visibility}')
"
        
        # Copy to public folder
        echo -e "\n${BLUE}📋 Copying to frontend...${NC}"
        cp management_interviews.json ../public/management_interviews.json
        echo -e "${GREEN}✅ Copied to public/management_interviews.json${NC}"
        
        echo -e "\n${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                                                          ║${NC}"
        echo -e "${GREEN}║         🎉 All done! Management interviews updated! 🎉   ║${NC}"
        echo -e "${GREEN}║                                                          ║${NC}"
        echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}\n"
        
        echo -e "${YELLOW}💡 Access the interviews in the web app:${NC}"
        echo -e "${BLUE}   1. Open your application${NC}"
        echo -e "${BLUE}   2. Select a company${NC}"
        echo -e "${BLUE}   3. Click on the 'Management Interviews' tab${NC}\n"
    else
        echo -e "\n${RED}❌ Scraping failed - no output file generated${NC}"
        exit 1
    fi
    
else
    echo -e "${RED}❌ Invalid mode: $MODE${NC}"
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ${BLUE}./update_management_interviews.sh test [company_name]${NC}  - Test on one company"
    echo -e "  ${BLUE}./update_management_interviews.sh full${NC}                - Process all companies"
    exit 1
fi



