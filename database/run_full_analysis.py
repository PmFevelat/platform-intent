#!/usr/bin/env python3
"""
Script principal pour exécuter l'analyse complète des tendances
Enchaîne automatiquement :
1. Analyse des tendances (analyze_trends.py)
2. Conversion vers le frontend (convert_trends_to_frontend.py)
"""

import subprocess
import sys
import os
from datetime import datetime

def print_header(text):
    """Affiche un en-tête stylisé"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def run_command(script_name, description):
    """Exécute un script Python et gère les erreurs"""
    print(f"🚀 {description}...")
    print(f"📝 Exécution de : {script_name}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✅ {description} terminé avec succès !\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors de {description}")
        print(f"Code de sortie : {e.returncode}\n")
        return False
    except FileNotFoundError:
        print(f"\n❌ Fichier introuvable : {script_name}")
        print("Assurez-vous d'être dans le répertoire 'database/'\n")
        return False

def check_prerequisites():
    """Vérifie que les fichiers nécessaires existent"""
    required_files = [
        'jobs_data.json',
        'analyze_trends.py',
        'convert_trends_to_frontend.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Fichiers manquants :")
        for file in missing_files:
            print(f"   - {file}")
        print("\nAssurez-vous d'être dans le répertoire 'database/' et que tous les fichiers sont présents.")
        return False
    
    return True

def main():
    start_time = datetime.now()
    
    print_header("🎯 PRESTI.AI - ANALYSE COMPLÈTE DES TENDANCES")
    
    print("📋 Ce script va exécuter :")
    print("   1️⃣  Analyse des tendances (GPT-4o-mini)")
    print("   2️⃣  Conversion vers le format frontend")
    print()
    
    # Vérifier les prérequis
    print("🔍 Vérification des prérequis...")
    if not check_prerequisites():
        sys.exit(1)
    print("✅ Tous les fichiers nécessaires sont présents\n")
    
    # Étape 1 : Analyse des tendances
    print_header("ÉTAPE 1/2 : ANALYSE DES TENDANCES")
    if not run_command('analyze_trends.py', 'Analyse des tendances'):
        print("⚠️  L'analyse a échoué. Arrêt du processus.")
        sys.exit(1)
    
    # Étape 2 : Conversion frontend
    print_header("ÉTAPE 2/2 : CONVERSION VERS LE FRONTEND")
    if not run_command('convert_trends_to_frontend.py', 'Conversion vers le frontend'):
        print("⚠️  La conversion a échoué.")
        sys.exit(1)
    
    # Résumé final
    elapsed_time = datetime.now() - start_time
    print_header("✅ ANALYSE COMPLÈTE TERMINÉE")
    
    print(f"⏱️  Durée totale : {elapsed_time}")
    print()
    print("📁 Fichiers générés :")
    print("   ✓ database/jobs_trends_analysis.json")
    print("   ✓ public/data.json")
    print()
    print("🎨 Prochaine étape :")
    print("   → Lancez l'application web et consultez l'onglet 'Trends'")
    print()
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processus interrompu par l'utilisateur")
        sys.exit(1)

