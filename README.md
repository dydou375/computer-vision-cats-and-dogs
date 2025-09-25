# Computer Vision - Classification d'images Cats & Dogs

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![FAST Api](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Keras](https://img.shields.io/badge/Keras-%23D00000.svg?style=for-the-badge&logo=Keras&logoColor=white)](https://keras.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)

<div align="center">

<h3>Classification d'images avec Keras et exposition du modèle via Fast API</br></h3>

[Explore the docs](docs/)

</div>

---

## 📌 Introduction

Ce projet est à vocation pédagogique sur des thématiques IA et MLOps. Il permet de réaliser des tâches de Computer Vision et spécifiquement de la classification d'images par la reconnaissance de chats et de chiens.  
Il est composé de :

- Un modèle de computer vision développé avec Keras 3 selon une architecture CNN. Voir le tutoriel Keras ([lien](https://keras.io/examples/vision/image_classification_from_scratch/)).
- Un service API développé avec Fast API, qui permet notamment de réaliser les opérations d'inférence (i.e prédiction), sur la route `/api/predict`.
- Une application web minimaliste (templates Jinja2).
- Des tests automatisés minimalistes (pytest).
- Un pipeline CI/CD minimaliste (Github Action).

## 📁 Structure du projet

```txt
project-name/
├── .github/
│   ├── workflows/           # CI/CD pipelines
│   └── ISSUE_TEMPLATE/      # Templates d'issues
├── config/                  # Fichiers de configuration
├── data/
│   ├── raw/                 # Données brutes (gitignored)
│   ├── processed/           # Données traitées (gitignored)
│   └── external/            # Données externes/références
├── docker/                  # Dockerfiles et compose
├── docs/                    # Documentation
├── notebooks/               # Jupyter notebooks pour exploration
├── requirements/            # Dépendances par environnement
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── scripts/                 # Scripts d'automatisation/déploiement
├── src/                     # Code source principal
│   ├── api/                 # APIs et services web
│   ├── data/                # Scripts de traitement des données
│   ├── models/              # Modèles ML/IA
│   ├── monitoring/          # Monitoring des modèles
│   ├── utils/               # Utilitaires partagés
│   └── web/                 # Templates jinja2
├── tests/                   # Tests unitaires et d'intégration
├── .env.example             # Variables d'environnement exemple
├── .gitignore
├── README.md
├── Makefile                 # Commandes fréquentes
└── pyproject.toml           # Configuration Python/packaging
```

## 🛠️ Commandes utiles

*Section minimaliste à faire évoluer.*

```bash
make env           # Installer les dépendances dans un environnement virtuel
```

## 🎯 API

Lorsque l'environnement virtuel est activé, vous pouvez lancer le serveur de l'API ...

```bash
python scripts/run_api.py
```

... et visiter la page de documentation Swagger :

![Swagger](/docs/img/swagger.png "Page de documentation de l'API")

## 📊 Application web

Lorsque l'environnement virtuel est activé, vous pouvez lancer le serveur de l'API ...

```bash
python scripts/run_api.py
```

... et utiliser l'application web :

![Web APP](/docs/img/web.png "Application web du projet")

## 🔒 Conformité RGPD (Base de données & Monitoring)

Cette application enregistre certaines informations d’inférence et de feedback dans une base PostgreSQL afin d’améliorer le modèle et de suivre ses performances.

- Finalités: amélioration continue du modèle (ré‑entraînement) et monitoring des performances (temps d’inférence, taux d’accord). Aucune finalité marketing.
- Catégories de données: métadonnées techniques d’inférence (date, succès/erreur, temps d’inférence) et feedback utilisateur (positif/négatif). Pas de données personnelles identifiables (DPI) prévues par défaut. Si un fichier ou un identifiant utilisateur est stocké, il doit être pseudonymisé.
- Base légale: intérêt légitime (optimisation du service) ou consentement si un lien peut être fait avec une personne identifiée/identifiable.
- Minimisation: ne stocker que le strict nécessaire (résultats agrégés, noms de fichiers non sensibles/pseudonymisés). Éviter tout contenu d’image en base; conserver les images sur un stockage séparé et contrôlé si besoin.
- Conservation: définir une politique (ex. 180 jours pour les logs d’inférence; 365 jours max pour les feedbacks) avec purge automatique (tâches planifiées/SQL).
- Droits des personnes: prévoir des moyens de suppression/rectification si des données personnelles sont traitées; documenter les procédures.
- Sécurité: restreindre l’accès à la base (comptes de service, rôles/ACL), chiffrer les mots de passe en variables d’environnement, activer TLS entre services si possible, sauvegardes chiffrées et testées.
- Sous‑traitance/Transferts: si hébergement/cloud, s’assurer d’un accord de traitement (DPA) et de la localisation des données conforme (UE/clauses types).
- Journalisation: tracer les accès administratifs et les opérations de maintenance.
- DPIA: non requise a priori pour ces données techniques. À ré‑évaluer si des DPI sont ajoutées.

Note: si vous ajoutez des champs pouvant identifier un utilisateur (email, ID, IP…), mettez à jour cette section, anonymisez/pseudonymisez les données et, si nécessaire, recueillez le consentement explicite.

## 📄 Licence

MIT - voir LICENSE pour plus de détails.
