"""
Chatbot RAG pour le tourisme au Burkina Faso
"""

import os
import json
import logging
from typing import List, Dict, Optional, Tuple
import re
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BurkinaChatbot:
    def __init__(self):
        """Initialisation du chatbot"""
        self.config = Config()
        
        logger.info("Chargement du modèle d'embeddings...")
        self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)
        
        logger.info("Initialisation de la base vectorielle...")
        self.chroma_client = chromadb.PersistentClient(
            path=self.config.CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        try:
            self.collection = self.chroma_client.get_collection(
                name=self.config.COLLECTION_NAME
            )
            logger.info(f"Collection existante récupérée: {self.collection.count()} documents")
        except:
            logger.info("Création d'une nouvelle collection...")
            self.collection = self.chroma_client.create_collection(
                name=self.config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        
        if self.collection.count() == 0:
            self.load_data()
        
        # Mots-clés pour identifier les catégories de questions
        self.category_keywords = {
            "hebergement": ["dormir", "hôtel", "hébergement", "loger", "chambre", "auberge", "lodge", "campement"],
            "restauration": ["manger", "restaurant", "nourriture", "plat", "cuisine", "gastronomie", "spécialité", "repas"],
            "transport": ["déplacer", "transport", "taxi", "bus", "voiture", "location", "trajet", "aller", "voyage"],
            "prix": ["prix", "coût", "coûte", "tarif", "budget", "dépense", "combien"],
            "periode": ["période", "quand", "saison", "moment", "meilleur", "climat", "météo", "temps"],
            "activites": ["faire", "activité", "visite", "visiter", "découvrir", "excursion", "voir"],
            "site_touristique": ["site", "lieu", "endroit", "cascade", "parc", "monument", "ruine", "musée", "mosquée"]
        }

    def _is_greeting(self, query: str) -> bool:
        """Détecte si le message est une salutation"""
        greetings = ["bonjour", "salut", "hello", "hey", "bonsoir", "hi", "coucou"]
        return any(word in query.lower() for word in greetings)

    def _clean_text(self, text: str) -> str:
        """Nettoie le texte des balises et caractères superflus"""
        # Supprimer les balises HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normaliser les espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les tirets répétés
        text = re.sub(r'[-_]{3,}', '', text)
        
        # Réduire les sauts de ligne multiples
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()

    def _detect_question_category(self, query: str) -> Optional[str]:
        """Identifie la catégorie de la question"""
        query_lower = query.lower()
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            logger.info(f"Catégorie détectée: {best_category} (score: {category_scores[best_category]})")
            return best_category
        
        return None

    def _deduplicate_results(self, documents: List[str], metadatas: List[Dict]) -> List[str]:
        """Élimine les doublons dans les résultats"""
        seen_names = set()
        unique_docs = []
        
        for doc, meta in zip(documents, metadatas):
            # Identifier l'élément unique
            name = meta.get('nom', '')
            
            # Éviter les doublons
            if name and name in seen_names:
                continue
                
            # Nettoyer les répétitions de lignes
            lines = doc.split('\n')
            cleaned_lines = []
            seen_lines = set()
            
            for line in lines:
                line_clean = line.strip().lower()
                if line_clean and line_clean not in seen_lines:
                    cleaned_lines.append(line)
                    seen_lines.add(line_clean)
            
            cleaned_doc = '\n'.join(cleaned_lines)
            
            if name:
                seen_names.add(name)
            unique_docs.append(cleaned_doc)
        
        return unique_docs

    def _extract_ville_from_query(self, query: str) -> str:
        """Extrait le nom de ville mentionné dans la question"""
        villes = ["ouagadougou", "banfora", "bobo-dioulasso", "bobo", "ouaga"]
        for ville in villes:
            if ville in query.lower():
                if ville == "ouaga":
                    return "Ouagadougou"
                elif ville == "bobo":
                    return "Bobo-Dioulasso"
                return ville.title()
        return ""

    def load_data(self):
        """Charge et indexe les données touristiques"""
        logger.info("Chargement des données touristiques...")
        
        documents = []
        metadatas = []
        ids = []
        
        if os.path.exists(self.config.DATA_JSON_PATH):
            with open(self.config.DATA_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            doc_id = 0
            
            # Traitement des sites touristiques
            if "sites_touristiques" in data:
                for site in data["sites_touristiques"]:
                    doc_text = self._format_site_info(site)
                    documents.append(doc_text)
                    metadatas.append({
                        "type": "site_touristique",
                        "nom": site.get("nom", ""),
                        "ville": site.get("ville", ""),
                        "region": site.get("region", ""),
                        "category": "site_touristique"
                    })
                    ids.append(f"site_{doc_id}")
                    doc_id += 1
                    
                    # Indexation des prix
                    if "prix" in site:
                        price_doc = f"Prix pour {site['nom']}: {site['prix']}. Tarifs d'entrée: {site['prix']}"
                        documents.append(price_doc)
                        metadatas.append({
                            "type": "prix",
                            "nom": site.get("nom", ""),
                            "ville": site.get("ville", ""),
                            "category": "prix"
                        })
                        ids.append(f"prix_{doc_id}")
                        doc_id += 1
                    
                    # Indexation des activités
                    if "activites" in site and site["activites"]:
                        activities_doc = f"Activités à {site['nom']}: {', '.join(site['activites'])}. Que faire: {', '.join(site['activites'])}"
                        documents.append(activities_doc)
                        metadatas.append({
                            "type": "activites",
                            "nom": site.get("nom", ""),
                            "ville": site.get("ville", ""),
                            "category": "activites"
                        })
                        ids.append(f"activites_{doc_id}")
                        doc_id += 1
            
            # Traitement des hébergements
            if "hebergements" in data:
                for hotel in data["hebergements"]:
                    doc_text = self._format_hotel_info(hotel)
                    documents.append(doc_text)
                    metadatas.append({
                        "type": "hebergement",
                        "nom": hotel.get("nom", ""),
                        "ville": hotel.get("ville", ""),
                        "categorie": hotel.get("categorie", ""),
                        "category": "hebergement"
                    })
                    ids.append(f"hotel_{doc_id}")
                    doc_id += 1
            
            # Traitement des restaurants
            if "restaurants" in data:
                for resto in data["restaurants"]:
                    doc_text = self._format_restaurant_info(resto)
                    documents.append(doc_text)
                    metadatas.append({
                        "type": "restaurant",
                        "nom": resto.get("nom", ""),
                        "ville": resto.get("ville", ""),
                        "cuisine": resto.get("cuisine", ""),
                        "category": "restauration"
                    })
                    ids.append(f"resto_{doc_id}")
                    doc_id += 1
            
            # Traitement des informations pratiques
            if "infos_pratiques" in data:
                for info in data["infos_pratiques"]:
                    doc_text = f"{info.get('categorie', '')}: {info.get('titre', '')}.\n{info.get('description', '')}"
                    documents.append(doc_text)
                    
                    categorie = info.get('categorie', '').lower()
                    if 'transport' in categorie:
                        cat = "transport"
                    elif 'climat' in categorie or 'saison' in categorie:
                        cat = "periode"
                    else:
                        cat = "pratique"
                    
                    metadatas.append({
                        "type": "info_pratique",
                        "categorie": info.get("categorie", ""),
                        "category": cat
                    })
                    ids.append(f"info_{doc_id}")
                    doc_id += 1
        
        # Chargement du fichier texte supplémentaire
        if os.path.exists(self.config.DATA_TXT_PATH):
            with open(self.config.DATA_TXT_PATH, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            chunks = self._split_text_with_categories(text_content)
            for i, (chunk, category) in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    "type": "text_chunk",
                    "source": "burkina_tourism_data.txt",
                    "chunk_id": i,
                    "category": category
                })
                ids.append(f"txt_chunk_{doc_id}")
                doc_id += 1
        
        if documents:
            logger.info(f"Indexation de {len(documents)} documents...")
            embeddings = self.embedding_model.encode(documents, show_progress_bar=True)
            embeddings_list = embeddings.tolist()
            
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                end_idx = min(i + batch_size, len(documents))
                self.collection.add(
                    embeddings=embeddings_list[i:end_idx],
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                    ids=ids[i:end_idx]
                )
            
            logger.info(f"✓ {len(documents)} documents indexés avec succès!")
        else:
            logger.warning("Aucune donnée trouvée à indexer!")

    def _split_text_with_categories(self, text: str) -> List[Tuple[str, str]]:
        """Découpe le texte en segments avec détection de catégorie"""
        chunks_with_categories = []
        sections = re.split(r'\n(?=[A-Z][A-Z\s]+\n[=]+)', text)
        
        for section in sections:
            category = "general"
            section_lower = section.lower()
            
            if any(word in section_lower for word in ["hébergement", "hôtel", "auberge"]):
                category = "hebergement"
            elif any(word in section_lower for word in ["restaurant", "gastronomie", "cuisine", "plat"]):
                category = "restauration"
            elif any(word in section_lower for word in ["transport", "déplacement", "taxi", "bus"]):
                category = "transport"
            elif any(word in section_lower for word in ["cascade", "parc", "site", "monument", "ruine"]):
                category = "site_touristique"
            elif any(word in section_lower for word in ["climat", "saison", "période"]):
                category = "periode"
            
            sentences = section.split('. ')
            current_chunk = ""
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) < self.config.CHUNK_SIZE:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks_with_categories.append((current_chunk.strip(), category))
                    current_chunk = sentence + ". "
            
            if current_chunk:
                chunks_with_categories.append((current_chunk.strip(), category))
        
        return chunks_with_categories

    def _format_site_info(self, site: Dict) -> str:
        """Formate les informations d'un site touristique"""
        parts = [
            f"📍 Site touristique : {site.get('nom', '')}",
            f"📌 Localisation : {site.get('ville', '')}, {site.get('region', '')}",
            f"📝 Description : {site.get('description', '')}",
            f"💰 Prix d'entrée : {site.get('prix', 'Non spécifié')}",
            f"🕐 Horaires : {site.get('horaires', 'Non spécifié')}",
            f"📅 Meilleure période : {site.get('meilleure_periode', 'Toute l\'année')}",
            f"⏱️ Durée de visite : {site.get('duree_visite', 'Variable')}"
        ]
        
        if site.get('activites'):
            parts.append(f"🎯 Activités : {', '.join(site['activites'])}")
        if site.get('conseils'):
            parts.append(f"💡 Conseils : {site['conseils']}")
        
        return "\n".join(parts)

    def _format_hotel_info(self, hotel: Dict) -> str:
        """Formate les informations d'un hébergement"""
        parts = [
            f"🏨 Hébergement : {hotel.get('nom', '')}",
            f"⭐ Type : {hotel.get('categorie', '')}",
            f"📍 Ville : {hotel.get('ville', '')}",
            f"💰 Prix par nuit : {hotel.get('prix_nuit', 'Variable')}"
        ]
        
        if hotel.get('telephone'):
            parts.append(f"📞 Contact : {hotel.get('telephone', '')}")
        
        if hotel.get('services'):
            parts.append(f"✨ Services : {', '.join(hotel['services'])}")
        
        return "\n".join(parts)

    def _format_restaurant_info(self, resto: Dict) -> str:
        """Formate les informations d'un restaurant"""
        parts = [
            f"🍽️ Restaurant : {resto.get('nom', '')}",
            f"👨‍🍳 Cuisine : {resto.get('cuisine', '')}",
            f"📍 Ville : {resto.get('ville', '')}",
            f"💰 Budget moyen : {resto.get('budget_moyen', 'Variable')}",
            f"🕐 Horaires : {resto.get('horaires', '')}"
        ]
        
        if resto.get('specialites'):
            parts.append(f"⭐ Spécialités : {', '.join(resto['specialites'])}")
        
        return "\n".join(parts)

    def search_similar_documents(self, query: str, n_results: int = None) -> Tuple[List[str], List[float]]:
        """Recherche les documents pertinents avec filtrage par catégorie"""
        if n_results is None:
            n_results = self.config.TOP_K_RESULTS
        
        try:
            detected_category = self._detect_question_category(query)
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Augmenter les résultats initiaux pour permettre la déduplication
            search_multiplier = 4
            
            # Recherche avec filtre de catégorie si applicable
            if detected_category:
                logger.info(f"Filtrage par catégorie: {detected_category}")
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results * search_multiplier,
                    where={"category": detected_category},
                    include=["documents", "metadatas", "distances"]
                )
                
                if not results['documents'][0]:
                    logger.info("Aucun résultat avec filtre, recherche sans filtre...")
                    results = self.collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results * 2,
                        include=["documents", "metadatas", "distances"]
                    )
            else:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results * 2,
                    include=["documents", "metadatas", "distances"]
                )
            
            if not results['documents'][0]:
                logger.warning("Aucun document trouvé dans la base")
                return [], []
            
            documents = results['documents'][0]
            distances = results['distances'][0]
            similarities = [1 - d for d in distances]
            metadatas = results['metadatas'][0]
            
            # Nettoyage des documents
            documents = [self._clean_text(doc) for doc in documents]
            
            # Filtrage par seuil de pertinence
            filtered_docs = []
            filtered_scores = []
            filtered_metas = []
            
            for doc, score, metadata in zip(documents, similarities, metadatas):
                if score >= self.config.SIMILARITY_THRESHOLD:
                    if detected_category:
                        doc_category = metadata.get('category', '')
                        if doc_category == detected_category or score > 0.45:
                            filtered_docs.append(doc)
                            filtered_scores.append(score)
                            filtered_metas.append(metadata)
                    else:
                        filtered_docs.append(doc)
                        filtered_scores.append(score)
                        filtered_metas.append(metadata)
            
            if not filtered_docs and documents:
                logger.info("Aucun document au-dessus du seuil, utilisation des meilleurs résultats")
                filtered_docs = documents[:n_results]
                filtered_scores = similarities[:n_results]
                filtered_metas = metadatas[:n_results]
            
            # Déduplication
            unique_docs = self._deduplicate_results(filtered_docs, filtered_metas)
            
            if self.config.DEBUG:
                logger.info(f"Query: {query}")
                logger.info(f"Catégorie détectée: {detected_category}")
                logger.info(f"Documents trouvés: {len(unique_docs)}")
            
            return unique_docs[:n_results], filtered_scores[:len(unique_docs[:n_results])]
        
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {e}")
            return [], []

    def generate_response(self, query: str, context: List[str]) -> str:
        """Génère une réponse structurée à partir du contexte"""
        
        # Traitement des salutations
        if self._is_greeting(query):
            return """👋 Bonjour ! Je suis votre assistant touristique pour le Burkina Faso.

Je peux vous aider à :
- Découvrir les sites touristiques
- Trouver un hébergement
- Vous renseigner sur la gastronomie
- Planifier votre voyage

Que souhaitez-vous savoir ?"""
        
        if not context:
            return self._generate_fallback_response(query)
        
        # Identification du type de question
        detected_category = self._detect_question_category(query)
        
        # Traitement spécifique pour le transport
        if detected_category == "transport":
            return self._format_transport_response(context)
        
        # Limitation du contexte pour éviter les réponses trop longues
        max_items = 2 if detected_category in ["hebergement", "restauration"] else 3
        context_items = context[:max_items]
        
        # Génération de la réponse selon la catégorie
        if detected_category == "hebergement":
            return self._format_hebergement_response(context_items, query)
        elif detected_category == "restauration":
            return self._format_restauration_response(context_items, query)
        elif detected_category == "prix":
            return self._format_prix_response(context_items, query)
        elif detected_category == "periode":
            return self._format_periode_response(context_items, query)
        elif detected_category == "site_touristique":
            return self._format_site_response(context_items, query)
        else:
            return self._format_general_response(context_items)

    def _format_hebergement_response(self, context: List[str], query: str) -> str:
        """Formate une réponse pour les hébergements"""
        ville = self._extract_ville_from_query(query)
        intro = f"🏨 Hébergements à {ville} :" if ville else "🏨 Hébergements recommandés :"
        
        formatted = [intro, ""]
        for item in context:
            # Extraction des informations essentielles
            lines = item.split('\n')
            essential = [l for l in lines if any(x in l for x in ['🏨', '⭐', '📍', '💰', '📞'])]
            formatted.append('\n'.join(essential[:5]))
            formatted.append("")
        
        formatted.append("💡 Besoin d'autres détails ? Demandez-moi !")
        return '\n'.join(formatted)

    def _format_restauration_response(self, context: List[str], query: str) -> str:
        """Formate une réponse pour la restauration"""
        ville = self._extract_ville_from_query(query)
        
        # Réponse spécifique pour les plats typiques
        if any(word in query.lower() for word in ["manger", "plat", "cuisine", "gastronomie"]):
            intro = (
                "🍽️ **Plats typiques burkinabè** :\n"
                "\n"
                "• **Tô** : Pâte de mil ou maïs accompagnée de sauce\n"
                "• **Riz gras** : Riz cuit avec viande et légumes\n"
                "• **Poulet bicyclette** : Poulet local grillé\n"
                "• **Brochettes** : Viande grillée sur brochettes\n"
                "• **Dolo** : Bière de mil traditionnelle\n"
                "\n"
                "**Où manger à Ouagadougou :**"
            )
            
            formatted = [intro, ""]
            
            # Recherche de restaurants dans le contexte
            restaurant_found = False
            for item in context:
                if any(x in item for x in ['🍽️', 'Restaurant', 'Cuisine']):
                    lines = item.split('\n')
                    essential = [l for l in lines if any(x in l for x in ['🍽️', '👨‍🍳', '📍', '💰'])]
                    if essential:
                        formatted.append('\n'.join(essential[:4]))
                        formatted.append("")
                        restaurant_found = True
            
            # Ajout de restaurants par défaut si nécessaire
            if not restaurant_found:
                formatted.append("🍽️ Restaurant : Le Gondwana")
                formatted.append("👨‍🍳 Cuisine : Internationale et Burkinabè")
                formatted.append("📍 Ville : Ouagadougou")
                formatted.append("💰 Budget moyen : 10,000 - 20,000 FCFA")
                formatted.append("")
                formatted.append("🍽️ Restaurant : Maquis Chez Tantie")
                formatted.append("👨‍🍳 Cuisine : Locale")
                formatted.append("📍 Ville : Ouagadougou")
                formatted.append("💰 Budget moyen : 2,000 - 5,000 FCFA")
                formatted.append("")
            
            formatted.append("💡 Pour d'autres villes, demandez-moi !")
            return '\n'.join(formatted)
        else:
            intro = f"🍽️ Restaurants à {ville} :" if ville else "🍽️ Restaurants recommandés :"
            formatted = [intro, ""]
            
            for item in context:
                lines = item.split('\n')
                essential = [l for l in lines if any(x in l for x in ['🍽️', '👨‍🍳', '📍', '💰'])]
                if essential:
                    formatted.append('\n'.join(essential[:4]))
                    formatted.append("")
            
            if len(formatted) <= 2:
                formatted.append("💡 Spécifiez une ville (Ouagadougou, Banfora, Bobo-Dioulasso) !")
            
            return '\n'.join(formatted)
    
    def _format_prix_response(self, context: List[str], query: str) -> str:
        """Formate une réponse pour les tarifs"""
        formatted = ["💰 Tarifs :", ""]
        
        for item in context:
            # Extraction des lignes de prix
            lines = item.split('\n')
            price_lines = [l for l in lines if any(x in l.lower() for x in ['💰', 'prix', 'fcfa', 'tarif'])]
            
            if price_lines:
                # Ajout du nom de l'établissement
                name_line = next((l for l in lines if any(x in l for x in ['📍', '🏨', '🍽️', 'Site', 'Hébergement', 'Restaurant'])), '')
                if name_line:
                    formatted.append(name_line)
                formatted.extend(price_lines[:2])
                formatted.append("")
        
        # Ajout d'informations sur le budget global si pertinent
        if any(word in query.lower() for word in ["séjour", "voyage", "budget global", "coûte un"]):
            formatted.append("💡 **Budget estimé pour un séjour** :")
            formatted.append("• Économique : 20,000-35,000 FCFA/jour")
            formatted.append("• Confort moyen : 40,000-70,000 FCFA/jour")
            formatted.append("• Haut de gamme : 100,000+ FCFA/jour")
        
        return '\n'.join(formatted)

    def _format_periode_response(self, context: List[str], query: str) -> str:
        """Formate une réponse sur la période de visite"""
        formatted = ["📅 **Meilleure période pour visiter le Burkina Faso** :", ""]
        
        formatted.append("🌤️ **Saison sèche (octobre à mai)** - RECOMMANDÉE")
        formatted.append("   • Idéale pour le tourisme")
        formatted.append("   • Températures : 25-35°C")
        formatted.append("   • Meilleure période : novembre à février (plus frais)")
        formatted.append("")
        formatted.append("🌧️ **Saison des pluies (juin à septembre)**")
        formatted.append("   • Cascades au débit maximal")
        formatted.append("   • Températures : 20-30°C")
        formatted.append("   • Paysages verdoyants")
        formatted.append("")
        formatted.append("💡 **Conseil** : Privilégiez novembre-février pour un climat agréable !")
        
        return '\n'.join(formatted)

    def _format_transport_response(self, context: List[str]) -> str:
        """Formate une réponse sur les moyens de transport"""
        formatted = ["🚗 **Comment se déplacer au Burkina Faso** :", ""]
        
        formatted.append("✈️ **Avion**")
        formatted.append("   • Aéroport : Ouagadougou (international)")
        formatted.append("   • Compagnies : Air France, Brussels Airlines, Ethiopian Airlines")
        formatted.append("   • Vol intérieur : Ouaga ↔ Bobo-Dioulasso (Air Burkina)")
        formatted.append("")
        
        formatted.append("🚌 **Bus interurbain**")
        formatted.append("   • Ouaga → Bobo : 4h, 5,000 FCFA")
        formatted.append("   • Ouaga → Banfora : 6h, 7,000 FCFA")
        formatted.append("   • Compagnies : STMB, TSR, TCV, Rakieta")
        formatted.append("")
        
        formatted.append("🚕 **Taxi en ville**")
        formatted.append("   • Course : 1,000-3,000 FCFA selon distance")
        formatted.append("   • Toujours négocier le prix avant")
        formatted.append("")
        
        formatted.append("🚙 **Location de voiture**")
        formatted.append("   • Avec chauffeur : 40,000-80,000 FCFA/jour")
        formatted.append("   • Recommandé pour visiter plusieurs sites")
        formatted.append("")
        
        formatted.append("💡 **Conseil** : Réservez les bus à l'avance en haute saison !")
        
        return '\n'.join(formatted)

    def _format_site_response(self, context: List[str], query: str) -> str:
        """Formate une réponse pour les sites touristiques"""
        formatted = ["🏞️ Sites touristiques recommandés :", ""]
        for item in context:
            lines = item.split('\n')
            # Sélection des informations clés
            essential = []
            for l in lines:
                if any(x in l for x in ['📍 Site', '📌 Localisation', '💰 Prix', '📅 Meilleure']):
                    essential.append(l)
                elif '📝 Description' in l:
                    # Raccourcissement de la description
                    desc = l.replace('📝 Description : ', '')
                    if len(desc) > 150:
                        desc = desc[:150] + "..."
                    essential.append(f"📝 {desc}")
            
            formatted.extend(essential[:5])
            formatted.append("")
        
        formatted.append("💡 Pour plus de détails, demandez-moi !")
        return '\n'.join(formatted)

    def _format_general_response(self, context: List[str]) -> str:
        """Formate une réponse générale"""
        # Limitation à 2 éléments de contexte
        formatted_context = '\n\n'.join(context[:2])
        
        return f"""Voici ce que j'ai trouvé :

{formatted_context}

━━━━━━━━━━━━━━

💡 Besoin de précisions ? Demandez-moi !"""

    def _generate_fallback_response(self, query: str) -> str:
        """Génère une réponse par défaut"""
        return f"""Je n'ai pas trouvé d'informations spécifiques sur "{query}".

Je peux vous aider avec :
- Sites touristiques du Burkina Faso
- Hébergements à Ouagadougou, Banfora, Bobo-Dioulasso
- Gastronomie locale
- Meilleures périodes pour visiter
- Transports et déplacements

Reformulez votre question ou choisissez un sujet !"""

    def chat(self, query: str) -> str:
        """Fonction principale d'interaction"""
        try:
            documents, scores = self.search_similar_documents(query)
            response = self.generate_response(query, documents)
            return response
        except Exception as e:
            logger.error(f"Erreur dans chat(): {e}")
            return f"Désolé, une erreur s'est produite : {str(e)}"

    def reset_database(self):
        """Réinitialise la base de données"""
        try:
            self.chroma_client.delete_collection(name=self.config.COLLECTION_NAME)
            self.collection = self.chroma_client.create_collection(
                name=self.config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            self.load_data()
            logger.info("Base de données réinitialisée avec succès!")
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation: {e}")


# Tests du chatbot
if __name__ == "__main__":
    print("Initialisation du chatbot...")
    chatbot = BurkinaChatbot()

    test_queries = [
        "Bonjour",
        "Quels sont les sites touristiques incontournables ?",
        "Où dormir à Ouagadougou ?",
        "Quel est le prix d'entrée aux cascades ?",
        "Que peut-on manger au Burkina Faso ?",
        "Quelle est la meilleure période pour visiter ?",
        "Comment se déplacer dans le pays ?",
        "Quelles sont les cascades à voir ?",
        "Y a-t-il des parcs nationaux ?",
        "Combien coûte un séjour touristique ?",
    ]

    print("\n" + "="*50)
    print("TEST DU CHATBOT BURKINA TOURISME")
    print("="*50)

    for query in test_queries:
        print(f"\n👤 Question: {query}")
        response = chatbot.chat(query)
        print(f"🤖 Réponse: {response}")
        print("-" * 50)