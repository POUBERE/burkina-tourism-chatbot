#!/usr/bin/env python
"""
Setup automatique du projet Chatbot Touristique Burkina Faso
Usage: python setup.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class ProjectSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.env_example = self.project_root / ".env.example"
        self.env_file = self.project_root / ".env"

    def print_banner(self):
        """Bannière du projet"""
        print("=" * 60)
        print("🌍 CHATBOT TOURISTIQUE BURKINA FASO - SETUP")
        print("=" * 60)

    def check_python_version(self):
        """Vérification de la version Python"""
        print("\n📌 Vérification de Python...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("❌ Python 3.8+ requis!")
            sys.exit(1)
        print(
            f"✅ Python {version.major}.{version.minor}.{version.micro} détecté")

    def create_virtual_env(self):
        """Création de l'environnement virtuel"""
        print("\n📌 Création de l'environnement virtuel...")

        if self.venv_path.exists():
            response = input(
                "L'environnement virtuel existe déjà. Le recréer? (o/n): ")
            if response.lower() == 'o':
                shutil.rmtree(self.venv_path)
            else:
                print("✅ Environnement virtuel existant conservé")
                return

        subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)])
        print("✅ Environnement virtuel créé")

    def get_pip_command(self):
        """Commande pip selon le système d'exploitation"""
        if os.name == 'nt':
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")

    def install_dependencies(self):
        """Installation des dépendances"""
        print("\n📌 Installation des dépendances...")

        pip_cmd = self.get_pip_command()

        print("Mise à jour de pip...")
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"])

        if self.requirements_file.exists():
            print("Installation des packages...")

            # PyTorch en version CPU pour réduire la taille
            print("Installation de PyTorch (CPU version)...")
            subprocess.run([
                pip_cmd, "install",
                "torch==2.1.2", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cpu"
            ])

            subprocess.run([pip_cmd, "install", "-r",
                           str(self.requirements_file)])
            print("✅ Dépendances installées")
        else:
            print("❌ Fichier requirements.txt non trouvé!")

    def setup_environment(self):
        """Configuration du fichier .env"""
        print("\n📌 Configuration de l'environnement...")

        if not self.env_file.exists() and self.env_example.exists():
            shutil.copy(self.env_example, self.env_file)
            print("✅ Fichier .env créé depuis .env.example")
            print("⚠️  N'oubliez pas d'ajouter vos clés API si nécessaire (optionnel)")
        elif self.env_file.exists():
            print("✅ Fichier .env déjà présent")
        else:
            print("⚠️  Fichier .env.example non trouvé")

    def create_directories(self):
        """Création de l'arborescence du projet"""
        print("\n📌 Création des répertoires...")

        directories = [
            "data",
            "chroma_db",
            "logs",
            "docs"
        ]

        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Répertoire '{dir_name}' créé/vérifié")

    def download_models(self):
        """Téléchargement des modèles pré-entraînés"""
        print("\n📌 Téléchargement des modèles (première fois seulement)...")

        download_script = """
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM

print("Téléchargement du modèle d'embeddings...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("✅ Modèle d'embeddings téléchargé")

print("Téléchargement du modèle de génération...")
try:
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
    print("✅ Modèle de génération téléchargé")
except Exception as e:
    print(f"⚠️ Modèle de génération non téléchargé (optionnel): {e}")
"""

        python_cmd = self.get_python_command()
        process = subprocess.Popen(
            [python_cmd, "-c", download_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        print(stdout)

    def get_python_command(self):
        """Commande Python selon le système d'exploitation"""
        if os.name == 'nt':
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")

    def test_installation(self):
        """Test des imports"""
        print("\n📌 Test de l'installation...")

        python_cmd = self.get_python_command()

        test_script = """
import streamlit
import sentence_transformers
import chromadb
import torch
print("✅ Tous les modules importés avec succès!")
"""

        result = subprocess.run(
            [python_cmd, "-c", test_script],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(result.stdout)
        else:
            print("❌ Erreur lors du test:")
            print(result.stderr)

    def print_instructions(self):
        """Instructions post-installation"""
        print("\n" + "=" * 60)
        print("🎉 INSTALLATION TERMINÉE!")
        print("=" * 60)

        if os.name == 'nt':
            activate_cmd = r"venv\Scripts\activate"
        else:
            activate_cmd = "source venv/bin/activate"

        print("\n📋 PROCHAINES ÉTAPES:")
        print(f"1. Activer l'environnement: {activate_cmd}")
        print("2. (Optionnel) Ajouter vos clés API dans .env")
        print("3. Lancer le chatbot: streamlit run app.py")
        print("\n💡 COMMANDES UTILES:")
        print("- Test du chatbot: python burkina_chatbot.py")
        print("- Réinitialiser la base: python scrape_data.py")
        print("- Lancer les tests: pytest test_chatbot.py")
        print("\n🌍 Bon voyage au Burkina Faso!")

    def run(self):
        """Exécution complète du setup"""
        try:
            self.print_banner()
            self.check_python_version()
            self.create_virtual_env()
            self.install_dependencies()
            self.setup_environment()
            self.create_directories()
            self.download_models()
            self.test_installation()
            self.print_instructions()

        except KeyboardInterrupt:
            print("\n\n❌ Installation annulée par l'utilisateur")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Erreur lors de l'installation: {e}")
            sys.exit(1)


if __name__ == "__main__":
    setup = ProjectSetup()
    setup.run()