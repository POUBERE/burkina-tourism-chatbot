"""
Configuration centralisée pour le chatbot touristique du Burkina Faso
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    # Configuration API
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

    # Configuration ChromaDB
    CHROMA_DB_PATH = "./chroma_db"
    COLLECTION_NAME = "burkina_tourism"

    # Modèle d'embeddings multilingue pour supporter le français
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # Paramètres de découpage des documents
    CHUNK_SIZE = 600  # Taille des segments de texte
    CHUNK_OVERLAP = 150  # Chevauchement entre segments

    # Paramètres de recherche
    SIMILARITY_THRESHOLD = 0.30  # Seuil de pertinence des résultats
    TOP_K_RESULTS = 3  # Nombre de résultats à retourner

    # Configuration du modèle de génération
    USE_LOCAL_MODEL = False  # Utiliser un modèle local ou l'API
    LOCAL_MODEL_NAME = "microsoft/DialoGPT-medium"

    # Chemins des données
    DATA_JSON_PATH = "./data/burkina_tourism_data.json"
    DATA_TXT_PATH = "./data/burkina_tourism_data.txt"

    # Configuration Streamlit
    STREAMLIT_THEME = "light"
    MAX_MESSAGE_HISTORY = 50

    # Paramètres de génération de réponses
    MAX_RESPONSE_LENGTH = 500
    TEMPERATURE = 0.7

    # Mode debug
    DEBUG = True


# Instance de configuration
config = Config()

# Affichage de la configuration au démarrage
if config.DEBUG:
    print("=" * 60)
    print("CONFIGURATION DU CHATBOT BURKINA FASO")
    print("=" * 60)
    print(
        f"✓ OPENAI_API_KEY: {'Configurée' if config.OPENAI_API_KEY else 'Non configurée'}")
    print(
        f"✓ HUGGINGFACE_API_KEY: {'Configurée' if config.HUGGINGFACE_API_KEY else 'Non configurée'}")
    print(f"✓ EMBEDDING_MODEL: {config.EMBEDDING_MODEL}")
    print(f"✓ CHUNK_SIZE: {config.CHUNK_SIZE}")
    print(f"✓ CHUNK_OVERLAP: {config.CHUNK_OVERLAP}")
    print(f"✓ SIMILARITY_THRESHOLD: {config.SIMILARITY_THRESHOLD}")
    print(f"✓ TOP_K_RESULTS: {config.TOP_K_RESULTS}")
    print(f"✓ USE_LOCAL_MODEL: {config.USE_LOCAL_MODEL}")
    print(f"✓ DATA_JSON_PATH: {config.DATA_JSON_PATH}")
    print(f"✓ DATA_TXT_PATH: {config.DATA_TXT_PATH}")
    print(f"✓ MAX_MESSAGE_HISTORY: {config.MAX_MESSAGE_HISTORY}")
    print(f"✓ MAX_RESPONSE_LENGTH: {config.MAX_RESPONSE_LENGTH}")
    print(f"✓ TEMPERATURE: {config.TEMPERATURE}")
    print("=" * 60)