# Organisation de l'Équipe - Projet Chatbot Burkina Faso

## 👥 Membres de l'Équipe (4 personnes)

### POUBERE Abdourazakou - Chef de Projet & Développeur IA

**Rôle principal:** Coordination générale et développement du moteur RAG

**Responsabilités:**

- Coordination et gestion du projet
- Architecture RAG et chatbot (`burkina_chatbot.py`)
- Configuration centralisée (`config.py`)
- Documentation principale (README, final_summary)
- Gestion du repository GitHub
- Intégration des composants

**Fichiers GitHub:**

- `burkina_chatbot.py` ⭐ (fichier principal)
- `config.py`
- `README.md`
- `final_summary.md`
- `.env.example`
- `.gitignore`

**Compétences développées:**

- Architecture RAG (Retrieval Augmented Generation)
- LangChain et ChromaDB
- Gestion de projet agile
- Leadership technique

---

### OUEDRAOGO Lassina - Développeur Frontend & Déploiement

**Rôle principal:** Interface utilisateur et mise en production

**Responsabilités:**

- Interface Streamlit (`app.py`)
- Design UX/UI et CSS personnalisé
- Déploiement sur Streamlit Cloud
- Configuration de l'environnement
- Scripts d'installation automatique
- Guide de démarrage rapide

**Fichiers GitHub:**

- `app.py` ⭐ (interface principale)
- `requirements.txt`
- `setup.py`
- `run.py`
- `docs/QUICKSTART.md`

**Compétences développées:**

- Streamlit framework
- UI/UX design
- DevOps et déploiement cloud
- CSS/HTML

---

### COMPAORE Abdoul Bassy Oumar - Développeur Data & Collecte

**Rôle principal:** Collecte et structuration des données

**Responsabilités:**

- Collecte des données touristiques
- Web scraping (`scrape_data.py`)
- Structuration JSON et texte
- Vérification et validation des données
- Présentation PowerPoint
- Documentation de l'équipe

**Fichiers GitHub:**

- `scrape_data.py`
- `data/burkina_tourism_data.json`
- `data/burkina_tourism_data.txt`
- `docs/presentation.md`
- `docs/TEAM_ORGANIZATION.md`

**Compétences développées:**

- Web scraping (BeautifulSoup, Requests)
- Gestion de données JSON
- Structuration d'informations
- Présentation professionnelle

---

### SOMDO Marcelin - Développeur Testing & Documentation

**Rôle principal:** Tests, validation et documentation technique

**Responsabilités:**

- Tests unitaires et fonctionnels (`test_chatbot.py`)
- Validation de la qualité
- Rapport de projet complet
- Guide de déploiement
- Documentation technique
- Configuration VS Code

**Fichiers GitHub:**

- `test_chatbot.py`
- `docs/rapport.md`
- `docs/DEPLOYMENT.md`
- `.vscode/settings.json`

**Compétences développées:**

- Tests unitaires Python (pytest)
- Documentation technique
- Assurance qualité
- Méthodologie de test

---

## 📅 Planning Détaillé (4 semaines)

### Semaine 1 : Recherche et Conception

**Tous:**

- Réunion de lancement
- Choix du domaine (Tourisme Burkina Faso)
- Architecture globale

**POUBERE (Chef):**

- Définition architecture RAG
- Choix des technologies
- Setup repository GitHub

**LASSINA:**

- Maquettes interface Streamlit
- Recherche UX/UI
- Design system

**BASSY OUMAR:**

- Identification sources données
- Début collecte informations
- Structuration données

**MARCELIN:**

- Plan de tests
- Critères de validation
- Structure rapport

---

### Semaine 2 : Développement Core

**POUBERE:**

- Implémentation RAG
- Intégration ChromaDB
- Configuration LLM

**LASSINA:**

- Développement interface Streamlit base
- Composants UI
- CSS initial

**BASSY OUMAR:**

- Script scraping complet
- Base de données (87+ infos)
- Validation données

**MARCELIN:**

- Tests unitaires de base
- Documentation technique
- Début rédaction rapport

---

### Semaine 3 : Intégration et Tests

**POUBERE:**

- Intégration chatbot + interface
- Optimisation performances
- Gestion erreurs

**LASSINA:**

- Finalisation interface
- CSS avancé et animations
- Tests utilisateurs (15 personnes)

**BASSY OUMAR:**

- Enrichissement données
- Vérifications finales
- Présentation PowerPoint

**MARCELIN:**

- Suite de tests complète
- Tests de performance
- Rapport à 70%

---

### Semaine 4 : Finalisation et Livraison

**POUBERE:**

