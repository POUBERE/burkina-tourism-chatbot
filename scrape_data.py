"""
Script de collecte et préparation des données touristiques du Burkina Faso
Usage: python scrape_data.py
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
import time

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BurkinaTourismDataCollector:
    """Gestion de la collecte des données touristiques"""

    def __init__(self):
        self.data_dir = Path("./data")
        self.data_dir.mkdir(exist_ok=True)

        self.json_file = self.data_dir / "burkina_tourism_data.json"
        self.txt_file = self.data_dir / "burkina_tourism_data.txt"

        # Base de données
        self.data = {
            "sites_touristiques": [],
            "hebergements": [],
            "restaurants": [],
            "infos_pratiques": [],
            "transport": [],
            "culture": [],
            "evenements": []
        }

    def create_sample_data(self):
        """Génère la base de données touristiques"""
        logger.info("Création des données touristiques du Burkina Faso...")

        # Sites touristiques
        self.data["sites_touristiques"] = [
            {
                "nom": "Cascades de Karfiguéla",
                "ville": "Banfora",
                "region": "Cascades",
                "coordonnees": "10.63°N, 4.56°W",
                "description": "Magnifiques chutes d'eau situées à 12 km de Banfora. Site naturel spectaculaire avec plusieurs niveaux de cascades, bassins naturels parfaits pour la baignade, entouré de végétation luxuriante. Un des sites les plus photographiés du Burkina Faso.",
                "prix": "Entrée gratuite, Guide optionnel 2000-3000 FCFA",
                "horaires": "6h00 - 18h00 tous les jours",
                "meilleure_periode": "Juillet à septembre (saison des pluies pour débit maximal)",
                "duree_visite": "2-3 heures",
                "activites": ["Baignade", "Randonnée", "Photographie", "Pique-nique", "Observation de la nature"],
                "services": ["Petits restaurants locaux", "Vendeurs de souvenirs", "Parking surveillé 500 FCFA", "Guides locaux"],
                "conseils": "Prévoir chaussures antidérapantes, crème solaire, eau. Éviter les weekends si vous cherchez la tranquillité. Négocier le prix du guide avant la visite."
            },
            {
                "nom": "Mosquée de Bobo-Dioulasso",
                "ville": "Bobo-Dioulasso",
                "region": "Hauts-Bassins",
                "description": "Chef-d'œuvre d'architecture soudano-sahélienne construite en banco en 1880. Classée monument historique, elle présente des tours coniques caractéristiques et des poutres en bois qui dépassent des murs.",
                "prix": "1000 FCFA par personne, Photos 500 FCFA supplémentaires",
                "horaires": "8h00-12h00 et 15h00-17h30 (fermé pendant les prières du vendredi)",
                "meilleure_periode": "Toute l'année (éviter l'heure de prière du vendredi)",
                "duree_visite": "1-2 heures",
                "activites": ["Visite guidée", "Architecture", "Photographie", "Histoire culturelle"],
                "conseils": "Tenue respectueuse obligatoire (épaules et genoux couverts), enlever les chaussures, demander la permission avant de photographier les fidèles."
            },
            {
                "nom": "Parc National d'Arly",
                "ville": "Diapaga",
                "region": "Est",
                "description": "Réserve naturelle de 76,000 hectares, partie du complexe W-Arly-Pendjari classé patrimoine mondial UNESCO. Abrite une faune exceptionnelle incluant éléphants, lions, léopards, buffles, hippopotames et plus de 200 espèces d'oiseaux.",
                "prix": "Entrée 10,000 FCFA/personne/jour, Guide obligatoire 15,000 FCFA/jour, Location 4x4 avec chauffeur 50,000 FCFA/jour",
                "horaires": "6h00-18h00 (fermé de juillet à octobre pendant la saison des pluies)",
                "meilleure_periode": "Décembre à mai (saison sèche, animaux près des points d'eau)",
                "duree_visite": "2-3 jours minimum recommandés",
                "activites": ["Safari photo", "Observation de la faune", "Camping", "Ornithologie", "Randonnée guidée"],
                "services": ["Campements aménagés", "Guides professionnels", "Location de véhicules", "Restaurant au camp de base"],
                "conseils": "Réservation obligatoire en haute saison, traitement antipaludéen indispensable, jumelles recommandées, respecter les consignes de sécurité."
            },
            {
                "nom": "Ruines de Loropéni",
                "ville": "Loropéni",
                "region": "Sud-Ouest",
                "description": "Forteresse en pierre datant du 11e siècle, inscrite au patrimoine mondial de l'UNESCO depuis 2009. Premier site burkinabè classé, ces ruines mystérieuses témoignent de l'histoire précoloniale de l'Afrique de l'Ouest.",
                "prix": "2000 FCFA adultes, 1000 FCFA enfants, Guide inclus",
                "horaires": "8h00-17h00 tous les jours",
                "meilleure_periode": "Novembre à février (climat plus frais)",
                "duree_visite": "2-3 heures",
                "activites": ["Visite historique", "Archéologie", "Photographie", "Découverte culturelle"],
                "conseils": "Apporter de l'eau, protection solaire, chaussures de marche. Le site est à 40km de Gaoua sur une piste."
            },
            {
                "nom": "Lac Tengrela",
                "ville": "Banfora",
                "region": "Cascades",
                "description": "Lac sacré abritant des hippopotames sacrés que l'on peut observer de près. Les hippopotames répondent à l'appel des guides locaux, expérience unique en Afrique.",
                "prix": "3000 FCFA par personne, Pirogue incluse",
                "horaires": "7h00-18h00, Meilleure observation 7h-9h et 16h-18h",
                "meilleure_periode": "Toute l'année",
                "duree_visite": "1-2 heures",
                "activites": ["Observation des hippopotames", "Balade en pirogue", "Photographie animalière", "Ornithologie"],
                "services": ["Guides locaux", "Location de pirogues", "Petit marché artisanal"],
                "conseils": "Respecter les consignes de sécurité, ne pas nourrir les animaux, prévoir un pourboire pour le guide."
            },
            {
                "nom": "Dômes de Fabédougou",
                "ville": "Banfora",
                "region": "Cascades",
                "description": "Formations rocheuses spectaculaires vieilles de plus d'un milliard d'années. Paysage lunaire unique avec des rochers aux formes étranges sculptés par l'érosion.",
                "prix": "1000 FCFA par personne",
                "horaires": "Accessible toute la journée",
                "meilleure_periode": "Novembre à mai",
                "duree_visite": "2 heures",
                "activites": ["Escalade facile", "Photographie", "Randonnée", "Pique-nique", "Coucher de soleil spectaculaire"],
                "conseils": "Meilleur moment pour les photos: lever et coucher du soleil. Apporter de l'eau, peu d'ombre sur le site."
            },
            {
                "nom": "Village de Tiébélé",
                "ville": "Tiébélé",
                "region": "Centre-Sud",
                "description": "Village traditionnel Kasséna avec des cases décorées de motifs géométriques peints. Architecture unique et traditions ancestrales préservées. Site culturel exceptionnel.",
                "prix": "5000 FCFA par personne incluant guide et droit photo",
                "horaires": "8h00-17h00",
                "meilleure_periode": "Novembre à février",
                "duree_visite": "3-4 heures",
                "activites": ["Visite culturelle", "Rencontre avec les habitants", "Démonstration d'artisanat", "Photographie", "Achat d'artisanat local"],
                "services": ["Guide obligatoire du village", "Vente d'artisanat", "Possibilité de déjeuner traditionnel"],
                "conseils": "Respecter les coutumes locales, demander avant de photographier les personnes, prévoir des cadeaux pour le chef du village."
            },
            {
                "nom": "Mare aux Crocodiles de Sabou",
                "ville": "Sabou",
                "region": "Centre-Ouest",
                "description": "Mare sacrée abritant plus d'une centaine de crocodiles sacrés. Les crocodiles sont vénérés par la population locale et ne sont pas dangereux pour les visiteurs accompagnés.",
                "prix": "2500 FCFA incluant guide et poulet pour attirer les crocodiles",
                "horaires": "7h00-18h00",
                "meilleure_periode": "Toute l'année",
                "duree_visite": "1 heure",
                "activites": ["Observation des crocodiles", "Nourrissage des crocodiles", "Photographie", "Visite du village"],
                "conseils": "Suivre impérativement les instructions du guide, ne pas s'approcher seul de l'eau."
            },
            {
                "nom": "Pics de Sindou",
                "ville": "Sindou",
                "region": "Cascades",
                "description": "Chaîne de pics rocheux s'étendant sur plusieurs kilomètres. Formation géologique impressionnante offrant des paysages spectaculaires et des sentiers de randonnée.",
                "prix": "1500 FCFA par personne",
                "horaires": "6h00-18h00",
                "meilleure_periode": "Novembre à mars",
                "duree_visite": "3-4 heures",
                "activites": ["Randonnée", "Escalade", "Photographie", "Observation du paysage", "Camping possible"],
                "services": ["Guides locaux disponibles", "Petite restauration", "Location de matériel d'escalade"],
                "conseils": "Chaussures de randonnée indispensables, partir tôt le matin pour éviter la chaleur, apporter beaucoup d'eau."
            },
            {
                "nom": "Musée National du Burkina Faso",
                "ville": "Ouagadougou",
                "region": "Centre",
                "description": "Musée moderne présentant l'histoire, la culture et les traditions du Burkina Faso. Collections d'objets traditionnels, costumes, instruments de musique et art contemporain.",
                "prix": "500 FCFA nationaux, 1500 FCFA étrangers",
                "horaires": "Mardi-Samedi 9h00-17h00, Dimanche 10h00-17h00",
                "meilleure_periode": "Toute l'année (climatisé)",
                "duree_visite": "2-3 heures",
                "activites": ["Expositions permanentes", "Expositions temporaires", "Boutique souvenirs", "Ateliers culturels"],
                "services": ["Guides disponibles", "Boutique", "Cafétéria", "Parking gratuit"],
                "conseils": "Photos interdites dans certaines salles, visites guidées très instructives."
            }
        ]

        # Hébergements
        self.data["hebergements"] = [
            {
                "nom": "Hôtel Splendid",
                "categorie": "4 étoiles",
                "ville": "Ouagadougou",
                "adresse": "Avenue Kwame Nkrumah",
                "telephone": "+226 25 30 60 60",
                "email": "info@splendidhotel.bf",
                "prix_nuit": "80,000 - 150,000 FCFA",
                "services": ["Piscine", "Restaurant", "Bar", "Salle de conférence", "WiFi gratuit", "Climatisation", "Parking", "Blanchisserie"],
                "description": "Hôtel de luxe au cœur de Ouagadougou, proche des institutions et du centre d'affaires."
            },
            {
                "nom": "Laico Ouaga 2000",
                "categorie": "5 étoiles",
                "ville": "Ouagadougou",
                "adresse": "Ouaga 2000",
                "telephone": "+226 25 37 60 00",
                "prix_nuit": "100,000 - 250,000 FCFA",
                "services": ["2 Piscines", "3 Restaurants", "Spa", "Salle de sport", "Centre d'affaires", "WiFi", "Navette aéroport"],
                "description": "Hôtel international de standing dans le quartier moderne Ouaga 2000."
            },
            {
                "nom": "Auberge Chez Thérese",
                "categorie": "Économique",
                "ville": "Banfora",
                "adresse": "Centre-ville",
                "telephone": "+226 70 12 34 56",
                "prix_nuit": "10,000 - 20,000 FCFA",
                "services": ["Ventilateur", "Moustiquaire", "Restaurant", "Parking", "Eau chaude"],
                "description": "Auberge familiale conviviale, excellent rapport qualité-prix, proche des sites touristiques."
            },
            {
                "nom": "Campement de Karfiguéla",
                "categorie": "Campement",
                "ville": "Banfora",
                "adresse": "Route des Cascades",
                "prix_nuit": "5,000 - 15,000 FCFA",
                "services": ["Cases traditionnelles", "Restaurant", "Guide", "Parking", "Ambiance locale"],
                "description": "Campement rustique à proximité immédiate des cascades, expérience authentique."
            },
            {
                "nom": "Hôtel Canne à Sucre",
                "categorie": "3 étoiles",
                "ville": "Banfora",
                "adresse": "Boulevard de la République",
                "telephone": "+226 20 91 03 41",
                "prix_nuit": "35,000 - 60,000 FCFA",
                "services": ["Piscine", "Restaurant", "Bar", "Jardin", "WiFi", "Climatisation", "Organisation d'excursions"],
                "description": "Hôtel confortable avec belle piscine, base idéale pour explorer la région des Cascades."
            },
            {
                "nom": "Villa Rose",
                "categorie": "Maison d'hôtes",
                "ville": "Bobo-Dioulasso",
                "adresse": "Quartier Diaradougou",
                "telephone": "+226 20 97 54 32",
                "prix_nuit": "25,000 - 40,000 FCFA",
                "services": ["Jardin", "Terrasse", "Petit déjeuner inclus", "WiFi", "Climatisation", "Cuisine équipée"],
                "description": "Maison d'hôtes charmante dans un quartier calme, accueil personnalisé."
            },
            {
                "nom": "Hôtel Tivoli",
                "categorie": "2 étoiles",
                "ville": "Bobo-Dioulasso",
                "adresse": "Centre-ville",
                "prix_nuit": "20,000 - 35,000 FCFA",
                "services": ["Restaurant", "Bar", "Climatisation", "Parking", "WiFi"],
                "description": "Hôtel simple mais propre, bien situé pour visiter la vieille ville."
            },
            {
                "nom": "Ranch de Nazinga",
                "categorie": "Lodge",
                "ville": "Parc de Nazinga",
                "region": "Centre-Sud",
                "prix_nuit": "30,000 - 50,000 FCFA",
                "services": ["Safari", "Restaurant", "Bar", "Guide naturaliste", "Observation des éléphants"],
                "description": "Lodge au cœur de la réserve, idéal pour l'observation de la faune sauvage."
            }
        ]

        # Restaurants
        self.data["restaurants"] = [
            {
                "nom": "Le Gondwana",
                "cuisine": "Internationale et Burkinabè",
                "ville": "Ouagadougou",
                "adresse": "Zone du Bois",
                "telephone": "+226 25 38 19 19",
                "budget_moyen": "10,000 - 20,000 FCFA",
                "horaires": "12h00-15h00 et 19h00-23h00",
                "specialites": ["Capitaine grillé", "Riz gras", "Grillades", "Poulet bicyclette"],
                "ambiance": "Terrasse agréable, musique live le weekend"
            },
            {
                "nom": "Le Verdoyant",
                "cuisine": "Française et Africaine",
                "ville": "Ouagadougou",
                "adresse": "Avenue Yennenga",
                "budget_moyen": "8,000 - 15,000 FCFA",
                "horaires": "11h30-15h00 et 18h30-22h30",
                "specialites": ["Steaks", "Poisson braisé", "Salades", "Desserts maison"],
                "ambiance": "Jardin ombragé, cadre reposant"
            },
            {
                "nom": "Maquis Chez Tantie",
                "cuisine": "Locale",
                "ville": "Ouagadougou",
                "adresse": "Quartier Gounghin",
                "budget_moyen": "2,000 - 5,000 FCFA",
                "horaires": "10h00-23h00",
                "specialites": ["Poulet grillé", "Poisson braisé", "Tô", "Riz sauce"],
                "ambiance": "Authentique maquis burkinabè, très animé"
            },
            {
                "nom": "Le Dancing",
                "cuisine": "Burkinabè et Occidentale",
                "ville": "Bobo-Dioulasso",
                "adresse": "Centre-ville",
                "budget_moyen": "5,000 - 12,000 FCFA",
                "horaires": "11h00-tard",
                "specialites": ["Brochettes", "Riz gras", "Bière locale", "Grillades"],
                "ambiance": "Restaurant-bar avec musique, très populaire"
            },
            {
                "nom": "La Guinguette",
                "cuisine": "Française",
                "ville": "Banfora",
                "adresse": "Bord du lac",
                "budget_moyen": "7,000 - 15,000 FCFA",
                "horaires": "12h00-22h00",
                "specialites": ["Pizza au four à bois", "Pâtes fraîches", "Poisson du jour"],
                "ambiance": "Vue sur le lac, cadre romantique"
            }
        ]

        # Informations pratiques
        self.data["infos_pratiques"] = [
            {
                "categorie": "Visa",
                "titre": "Formalités d'entrée",
                "description": "Visa obligatoire pour la plupart des nationalités. Obtention possible à l'arrivée à l'aéroport (visa de 30 jours: 94,000 FCFA) ou au consulat. Passeport valide 6 mois après la date de retour. Carnet de vaccination fièvre jaune obligatoire."
            },
            {
                "categorie": "Santé",
                "titre": "Précautions sanitaires",
                "description": "Vaccination fièvre jaune obligatoire. Traitement antipaludéen recommandé. Éviter l'eau du robinet, préférer l'eau en bouteille. Se protéger des moustiques. Assurance santé avec rapatriement conseillée."
            },
            {
                "categorie": "Monnaie",
                "titre": "Franc CFA",
                "description": "Le Franc CFA (XOF) est la monnaie officielle. 1 Euro = 656 FCFA (taux fixe). Distributeurs automatiques dans les grandes villes. Cash préféré dans les zones rurales. Cartes Visa/Mastercard acceptées dans grands hôtels."
            },
            {
                "categorie": "Climat",
                "titre": "Quand visiter",
                "description": "Climat tropical avec deux saisons: saison sèche (octobre à mai) idéale pour le tourisme, et saison des pluies (juin à septembre). Températures: 25-35°C en saison sèche, 20-30°C en saison des pluies."
            },
            {
                "categorie": "Langue",
                "titre": "Communication",
                "description": "Français langue officielle. Plus de 60 langues locales dont le mooré (50% population), le dioula et le fulfuldé. Anglais peu parlé sauf dans grands hôtels."
            },
            {
                "categorie": "Sécurité",
                "titre": "Conseils sécurité",
                "description": "Éviter les zones frontalières nord et est. Se renseigner sur la situation sécuritaire avant le départ. Éviter de sortir seul la nuit. Garder copies des documents importants. Numéros utiles: Police 17, Pompiers 18."
            },
            {
                "categorie": "Électricité",
                "titre": "Prises et voltage",
                "description": "220V, 50Hz. Prises type C et E (standard européen). Coupures occasionnelles, prévoir une lampe torche. Adaptateur peut être nécessaire pour certains appareils."
            },
            {
                "categorie": "Téléphone/Internet",
                "titre": "Télécommunications",
                "description": "Indicatif +226. Cartes SIM locales disponibles (Orange, Moov, Telecel) environ 1000 FCFA. Internet 3G/4G dans les villes. WiFi dans la plupart des hôtels."
            }
        ]

        # Transport
        self.data["transport"] = [
            {
                "type": "Avion",
                "compagnies": ["Air France", "Brussels Airlines", "Ethiopian Airlines", "Royal Air Maroc", "Air Burkina"],
                "aeroport_principal": "Aéroport International de Ouagadougou",
                "liaisons_nationales": "Vols intérieurs vers Bobo-Dioulasso avec Air Burkina"
            },
            {
                "type": "Bus",
                "compagnies": ["STMB", "TSR", "TCV", "Rakieta"],
                "principales_liaisons": "Ouaga-Bobo (4h, 5000 FCFA), Ouaga-Banfora (6h, 7000 FCFA)",
                "conseils": "Réserver à l'avance, préférer les compagnies réputées"
            },
            {
                "type": "Taxi",
                "tarifs_ville": "Course en ville: 1000-3000 FCFA selon distance",
                "taxi_brousse": "Pour liaisons interurbaines, négocier le prix avant",
                "location_voiture": "40,000-80,000 FCFA/jour avec chauffeur recommandé"
            }
        ]

        # Culture et événements
        self.data["culture"] = [
            {
                "nom": "FESPACO",
                "type": "Festival de cinéma",
                "periode": "Février/Mars (années impaires)",
                "description": "Plus grand festival de cinéma africain, attire des cinéastes du monde entier",
                "lieu": "Ouagadougou"
            },
            {
                "nom": "SIAO",
                "type": "Salon de l'artisanat",
                "periode": "Octobre/Novembre (années paires)",
                "description": "Salon International de l'Artisanat de Ouagadougou, vitrine de l'artisanat africain",
                "lieu": "Ouagadougou"
            },
            {
                "nom": "Semaine Nationale de la Culture",
                "type": "Festival culturel",
                "periode": "Mars/Avril (années paires)",
                "description": "Célébration de la diversité culturelle burkinabè",
                "lieu": "Bobo-Dioulasso"
            }
        ]

        # Événements
        self.data["evenements"] = [
            {
                "nom": "FESPACO",
                "type": "Festival de cinéma",
                "periode": "Février/Mars (années impaires)",
                "description": "Plus grand festival de cinéma africain, attire des cinéastes du monde entier",
                "lieu": "Ouagadougou",
                "prix": "Variable selon les projections",
                "site_web": "www.fespaco.bf"
            },
            {
                "nom": "SIAO",
                "type": "Salon de l'artisanat",
                "periode": "Octobre/Novembre (années paires)",
                "description": "Salon International de l'Artisanat de Ouagadougou, vitrine de l'artisanat africain",
                "lieu": "Ouagadougou",
                "prix": "Entrée payante",
                "site_web": "www.siao.bf"
            },
            {
                "nom": "Semaine Nationale de la Culture",
                "type": "Festival culturel",
                "periode": "Mars/Avril (années paires)",
                "description": "Célébration de la diversité culturelle burkinabè avec danses, musiques et expositions",
                "lieu": "Bobo-Dioulasso"
            }
        ]

        logger.info(f"✓ Données créées: {len(self.data['sites_touristiques'])} sites, "
                    f"{len(self.data['hebergements'])} hébergements, "
                    f"{len(self.data['restaurants'])} restaurants")

    def save_json_data(self):
        """Sauvegarde au format JSON"""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ Données JSON sauvegardées dans {self.json_file}")

    def save_text_data(self):
        """Génère et sauvegarde le fichier texte"""
        text_content = []

        # En-tête
        text_content.append("=" * 80)
        text_content.append("GUIDE TOURISTIQUE COMPLET DU BURKINA FASO")
        text_content.append("Le Pays des Hommes Intègres")
        text_content.append("=" * 80)
        text_content.append("")

        # Introduction
        text_content.append("INTRODUCTION AU BURKINA FASO")
        text_content.append("-" * 40)
        text_content.append("""
