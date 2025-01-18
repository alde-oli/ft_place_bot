# FTPlace Image Maintainer

[![Release](https://img.shields.io/github/v/release/alde-oli/ft_place_bot?include_prereleases&style=flat-square)](https://github.com/alde-oli/ft_place_bot/releases)
[![CI Status](https://img.shields.io/github/actions/workflow/status/alde-oli/ft_place_bot/ci.yml?branch=main&style=flat-square)](https://github.com/alde-oli/ft_place_bot/actions)
[![License](https://img.shields.io/github/license/alde-oli/ft_place_bot?style=flat-square)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)](pyproject.toml)
[![Code Coverage](https://img.shields.io/codecov/c/github/alde-oli/ft_place_bot?style=flat-square)](https://codecov.io/gh/alde-oli/ft_place_bot)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?style=flat-square)](https://github.com/astral-sh/ruff)

FTPlace Image Maintainer est une application Python conçue pour maintenir des images sur le tableau FTPlace. Elle utilise l'API FTPlace pour interagir avec le tableau, récupère son état actuel et s'assure que l'image cible est correctement maintenue sur le tableau.

## Fonctionnalités

- Interface interactive pour la configuration
- Sauvegarde automatique des paramètres précédents
- Configuration intuitive des priorités de couleurs
- Conversion automatique des images vers les couleurs FTPlace
- Surveillance du tableau et identification des pixels à corriger
- Placement des pixels selon les règles de priorité
- Gestion automatique de l'expiration des tokens

## Prérequis

- Python 3.9+

## Installation

1. Clonez le dépôt :
    ```sh
    git clone https://github.com/alde-oli/ft_place_bot.git
    cd ft_place_bot
    ```

2. Installez poetry si ce n'est pas déjà fait :
    ```sh
    pip install poetry
    ```

3. Installez les dépendances :
    ```sh
    poetry install
    ```

## Utilisation

1. Lancez l'application :
    ```sh
    poetry run ft_place_bot
    ```

2. Suivez les étapes interactives :
   - Configuration des tokens d'accès (sauvegardés pour les utilisations futures)
   - Sélection de l'image à maintenir
   - Définition des coordonnées sur le tableau
   - Configuration des priorités de couleurs (optionnel, configuration précédente réutilisable)

## Configuration des Couleurs

L'interface vous permet de configurer facilement :

- Les niveaux de priorité pour chaque couleur (1-3)
- Les couleurs à ignorer
- Les groupes de couleurs similaires

Votre configuration est automatiquement sauvegardée et peut être réutilisée lors des prochaines exécutions.

## Fichiers de Configuration

Les configurations sont stockées dans :
- `~/.ft_place_bot_config.json` : Stocke les tokens, dernière position, et configuration des couleurs

## Composants

### Interface Interactive (`interface.py`)
- Gestion des interactions utilisateur
- Sauvegarde et chargement des configurations

### API Client (`client_api.py`)
- Communication avec l'API FTPlace
- Gestion des tokens et des requêtes

### Gestionnaire d'Images (`utils.py`)
- Chargement et conversion des images
- Calcul des distances entre couleurs

### Moniteur d'Images (`image_monitor.py`)
- Surveillance du tableau
- Placement intelligent des pixels

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request pour toute amélioration.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