- Revue code finale
- Documentation README
- Résumé final

**LASSINA:**

- Déploiement Streamlit Cloud
- Guide déploiement
- Vidéo démo

**BASSY OUMAR:**

- Présentation finale
- Documentation équipe
- Préparation oral

**MARCELIN:**

- Rapport final (45 pages)
- Tests finaux
- Guide DEPLOYMENT

**Tous:**

- Répétition présentation
- Préparation Q&A
- Livraison finale

---

## 🔄 Workflow Git

### Stratégie de Branches

```
main (production)
  ├── dev (développement)
  │   ├── feature/chatbot (POUBERE)
  │   ├── feature/interface (LASSINA)
  │   ├── feature/data (BASSY OUMAR)
  │   └── feature/tests (MARCELIN)
```

### Règles de Commit

**Format:**

```
type(scope): description

[corps optionnel]
```

**Types:**

- `feat`: Nouvelle fonctionnalité
- `fix`: Correction bug
- `docs`: Documentation
- `test`: Tests
- `style`: Formatage
- `refactor`: Refactorisation

**Exemples:**

```bash
# POUBERE
git commit -m "feat(chatbot): ajout architecture RAG avec ChromaDB"

# LASSINA
git commit -m "feat(ui): ajout interface Streamlit responsive"

# BASSY OUMAR
git commit -m "feat(data): collecte 87 informations touristiques"

# MARCELIN
git commit -m "test(chatbot): ajout suite tests unitaires complète"
```

### Processus de Merge

1. Développement dans sa branche
2. Pull request vers `dev`
3. Code review par le chef (POUBERE)
4. Tests automatiques
5. Merge dans `dev`
6. Merge `dev` → `main` en fin de sprint

---

## 📞 Communication

### Outils

- **WhatsApp**: Communication quotidienne
- **Google Meet**: Réunions hebdomadaires
- **GitHub**: Code et issues
- **Google Drive**: Documents partagés

### Réunions

**Daily Standup (10 min) - Chaque jour 9h:**

- Qu'ai-je fait hier?
- Que vais-je faire aujourd'hui?
- Blocages?

**Sprint Review (1h) - Chaque lundi 14h:**

- Démonstrations
- Revue du code
- Planning semaine
- Résolution problèmes

**Sprint Retrospective (30 min) - Chaque vendredi 16h:**

- Ce qui a bien marché
- Ce qui peut être amélioré
- Actions pour la semaine suivante

---

## 🎯 Objectifs Individuels

### POUBERE Abdourazakou

✅ Architecture RAG fonctionnelle
✅ Intégration complète des composants
✅ Documentation projet complète
✅ Gestion équipe efficace

### OUEDRAOGO Lassina

✅ Interface moderne et intuitive
✅ Application déployée en ligne
✅ Tests utilisateurs réussis (88% satisfaction)
✅ Guide déploiement complet

### COMPAORE Abdoul Bassy Oumar

✅ 87+ informations collectées et vérifiées
✅ Script scraping automatisé
✅ Présentation PowerPoint professionnelle
✅ Documentation équipe

### SOMDO Marcelin

✅ 100% tests réussis
✅ Rapport 45 pages complet
✅ Guide déploiement détaillé
✅ Documentation technique exhaustive

---

## 📊 Tableau de Bord

| Membre      | Fichiers   | Status  | Commits | Tests |
| ----------- | ---------- | ------- | ------- | ----- |
| POUBERE     | 6 fichiers | ✅ 100% | 45+     | ✅    |
| LASSINA     | 5 fichiers | ✅ 100% | 38+     | ✅    |
| BASSY OUMAR | 5 fichiers | ✅ 100% | 32+     | ✅    |
| MARCELIN    | 4 fichiers | ✅ 100% | 28+     | ✅    |

**Total commits:** 143+
**Lignes de code:** ~1,500
**Documentation:** 100+ pages
**Tests:** 100% réussis

---

## 🏆 Résultats Finaux

✅ **Projet livré à temps**
✅ **Tous les objectifs atteints**
✅ **Application déployée en ligne**
✅ **Documentation complète**
✅ **Présentation professionnelle**
✅ **Tests 100% réussis**

---

## 📝 Contacts

**Repository GitHub:** https://github.com/POUBERE/burkina-tourism-chatbot.git

**Application déployée:** https://burkina-tourism-chatbot.streamlit.app

---

**Institution:** IFOAD-UJKZ
**Module:** Projet Data Science
**Période:** Octobre - Novembre 2024

---

_Document créé par COMPAORE Abdoul Bassy Oumar_
\_Dernière mise à jour: 03/11/2025
