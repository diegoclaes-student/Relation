"""Configuration centralisée de l'application

Les valeurs sensibles et celles dépendantes de l'environnement peuvent être
passées via des variables d'environnement (12-factor). Ceci facilite le
déploiement sur des plateformes comme Render, Fly.io, Vercel (Docker) etc.
"""

import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "social_network.db"))

# Application
APP_TITLE = os.getenv("APP_TITLE", "Social Network Analyzer")
APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8051"))
# DEBUG can be set to "True"/"1"/"yes" in environment
DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes")

# Authentification
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Security
SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("FLASK_SECRET_KEY", "change-this-in-prod"))

# Performance
CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", "300"))  # secondes
MAX_HISTORY_ITEMS = int(os.getenv("MAX_HISTORY_ITEMS", "100"))
GRAPH_UPDATE_DEBOUNCE = int(os.getenv("GRAPH_UPDATE_DEBOUNCE", "500"))  # millisecondes

# UI
THEME = os.getenv("THEME", "BOOTSTRAP")
GRAPH_HEIGHT = os.getenv("GRAPH_HEIGHT", "90vh")
MODAL_SIZE = os.getenv("MODAL_SIZE", "xl")

# Base de données
DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", "30"))
DB_CHECK_SAME_THREAD = os.getenv("DB_CHECK_SAME_THREAD", "False").lower() in ("1", "true", "yes")
