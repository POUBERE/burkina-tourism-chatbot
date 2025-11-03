#!/usr/bin/env python
"""
Script de lancement rapide pour le Chatbot Touristique Burkina Faso
Usage: python run.py
"""

import os
import sys
import subprocess
from pathlib import Path
import platform

def print_banner():
    """Affiche la bannière du projet"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║     🌍 CHATBOT TOURISTIQUE BURKINA FASO                  ║
║          Le Pays des Hommes Intègres                     ║
╚═══════════════════════════════════════════════════════════╝
    """)

def check_environment():
    """Vérifie que l'environnement est prêt"""
    issues = []
    
    # Vérifier la version de Python
    if sys.version_info < (3, 8):
        issues.append("❌ Python 3.8+ requis")
    
    # Vérifier la présence des fichiers essentiels
    required_files = [
        "app.py",
        "burkina_chatbot.py",
        "config.py",
        "requirements.txt"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            issues.append(f"❌ Fichier manquant: {file}")
    
    # Créer le dossier data s'il n'existe pas
    if not Path("data").exists():
        print("📁 Création du dossier data...")
        Path("data").mkdir(exist_ok=True)
    
    # Générer les données si nécessaire
    if not Path("data/burkina_tourism_data.json").exists():
        print("⚠️  Données non trouvées. Génération en cours...")
        subprocess.run([sys.executable, "scrape_data.py"])
    
    # Vérifier la présence d'un environnement virtuel
    if not Path("venv").exists() and not Path(".venv").exists():
        issues.append("⚠️  Environnement virtuel non trouvé. Lancez 'python setup.py' d'abord")
    
    # Créer le fichier .env depuis l'exemple
    if not Path(".env").exists() and Path(".env.example").exists():
        print("📝 Création du fichier .env depuis .env.example...")
        import shutil
        shutil.copy(".env.example", ".env")
    
    return issues

def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    try:
        import streamlit
        import chromadb
        import sentence_transformers
        return True
    except ImportError as e:
        print(f"❌ Dépendances manquantes: {e}")
        print("💡 Installez les dépendances avec: pip install -r requirements.txt")
        return False

def launch_chatbot():
    """Lance le chatbot"""
    print("\n🚀 Lancement du chatbot...")
    print("="*60)
    
    # Commande Python selon le système d'exploitation
    if platform.system() == "Windows":
        python_cmd = "python"
    else:
        python_cmd = "python3"
    
    # Détecter si un environnement virtuel est actif
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Environnement virtuel détecté")
    else:
        print("⚠️  Pas d'environnement virtuel actif")
        
        # Chercher un environnement virtuel existant
        venv_path = Path("venv")
        if not venv_path.exists():
            venv_path = Path(".venv")
        
        if venv_path.exists():
            if platform.system() == "Windows":
                activate_cmd = venv_path / "Scripts" / "activate.bat"
                print(f"💡 Activez l'environnement avec: {activate_cmd}")
            else:
                activate_cmd = venv_path / "bin" / "activate"
                print(f"💡 Activez l'environnement avec: source {activate_cmd}")
    
    print("\n📋 Options de lancement:")
    print("1. Interface Web Streamlit (Recommandé)")
    print("2. Test en ligne de commande")
    print("3. Lancer les tests unitaires")
    print("4. Régénérer les données")
    print("5. Configuration avancée")
    print("6. Quitter")
    
    choice = input("\n👉 Votre choix (1-6): ").strip()
    
    if choice == "1":
        print("\n🌐 Lancement de l'interface Streamlit...")
        print("="*60)
        print("L'application va s'ouvrir dans votre navigateur.")
        print("Si ce n'est pas le cas, ouvrez: http://localhost:8501")
        print("\n📌 Pour arrêter: Ctrl+C")
        print("="*60)
        
        try:
            subprocess.run(["streamlit", "run", "app.py"])
        except KeyboardInterrupt:
            print("\n\n✅ Application arrêtée")
        except FileNotFoundError:
            print("❌ Streamlit non trouvé. Installez avec: pip install streamlit")
            
    elif choice == "2":
        print("\n🤖 Lancement du test en ligne de commande...")
        print("="*60)
        try:
            subprocess.run([python_cmd, "burkina_chatbot.py"])
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
    elif choice == "3":
        print("\n🧪 Lancement des tests unitaires...")
        print("="*60)
        try:
            subprocess.run(["pytest", "test_chatbot.py", "-v"])
        except FileNotFoundError:
            print("❌ Pytest non trouvé. Installez avec: pip install pytest")
            try:
                subprocess.run([python_cmd, "test_chatbot.py"])
            except Exception as e:
                print(f"❌ Erreur: {e}")
                
    elif choice == "4":
        print("\n📊 Régénération des données...")
        print("="*60)
        try:
            subprocess.run([python_cmd, "scrape_data.py"])
        except Exception as e:
            print(f"❌ Erreur: {e}")
            
    elif choice == "5":
        print("\n⚙️  Configuration avancée")
        print("="*60)
        print("1. Éditer .env pour configurer les clés API")
        print("2. Modifier config.py pour les paramètres du chatbot")
        print("3. Ajuster les seuils de similarité dans config.py")
        print("4. Activer/désactiver le mode debug")
        print("\n💡 Consultez README.md pour plus de détails")
        
    elif choice == "6":
        print("\n👋 À bientôt!")
        sys.exit(0)
        
    else:
        print("❌ Choix invalide")

def main():
    """Fonction principale"""
    print_banner()
    
    # Vérifications initiales
    print("🔍 Vérification de l'environnement...")
    issues = check_environment()
    
    if issues:
        print("\n⚠️  Problèmes détectés:")
        for issue in issues:
            print(f"  {issue}")
        
        if any("❌" in issue for issue in issues):
            print("\n💡 Résolvez ces problèmes avant de continuer")
            sys.exit(1)
    else:
        print("✅ Environnement OK")
    
    # Vérification des dépendances
    if not check_dependencies():
        response = input("\n📦 Installer les dépendances maintenant? (o/n): ")
        if response.lower() == 'o':
            print("Installation en cours...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        else:
            print("❌ Installation annulée. Les dépendances sont requises.")
            sys.exit(1)
    
    # Boucle principale
    while True:
        try:
            launch_chatbot()
            
            # Proposer de relancer
            response = input("\n\n🔄 Relancer une action? (o/n): ")
            if response.lower() != 'o':
                print("\n👋 Merci d'avoir utilisé le Chatbot Burkina Tourisme!")
                break
                
        except KeyboardInterrupt:
            print("\n\n✅ Programme interrompu par l'utilisateur")
            break
        except Exception as e:
            print(f"\n❌ Erreur inattendue: {e}")
            break

if __name__ == "__main__":
    main()