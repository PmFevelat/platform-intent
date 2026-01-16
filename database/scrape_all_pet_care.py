#!/usr/bin/env python3
"""
Script orchestrateur pour lancer tous les scripts de scraping pour les entreprises Pet Care.
Lance les scripts dans l'ordre : Financial News → Company News → Management Interviews → Job Offers
"""

import subprocess
import sys
import time
from datetime import datetime

# Entreprises Pet Care
PET_CARE_COMPANIES = [
    {
        "name": "Chewy",
        "website": "https://www.chewy.com/"
    },
    {
        "name": "Petco",
        "website": "https://www.petco.com/shop/en/petcostore"
    },
    {
        "name": "Petmate",
        "website": "https://www.petmate.com/"
    },
    {
        "name": "Petsmart",
        "website": "https://www.petsmart.com/"
    }
]

# Scripts à exécuter dans l'ordre
SCRIPTS = [
    {
        "name": "Financial News",
        "script": "scrape_financial_news_async.py",
        "needs_website": False
    },
    {
        "name": "Company News",
        "script": "scrape_company_news_async.py",
        "needs_website": False
    },
    {
        "name": "Management Interviews",
        "script": "scrape_management_interviews.py",
        "needs_website": False
    },
    {
        "name": "Job Offers",
        "script": "analyze_jobs_detailed.py",
        "needs_website": True
    }
]

def run_script(script_name, script_file, company_name, website=None):
    """Exécute un script de scraping pour une entreprise donnée"""
    print(f"\n{'='*70}")
    print(f"🚀 Lancement : {script_name} pour {company_name}")
    print(f"{'='*70}")
    
    # Préparer la commande
    cmd = ["python3", script_file, company_name]
    if website:
        cmd.append(website)
    
    start_time = time.time()
    
    try:
        # Exécuter le script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {script_name} terminé avec succès ({duration:.1f}s)")
            if result.stdout:
                print(f"Output:\n{result.stdout[:500]}")  # Premiers 500 caractères
            return True
        else:
            print(f"❌ {script_name} a échoué")
            if result.stderr:
                print(f"Erreur:\n{result.stderr[:500]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ {script_name} a dépassé le timeout (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False

def main():
    """Fonction principale"""
    print("🐾 SCRAPING COMPLET DES ENTREPRISES PET CARE")
    print("=" * 70)
    print(f"Démarrage : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Entreprises : {len(PET_CARE_COMPANIES)}")
    print(f"Scripts par entreprise : {len(SCRIPTS)}")
    print(f"Total d'opérations : {len(PET_CARE_COMPANIES) * len(SCRIPTS)}")
    print("=" * 70)
    
    results = {
        "success": 0,
        "failed": 0,
        "total": 0
    }
    
    # Pour chaque entreprise
    for company in PET_CARE_COMPANIES:
        print(f"\n\n{'#'*70}")
        print(f"# ENTREPRISE : {company['name']}")
        print(f"{'#'*70}")
        
        # Lancer chaque script
        for script in SCRIPTS:
            results["total"] += 1
            
            website = company["website"] if script["needs_website"] else None
            success = run_script(
                script["name"],
                script["script"],
                company["name"],
                website
            )
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            # Petite pause entre les scripts
            time.sleep(2)
    
    # Résumé final
    print("\n\n" + "=" * 70)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 70)
    print(f"✅ Succès : {results['success']}/{results['total']}")
    print(f"❌ Échecs : {results['failed']}/{results['total']}")
    print(f"📈 Taux de réussite : {(results['success']/results['total']*100):.1f}%")
    print(f"🕐 Fin : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    if results["failed"] > 0:
        print("\n⚠️ Certains scripts ont échoué. Vérifiez les logs ci-dessus.")
        return 1
    else:
        print("\n🎉 Tous les scripts ont été exécutés avec succès !")
        print("\n📝 Prochaines étapes :")
        print("   1. Vérifiez les fichiers JSON générés dans public/")
        print("   2. Rafraîchissez l'interface web /jobs")
        print("   3. Consultez les pages détaillées de chaque entreprise")
        return 0

if __name__ == "__main__":
    sys.exit(main())