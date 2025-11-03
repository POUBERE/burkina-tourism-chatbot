# Guide de Démarrage Rapide

## Installation en 5 minutes

### Étape 1 : Cloner le projet

```bash
git clone https://github.com/POUBERE/burkina-tourism-chatbot.git
cd burkina-tourism-chatbot
```

### Étape 2 : Créer l'environnement virtuel

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Étape 3 : Installer les dépendances

```bash
pip install -r requirements.txt
```

**Note:** L'installation peut prendre 5-10 minutes (téléchargement des packages).

### Étape 4 : Configuration

1. Copier le fichier de configuration :

```bash
cp .env.example .env
```

2. Obtenir un token Hugging Face (GRATUIT) :

      - Créer un compte sur https://huggingface.co
      - Aller dans Settings → Access Tokens
      - Créer un token (type: Read)
      - Copier le token

3. Éditer le fichier `.env` et remplacer :

```
HUGGINGFACE_API_TOKEN=hf_votre_token_ici
```

### Étape 5 : Collecter les données

```bash
python scrape_data.py
```

Cela va créer les fichiers `data/burkina_tourism_data.json` et `data/burkina_tourism_data.txt`.

### Étape 6 : Tester le chatbot (ligne de commande)

```bash
python burkina_chatbot.py
```

Posez quelques questions pour vérifier que tout fonctionne.

### Étape 7 : Lancer l'application web

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à `http://localhost:8501`.

## Vérification de l'installation

Exécuter les tests :

```bash
python test_chatbot.py
```

Tous les tests doivent passer (score 100%).

## Problèmes Courants

### Erreur : "No module named 'chromadb'"

**Solution :** `pip install chromadb`

### Erreur : "HUGGINGFACE_API_TOKEN not found"

**Solution :** Vérifier que le token est bien dans le fichier `.env`

### Le chatbot est lent

**Normal :** Le premier chargement prend 30-60 secondes (téléchargement des modèles).
Les réponses suivantes seront rapides (2-5 secondes).

### Erreur compilation hnswlib

**Solution :** Commenter la ligne `hnswlib` dans `requirements.txt`, ChromaDB utilisera une alternative.

## Commandes Utiles

**Lancer l'app :**

```bash
streamlit run app.py
```

**Lancer en mode développement (hot reload) :**

```bash
streamlit run app.py --server.runOnSave true
```

**Tester le chatbot en CLI :**

```bash
python burkina_chatbot.py
```

**Recréer les données :**

```bash
python scrape_data.py
```

**Exécuter les tests :**

```bash
python test_chatbot.py
```

## Prochaines Étapes

1. Tester le chatbot avec diverses questions
2. Personnaliser l'interface dans `app.py`
3. Ajouter plus de données dans `scrape_data.py`
4. Déployer en ligne sur Streamlit Cloud

## Besoin d'aide ?

- Consulter le README.md complet
- Vérifier les logs d'erreur
- Relancer les tests avec `python test_chatbot.py`

Bon développement !
