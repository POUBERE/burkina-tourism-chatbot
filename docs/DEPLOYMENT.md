# Guide de Déploiement

Ce guide explique comment déployer le chatbot en ligne gratuitement.

## Option 1 : Streamlit Cloud (Recommandé)

### Avantages

- ✅ Gratuit
- ✅ Déploiement simple
- ✅ Intégration GitHub native
- ✅ SSL automatique
- ✅ CI/CD automatique

### Étapes de déploiement

**1. Préparer le repository GitHub**

```bash
# Initialiser Git si pas encore fait
git init
git add .
git commit -m "Initial commit - Chatbot Burkina Faso"

# Créer repository sur GitHub et pusher
git remote add origin https://github.com/POUBERE/burkina-tourism-chatbot.git
git push -u origin main
```

**2. Créer un compte Streamlit Cloud**

- Aller sur https://share.streamlit.io
- Se connecter avec GitHub
- Autoriser l'accès à vos repositories

**3. Déployer l'application**

- Cliquer sur "New app"
- Sélectionner votre repository
- Choisir la branche : `main`
- Fichier principal : `app.py`
- Cliquer sur "Deploy"

**4. Configurer les secrets**

- Aller dans Settings → Secrets
- Ajouter votre token Hugging Face :

```toml
HUGGINGFACE_API_TOKEN = "hf_votre_token_ici"
```

**5. URL de l'application**

Votre app sera accessible à :

```
https://votre-username-burkina-tourism-chatbot-app-xxxxx.streamlit.app
```

### Personnaliser l'URL (optionnel)

Dans les paramètres Streamlit Cloud, vous pouvez :

- Changer le nom de l'app
- Ajouter un domaine personnalisé

---

## Option 2 : Hugging Face Spaces

### Avantages

- ✅ Gratuit
- ✅ Communauté IA
- ✅ GPU disponible (gratuit)
- ✅ Simple

### Étapes

**1. Créer un Space**

- Aller sur https://huggingface.co/spaces
- Cliquer sur "Create new Space"
- Nom : `burkina-tourism-chatbot`
- SDK : Streamlit
- Visibilité : Public

**2. Uploader les fichiers**

Soit via l'interface web, soit avec Git :

```bash
git remote add hf https://huggingface.co/spaces/votre-username/burkina-tourism-chatbot
git push hf main
```

**3. Configurer les secrets**

Créer un fichier `.streamlit/secrets.toml` dans le Space :

```toml
HUGGINGFACE_API_TOKEN = "hf_votre_token_ici"
```

**4. Accéder à l'application**

URL : `https://huggingface.co/spaces/votre-username/burkina-tourism-chatbot`

---

## Option 3 : Render.com

### Avantages

- Gratuit (plan Free)
- Support Docker
- Plus de contrôle

### Étapes

**1. Créer un compte**

- Aller sur https://render.com
- S'inscrire gratuitement

**2. Créer un Web Service**

- Dashboard → New → Web Service
- Connecter votre repository GitHub

**3. Configuration**

```
Name: burkina-tourism-chatbot
Environment: Python
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**4. Variables d'environnement**

Ajouter dans "Environment" :

```
HUGGINGFACE_API_TOKEN=hf_votre_token_ici
```

**5. Déployer**

- Cliquer sur "Create Web Service"
- Attendre 5-10 minutes

---

## Option 4 : Hébergement Local (Démonstration)

Pour présenter localement sans internet :

**1. Installer les dépendances**

```bash
pip install -r requirements.txt
```

**2. Télécharger les modèles à l'avance**

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
model.save('./models/embeddings')
```

**3. Lancer l'app**

```bash
streamlit run app.py
```

**4. Accès réseau local**

```bash
streamlit run app.py --server.address=0.0.0.0
```

Accessible depuis autres appareils sur le même réseau : `http://votre-ip:8501`

---

## Checklist Pré-Déploiement

Avant de déployer, vérifier :

- [ ] Tous les fichiers sont commitées sur Git
- [ ] `.env` est dans `.gitignore` (ne pas commiter les secrets!)
- [ ] `.env.example` est présent avec des exemples
- [ ] `requirements.txt` est à jour
- [ ] Les données sont dans `data/`
- [ ] Les tests passent (`python test_chatbot.py`)
- [ ] L'app fonctionne localement
- [ ] Token Hugging Face est valide