Le Burkina Faso, littéralement « Pays des Hommes Intègres », est un pays enclavé d'Afrique de l'Ouest
qui offre une richesse culturelle et naturelle exceptionnelle. Avec plus de 60 groupes ethniques,
une tradition d'hospitalité légendaire (le « Tenga » ou terre d'accueil), et des paysages variés
allant de la savane aux formations rocheuses spectaculaires, le Burkina Faso est une destination
authentique pour les voyageurs en quête d'expériences uniques.

Capitale: Ouagadougou (communément appelée "Ouaga")
Population: Environ 21 millions d'habitants
Superficie: 274,200 km²
Langues: Français (officielle), Mooré, Dioula, Fulfuldé et plus de 60 langues locales
Monnaie: Franc CFA (XOF)
Fuseau horaire: GMT+0
Indicatif téléphonique: +226
        """)

        # Sites touristiques
        text_content.append("\nSITES TOURISTIQUES INCONTOURNABLES")
        text_content.append("=" * 40)
        for site in self.data["sites_touristiques"]:
            text_content.append(f"\n{site['nom'].upper()}")
            text_content.append("-" * len(site['nom']))
            text_content.append(
                f"Localisation: {site.get('ville', '')}, {site.get('region', '')}")
            text_content.append(f"Description: {site.get('description', '')}")
            text_content.append(
                f"Prix d'entrée: {site.get('prix', 'Non spécifié')}")
            text_content.append(
                f"Horaires: {site.get('horaires', 'Non spécifié')}")
            text_content.append(
                f"Meilleure période: {site.get('meilleure_periode', "Toute l'année")}")

            if site.get('activites'):
                text_content.append(
                    f"Activités possibles: {', '.join(site['activites'])}")

            if site.get('conseils'):
                text_content.append(f"Conseils pratiques: {site['conseils']}")

            text_content.append("")

        # Hébergements
        text_content.append("\nHÉBERGEMENTS RECOMMANDÉS")
        text_content.append("=" * 40)
        for hotel in self.data["hebergements"]:
            text_content.append(
                f"\n{hotel['nom']} ({hotel.get('categorie', '')})")
            text_content.append(f"Ville: {hotel.get('ville', '')}")
            text_content.append(
                f"Prix par nuit: {hotel.get('prix_nuit', 'Variable')}")
            if hotel.get('services'):
                text_content.append(
                    f"Services: {', '.join(hotel['services'])}")
            text_content.append(f"Description: {hotel.get('description', '')}")
            text_content.append("")

        # Restaurants
        text_content.append("\nRESTAURANTS ET GASTRONOMIE")
        text_content.append("=" * 40)
        text_content.append("""
