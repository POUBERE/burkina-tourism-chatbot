"""
Interface Streamlit pour le chatbot touristique du Burkina Faso
"""

import streamlit as st
from datetime import datetime
import logging
from burkina_chatbot import BurkinaChatbot
from config import Config
import random

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Streamlit
st.set_page_config(
    page_title="Burkina Faso - Guide Touristique",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_css():
    """Charge les styles CSS personnalisés"""
    st.markdown("""
    <style>
    /* Style global */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    /* Messages de chat */
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        animation: fadeIn 0.5s;
        white-space: pre-wrap;
        line-height: 1.6;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Boutons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Cartes d'information */
    .info-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Cartes de métriques */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
                
    /* Style pour bouton d'envoi */
    .stForm button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        font-size: 1.5rem;
        font-weight: bold;
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .stForm button[kind="primary"]:hover {
        transform: scale(1.1);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
                
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initialise les variables de session"""
    if 'chatbot' not in st.session_state:
        with st.spinner("🚀 Initialisation du chatbot..."):
            try:
                st.session_state.chatbot = BurkinaChatbot()
                st.session_state.initialized = True
            except Exception as e:
                st.error(f"Erreur lors de l'initialisation: {e}")
                st.session_state.initialized = False

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'conversation_count' not in st.session_state:
        st.session_state.conversation_count = 0

    if 'feedback' not in st.session_state:
        st.session_state.feedback = {}


def display_header():
    """Affiche l'en-tête de l'application"""
    st.markdown("""
    <div class="main-header">
        <h1>🌍 Burkina Faso - Assistant Touristique</h1>
        <p style="font-size: 1.2rem;">Découvrez le Pays des Hommes Intègres</p>
        <p>Votre guide personnalisé pour explorer le Burkina Faso 🇧🇫</p>
    </div>
    """, unsafe_allow_html=True)


def display_sidebar():
    """Affiche le menu latéral avec les options"""
    with st.sidebar:
        st.markdown("## 🎯 Navigation")

        # Guide d'utilisation
        st.markdown("""
        <div class="info-card">
            <h3>💡 Comment utiliser ce chatbot ?</h3>
            <ul>
                <li>Posez vos questions sur le tourisme au Burkina Faso</li>
                <li>Découvrez les sites touristiques</li>
                <li>Trouvez des hébergements</li>
                <li>Explorez la gastronomie locale</li>
                <li>Obtenez des conseils pratiques</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Questions prédéfinies
        st.markdown("### 🤔 Questions suggérées")
        suggestions = [
            "Quels sont les sites touristiques incontournables ?",
            "Où dormir à Ouagadougou ?",
            "Que peut-on manger au Burkina Faso ?",
            "Quelle est la meilleure période pour visiter ?",
            "Comment se déplacer dans le pays ?",
            "Quelles sont les cascades à voir ?",
            "Y a-t-il des parcs nationaux ?",
            "Combien coûte un séjour touristique ?"
        ]

        for suggestion in suggestions:
            if st.button(f"💬 {suggestion}", key=f"sugg_{suggestion[:20]}"):
                process_user_query(suggestion)
                st.rerun()

        # Statistiques d'utilisation
        st.markdown("### 📊 Statistiques")
        
        user_message_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                <h3 style="margin: 0;">💬</h3>
                <p style="margin: 0; font-size: 1.5rem; font-weight: bold;">{user_message_count}</p>
                <p style="margin: 0; font-size: 0.8rem;">Messages</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            if hasattr(st.session_state, 'chatbot') and st.session_state.initialized:
                doc_count = st.session_state.chatbot.collection.count()
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                    <h3 style="margin: 0;">📄</h3>
                    <p style="margin: 0; font-size: 1.5rem; font-weight: bold;">{doc_count}</p>
                    <p style="margin: 0; font-size: 0.8rem;">Documents</p>
                </div>
                """, unsafe_allow_html=True)

        # Paramètres avancés
        with st.expander("⚙️ Options avancées"):
            # Affichage des messages de confirmation
            if 'reset_success' in st.session_state and st.session_state.reset_success:
                st.success("✅ Conversation réinitialisée!")
                st.session_state.reset_success = False
            
            if 'reload_success' in st.session_state and st.session_state.reload_success:
                st.success("✅ Base de données rechargée!")
                st.session_state.reload_success = False
            
            if st.button("🔄 Réinitialiser la conversation"):
                st.session_state.messages = []
                st.session_state.conversation_count = 0
                st.session_state.feedback = {}
                st.session_state.reset_success = True
                st.rerun()

            if st.button("🗄️ Recharger la base de données"):
                with st.spinner("Rechargement en cours..."):
                    if st.session_state.initialized:
                        st.session_state.chatbot.reset_database()
                        st.session_state.reload_success = True
                        st.rerun()

            # Mode débogage
            debug_mode = st.checkbox("🐛 Mode Debug", value=Config.DEBUG)
            if st.session_state.initialized:
                st.session_state.chatbot.config.DEBUG = debug_mode

        # Anecdotes sur le Burkina Faso
        st.markdown("### 🌍 Le saviez-vous ?")
        facts = [
            "Le Burkina Faso signifie 'Pays des Hommes Intègres'",
            "La capitale est Ouagadougou",
            "Le pays compte plus de 60 ethnies",
            "Le FESPACO est le plus grand festival de cinéma africain",
            "Les Mossi constituent l'ethnie majoritaire"
        ]
        st.info(random.choice(facts))

        # Pied de page
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; opacity: 0.7;">
            <p>Créé avec ❤️ pour découvrir le Burkina Faso</p>
            <p style="font-size: 0.8rem;">© 2024 - Projet Data Science</p>
        </div>
        """, unsafe_allow_html=True)


def process_user_query(user_input: str):
    """Traite la question de l'utilisateur"""
    if not st.session_state.initialized:
        st.error("❌ Le chatbot n'est pas encore initialisé. Veuillez patienter...")
        return

    # Enregistrement de la question
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    st.session_state.conversation_count += 1
    
    logger.info(f"Message {st.session_state.conversation_count} traité")

    # Génération de la réponse
    with st.spinner("🤔 Je réfléchis..."):
        try:
            response = st.session_state.chatbot.chat(user_input)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
            
            user_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
            logger.info(f"Total messages utilisateur: {user_count}")

        except Exception as e:
            logger.error(f"Erreur lors de la génération de réponse: {e}")
            st.error(f"❌ Erreur: {e}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Désolé, j'ai rencontré une erreur. Pouvez-vous reformuler votre question ?",
                "timestamp": datetime.now().strftime("%H:%M")
            })


def display_chat_messages():
    """Affiche l'historique de la conversation"""
    for idx, message in enumerate(st.session_state.messages):
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", "")

        if role == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <b>👤 Vous ({timestamp})</b><br>
                {content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <b>🤖 Assistant ({timestamp})</b><br>
                {content}
            </div>
            """, unsafe_allow_html=True)

            # Système de feedback
            col1, col2, col3 = st.columns([1, 1, 8])
            msg_id = f"{idx}_{timestamp}"
            safe_msg_id = str(msg_id).replace(":", "_").replace(" ", "_")

            with col1:
                if st.button("👍", key=f"like_{safe_msg_id}"):
                    st.session_state.feedback[safe_msg_id] = "positive"
                    st.toast("✅ Merci pour votre retour !", icon="👍")

            with col2:
                if st.button("👎", key=f"dislike_{safe_msg_id}"):
                    st.session_state.feedback[safe_msg_id] = "negative"
                    st.toast("📝 Merci, nous allons nous améliorer !", icon="👎")


def main():
    """Point d'entrée principal de l'application"""
    load_css()
    init_session_state()
    display_header()
    display_sidebar()

    # Interface de chat
    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        if st.session_state.messages:
            display_chat_messages()
        else:
            st.markdown("""
            <div class="info-card" style="text-align: center;">
                <h2>👋 Bienvenue!</h2>
                <p>Je suis votre assistant touristique pour découvrir le Burkina Faso.</p>
                <p>Posez-moi vos questions ou utilisez les suggestions dans la barre latérale.</p>
                <br>
                <p><b>Exemples de questions:</b></p>
                <ul style="text-align: left; max-width: 500px; margin: auto;">
                    <li>Quels sont les sites touristiques à visiter ?</li>
                    <li>Où puis-je dormir à Banfora ?</li>
                    <li>Quel est le prix d'entrée au parc d'Arly ?</li>
                    <li>Que peut-on manger de typique ?</li>
                    <li>Quelles sont les cascades à voir ?</li>
                    <li>Y a-t-il des parcs nationaux ?</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Formulaire de saisie
        with st.form(key="chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])

            with col1:
                user_input = st.text_input(
                    "Votre question:",
                    placeholder="Tapez votre question ici...",
                    label_visibility="collapsed"
                )

            with col2:
                submit = st.form_submit_button("🚀", use_container_width=True, type="primary")

            if submit and user_input:
                process_user_query(user_input)
                st.rerun()

    # Indicateurs de statut
    with col3:
        if st.session_state.initialized:
            st.markdown("""
            <div class="metric-card">
                <p>✅ Chatbot Actif</p>
            </div>
            """, unsafe_allow_html=True)

            user_message_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
            if user_message_count > 0:
                st.markdown(f"""
                <div class="metric-card">
                    <p>💬 {user_message_count} message{'s' if user_message_count > 1 else ''}</p>
                </div>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()