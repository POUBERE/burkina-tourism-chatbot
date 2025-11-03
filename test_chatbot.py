"""
Tests unitaires pour le Chatbot Touristique du Burkina Faso
Usage: pytest test_chatbot.py -v
"""

from config import Config
from burkina_chatbot import BurkinaChatbot
import pytest
import os
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))


class TestBurkinaChatbot:
    """Tests de la classe BurkinaChatbot"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_db_path = Config.CHROMA_DB_PATH
        Config.CHROMA_DB_PATH = self.temp_dir
        
        self.chatbot = BurkinaChatbot()

        yield

        Config.CHROMA_DB_PATH = self.original_db_path

    def test_initialization(self):
        """Initialisation du chatbot"""
        assert self.chatbot is not None
        assert self.chatbot.embedding_model is not None
        assert self.chatbot.collection is not None
        assert self.chatbot.config is not None

    def test_load_data(self):
        """Chargement des données"""
        doc_count = self.chatbot.collection.count()
        assert doc_count > 0, "Aucun document chargé dans la base"

    def test_search_similar_documents(self):
        """Recherche de documents similaires"""
        test_queries = [
            "cascades",
            "hôtel",
            "restaurant",
            "prix",
            "Banfora"
        ]

        for query in test_queries:
            docs, scores = self.chatbot.search_similar_documents(query)

            assert len(docs) > 0, f"Aucun document trouvé pour: {query}"
            assert len(docs) == len(
                scores), "Nombre de documents et scores différent"

            for score in scores:
                assert 0 <= score <= 1, f"Score invalide: {score}"

    def test_generate_response(self):
        """Génération de réponses"""
        context = [
            "Les Cascades de Karfiguéla sont situées près de Banfora.",
            "Le prix d'entrée est gratuit, guide optionnel 2000-3000 FCFA."
        ]

        response = self.chatbot.generate_response(
            "Quel est le prix des cascades?",
            context
        )

        assert response is not None
        assert len(response) > 0
        assert not response.startswith("Désolé")

    def test_fallback_response(self):
        """Réponses de secours"""
        response = self.chatbot.generate_response(
            "Question aléatoire",
            []
        )

        assert response is not None
        assert len(response) > 0
        assert "Burkina" in response or "touristique" in response

    def test_chat_function(self):
        """Fonction chat principale"""
        test_conversations = [
            ("Bonjour", ["bienvenue", "assistant", "touristique"]),
            ("Quels sont les sites touristiques ?",
             ["Cascades", "Mosquée", "Parc"]),
            ("Où dormir à Banfora ?", ["hébergement", "hôtel"]),
            ("Prix des cascades", ["gratuit", "FCFA", "guide"]),
            ("Meilleure période pour visiter",
             ["saison", "novembre", "février"])
        ]

        for query, expected_keywords in test_conversations:
            response = self.chatbot.chat(query)

            assert response is not None
            assert len(response) > 0

            response_lower = response.lower()
            found = any(keyword.lower()
                        in response_lower for keyword in expected_keywords)
            assert found, f"Aucun mot-clé trouvé dans la réponse pour: {query}"

    def test_format_functions(self):
        """Fonctions de formatage"""
        site = {
            "nom": "Test Site",
            "ville": "Test Ville",
            "region": "Test Region",
            "description": "Description test",
            "prix": "1000 FCFA",
            "activites": ["Activité 1", "Activité 2"]
        }

        formatted = self.chatbot._format_site_info(site)
        assert "Test Site" in formatted
        assert "Test Ville" in formatted
        assert "1000 FCFA" in formatted
        assert "Activité 1" in formatted

    def test_split_text(self):
        """Découpage de texte"""
        long_text = ". ".join([f"Phrase numéro {i}" for i in range(100)])

        chunks = self.chatbot._split_text(long_text)

        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk) <= self.chatbot.config.CHUNK_SIZE + 100

    def test_reset_database(self):
        """Réinitialisation de la base"""
        count_before = self.chatbot.collection.count()

        self.chatbot.reset_database()

        count_after = self.chatbot.collection.count()

        assert count_after > 0

    def test_edge_cases(self):
        """Cas limites"""
        edge_cases = [
            "",
            "a" * 1000,
            "!@#$%^&*()",
            "12345",
            "burkina" * 50,
        ]

        for query in edge_cases:
            try:
                response = self.chatbot.chat(query)
                assert response is not None
                assert len(response) > 0
            except Exception as e:
                pytest.fail(f"Erreur non gérée pour: {query} - {e}")


class TestConfig:
    """Tests de configuration"""

    def test_config_values(self):
        """Valeurs de configuration"""
        config = Config()

        assert hasattr(config, 'CHROMA_DB_PATH')
        assert hasattr(config, 'COLLECTION_NAME')
        assert hasattr(config, 'EMBEDDING_MODEL')
        assert hasattr(config, 'CHUNK_SIZE')
        assert hasattr(config, 'SIMILARITY_THRESHOLD')

        assert config.CHUNK_SIZE > 0
        assert 0 <= config.SIMILARITY_THRESHOLD <= 1
        assert config.TOP_K_RESULTS > 0

    def test_environment_variables(self):
        """Variables d'environnement"""
        config = Config()

        assert hasattr(config, 'OPENAI_API_KEY')
        assert hasattr(config, 'HUGGINGFACE_API_KEY')


class TestIntegration:
    """Tests d'intégration"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup pour tests d'intégration"""
        self.temp_dir = tempfile.mkdtemp()
        Config.CHROMA_DB_PATH = self.temp_dir
        self.chatbot = BurkinaChatbot()
        yield
        Config.CHROMA_DB_PATH = "./chroma_db"

    def test_complete_conversation_flow(self):
        """Flux de conversation complet"""
        conversation = [
            "Bonjour",
            "Je veux visiter le Burkina Faso",
            "Quels sont les sites à voir ?",
            "Combien coûte l'entrée aux cascades ?",
            "Où dormir près des cascades ?",
            "Merci pour les informations"
        ]

        for message in conversation:
            response = self.chatbot.chat(message)

            assert response is not None
            assert len(response) > 0

            if "cascades" in message.lower():
                assert any(word in response.lower()
                           for word in ["cascade", "karfiguéla", "banfora", "fcfa"])

    def test_similarity_threshold_impact(self):
        """Impact du seuil de similarité"""
        query = "prix cascades Karfiguéla"

        self.chatbot.config.SIMILARITY_THRESHOLD = 0.1
        docs_low, _ = self.chatbot.search_similar_documents(query)

        self.chatbot.config.SIMILARITY_THRESHOLD = 0.8
        docs_high, _ = self.chatbot.search_similar_documents(query)

        assert len(docs_low) >= len(docs_high)


def run_tests():
    """Lance tous les tests"""
    import subprocess
    result = subprocess.run(["pytest", __file__, "-v"],
                            capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0


if __name__ == "__main__":
    success = run_tests()
    if success:
        print("\n✅ Tous les tests sont passés avec succès!")
    else:
        print("\n❌ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")