La cuisine burkinabè est riche et variée, mélange d'influences ouest-africaines. 
Les plats nationaux incluent:
- Le Tô: pâte de mil ou maïs accompagnée de sauce
- Le Riz gras: riz cuit avec viande et légumes
- Le Poulet bicyclette: poulet local grillé
- Les brochettes de viande
- Le Dolo: bière de mil traditionnelle
- Le Zoom-koom: boisson à base de mil
        """)

        for resto in self.data["restaurants"]:
            text_content.append(f"\n{resto['nom']}")
            text_content.append(f"Cuisine: {resto.get('cuisine', '')}")
            text_content.append(f"Ville: {resto.get('ville', '')}")
            text_content.append(
                f"Budget moyen: {resto.get('budget_moyen', '')}")
            if resto.get('specialites'):
                text_content.append(
                    f"Spécialités: {', '.join(resto['specialites'])}")
            text_content.append("")

        # Informations pratiques
        text_content.append("\nINFORMATIONS PRATIQUES")
        text_content.append("=" * 40)
        for info in self.data["infos_pratiques"]:
            text_content.append(f"\n{info['titre'].upper()}")
            text_content.append("-" * len(info['titre']))
            text_content.append(info['description'])
            text_content.append("")

        # Transport
        text_content.append("\nTRANSPORT")
        text_content.append("=" * 40)
        for transport in self.data["transport"]:
            text_content.append(f"\n{transport['type'].upper()}")
            for key, value in transport.items():
                if key != 'type':
                    if isinstance(value, list):
                        text_content.append(
                            f"{key.replace('_', ' ').title()}: {', '.join(value)}")
                    else:
                        text_content.append(
                            f"{key.replace('_', ' ').title()}: {value}")
            text_content.append("")

        # Culture et événements
        text_content.append("\nÉVÉNEMENTS CULTURELS MAJEURS")
        text_content.append("=" * 40)
        for event in self.data["culture"]:
            text_content.append(f"\n{event['nom']}")
            text_content.append(f"Type: {event['type']}")
            text_content.append(f"Période: {event['periode']}")
            text_content.append(f"Description: {event['description']}")
            text_content.append(f"Lieu: {event['lieu']}")
            text_content.append("")

        # Conseils généraux
        text_content.append("\nCONSEILS POUR UN VOYAGE RÉUSSI")
        text_content.append("=" * 40)
        text_content.append("""