---

## Configuration des Secrets (Sécurité)

### Streamlit Cloud

Fichier `.streamlit/secrets.toml` (NE PAS COMMITER) :

```toml
HUGGINGFACE_API_TOKEN = "hf_xxxxx"
```

Dans le code, accéder avec :

```python
import streamlit as st
token = st.secrets.get("HUGGINGFACE_API_TOKEN", "")
```

### Render / Autres plateformes

Utiliser les variables d'environnement de la plateforme.

---

## Optimisations pour Production

### 1. Caching Streamlit

Déjà implémenté dans `app.py` :

```python
@st.cache_resource
def load_chatbot():
    return BurkinaTourismChatbot()
```

### 2. Réduire l'utilisation mémoire

Dans `requirements.txt`, utiliser :

```
torch==2.1.0+cpu  # Version CPU uniquement
```

### 3. Compression des données

Si les données deviennent volumineuses, compresser :

```python
import gzip
import json

with gzip.open('data.json.gz', 'wt', encoding='utf-8') as f:
    json.dump(data, f)
```

### 4. Monitoring

Ajouter Google Analytics dans `app.py` :

```python
# Dans le <head>
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
""", unsafe_allow_html=True)
```

---

## Dépannage Déploiement

### Erreur : "Module not found"

**Solution :** Vérifier que toutes les dépendances sont dans `requirements.txt`

```bash
pip freeze > requirements.txt
```

### Erreur : "Out of memory"

**Solution :** Utiliser un modèle plus léger

```python
LLM_MODEL = "google/flan-t5-base"  # Au lieu de large
```

### L'application ne démarre pas

**Vérifier les logs :**

- Streamlit Cloud : App → Manage app → Logs
- Render : Dashboard → Logs
- Hugging Face : Onglet "Logs"

### Erreur : "ChromaDB persistence"

Sur certaines plateformes, la persistence peut échouer.

**Solution :** Utiliser in-memory uniquement :

```python
vectorstore = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings
    # Pas de persist_directory
)
```

---

## Performance et Limites

### Streamlit Cloud (Plan Free)

- CPU : Partagé
- RAM : 1 GB
- Limite : ~1000 visites/mois
- Inactivité : Sleep après 7 jours sans visite

### Hugging Face Spaces (Free)

- CPU : Partagé
- RAM : 16 GB
- GPU : Disponible (T4)
- Limite : Pas de limite stricte

### Render (Plan Free)

- CPU : Partagé
- RAM : 512 MB
- Limite : 750h/mois
- Inactivité : Sleep après 15 min

---

## URLs Utiles

- **Streamlit Cloud :** https://share.streamlit.io
- **Hugging Face Spaces :** https://huggingface.co/spaces
- **Render :** https://render.com
- **Documentation Streamlit :** https://docs.streamlit.io
- **Support Hugging Face :** https://discuss.huggingface.co

---

## Mise à jour de l'application déployée

### Via Git (automatique)

```bash
git add .
git commit -m "Mise à jour des données"
git push origin main
```

L'application se redéploie automatiquement (CI/CD).

### Mise à jour manuelle des données

1. Exécuter localement : `python scrape_data.py`
2. Commiter les nouveaux fichiers data/
3. Pusher sur GitHub

---

## Domaine Personnalisé

### Streamlit Cloud

Ne supporte pas les domaines personnalisés sur le plan gratuit.

**Alternative :** Utiliser un service de redirection comme bit.ly

### Render

Supporte les domaines personnalisés :

1. Acheter un domaine (ex: burkinatourism.com)
2. Dans Render : Settings → Custom Domain
3. Configurer les DNS

---

## Backup et Sauvegarde

### Sauvegarder régulièrement :

- Code source (Git)
- Données (`data/`)
- Base vectorielle (`chroma_db/`)

### Script de backup

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup_$DATE.tar.gz data/ chroma_db/
```

---

## Support et Communauté

- **Issues GitHub :** Pour bugs et suggestions
- **Discord Streamlit :** https://discuss.streamlit.io
- **Forum Hugging Face :** https://discuss.huggingface.co

---

Bon déploiement !