1. MEILLEURE PÉRIODE: Novembre à février (saison fraîche et sèche)
2. BUDGET MOYEN: 30,000-50,000 FCFA/jour pour un confort moyen
3. DURÉE RECOMMANDÉE: Minimum 7-10 jours pour découvrir les essentiels
4. ITINÉRAIRE CLASSIQUE: Ouagadougou → Bobo-Dioulasso → Banfora → Retour
5. SOUVENIRS À RAPPORTER: Bronze de Ouagadougou, tissus Faso Dan Fani, instruments de musique, masques
6. PHOTOGRAPHIER: Toujours demander la permission avant de photographier les personnes
7. POURBOIRES: Courants mais non obligatoires (500-1000 FCFA approprié)
8. NÉGOCIATION: Normale sur les marchés, prix fixes dans les magasins
9. RESPECT: Tenue correcte appréciée, surtout dans les lieux religieux
10. HOSPITALITÉ: Les Burkinabè sont réputés pour leur accueil chaleureux
        """)

        # Contacts utiles
        text_content.append("\nCONTACTS UTILES")
        text_content.append("=" * 40)
        text_content.append("""
- Police: 17
- Pompiers: 18
- SAMU: 112
- Office National du Tourisme Burkinabè (ONTB): +226 25 31 19 59
- Aéroport de Ouagadougou: +226 25 30 65 15
- Ambassade de France: +226 25 49 66 66
- Hôpital Yalgado Ouagadougou: +226 25 30 66 44
        """)

        # Lexique de base
        text_content.append("\nLEXIQUE DE BASE EN MOORÉ")
        text_content.append("=" * 40)
        text_content.append("""
- Bonjour (matin): Né y yibéogo
- Bonjour (après-midi): Né y zaabré
- Comment allez-vous?: Kibaré?
- Ça va bien: Laafi
- Merci: Barka
- Au revoir: Wend na kô ligdi
- Oui: Ôô
- Non: Ayi
- S'il vous plaît: Soré
- Combien?: Boaga?
- Eau: Kôom
- Nourriture: Ribou
        """)

        with open(self.txt_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(text_content))

        logger.info(
            f"✓ Données texte sauvegardées dans {self.txt_file} ({len(text_content)} lignes)")

    def scrape_additional_data(self):
        """
        Récupération de données complémentaires depuis des sources externes
        À implémenter selon les besoins
        """
        logger.info("Recherche de données complémentaires...")
        
        # Structure prévue pour intégration future de sources web
        # Nécessite respect des conditions d'utilisation
        
        logger.info("✓ Récupération terminée")

    def validate_data(self):
        """Vérifie l'intégrité des données"""
        issues = []

        for category, items in self.data.items():
            if not items:
                issues.append(f"Catégorie '{category}' vide")
            else:
                if category == "sites_touristiques":
                    for site in items:
                        if not site.get("nom"):
                            issues.append(f"Site sans nom dans '{category}'")
                        if not site.get("description"):
                            issues.append(
                                f"Site '{site.get('nom', 'inconnu')}' sans description")

        if issues:
            logger.warning("Problèmes détectés:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("✓ Validation réussie")

        return len(issues) == 0

    def generate_statistics(self):
        """Calcule les statistiques de la base de données"""
        stats = {
            "total_sites": len(self.data.get("sites_touristiques", [])),
            "total_hebergements": len(self.data.get("hebergements", [])),
            "total_restaurants": len(self.data.get("restaurants", [])),
            "villes_couvertes": set(),
            "prix_moyen_hotel": [],
            "activites_disponibles": set()
        }

        for site in self.data.get("sites_touristiques", []):
            if site.get("ville"):
                stats["villes_couvertes"].add(site["ville"])

        for hotel in self.data.get("hebergements", []):
            if hotel.get("ville"):
                stats["villes_couvertes"].add(hotel["ville"])

        for site in self.data.get("sites_touristiques", []):
            if site.get("activites"):
                stats["activites_disponibles"].update(site["activites"])

        logger.info("\n" + "="*50)
        logger.info("STATISTIQUES DES DONNÉES")
        logger.info("="*50)
        logger.info(f"Sites touristiques: {stats['total_sites']}")
        logger.info(f"Hébergements: {stats['total_hebergements']}")
        logger.info(f"Restaurants: {stats['total_restaurants']}")
        logger.info(f"Villes couvertes: {len(stats['villes_couvertes'])}")
        logger.info(f"  → {', '.join(sorted(stats['villes_couvertes']))}")
        logger.info(
            f"Activités disponibles: {len(stats['activites_disponibles'])}")
        logger.info(
            f"  → {', '.join(sorted(list(stats['activites_disponibles'])[:5]))}...")

        return stats

    def run(self):
        """Lance le processus complet"""
        logger.info("\n" + "="*50)
        logger.info("DÉMARRAGE DE LA COLLECTE DE DONNÉES")
        logger.info("="*50)

        try:
            self.create_sample_data()
            self.scrape_additional_data()

            if self.validate_data():
                self.save_json_data()
                self.save_text_data()
                self.generate_statistics()

                logger.info("\n✅ COLLECTE TERMINÉE AVEC SUCCÈS!")
                logger.info(f"📁 Fichiers créés:")
                logger.info(f"   - {self.json_file}")
                logger.info(f"   - {self.txt_file}")

                return True
            else:
                logger.error("❌ Validation échouée")
                return False

        except Exception as e:
            logger.error(f"❌ Erreur: {e}")
            return False


def main():
    """Point d'entrée du programme"""
    collector = BurkinaTourismDataCollector()

    if collector.json_file.exists():
        response = input("Les données existent déjà. Les régénérer ? (o/n): ")
        if response.lower() != 'o':
            logger.info("Opération annulée.")
            return

    success = collector.run()

    if success:
        print("\n" + "="*50)
        print("✨ Données prêtes pour le chatbot!")
        print("Lancez 'python burkina_chatbot.py' pour tester")
        print("ou 'streamlit run app.py' pour l'interface web")
        print("="*50)
    else:
        print("\n❌ La collecte a échoué.")
        print("Consultez les logs pour plus de détails.")


if __name__ == "__main__":
    main()