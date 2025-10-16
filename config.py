"""Configuration centralisée de l'application"""

import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "social_network.db"

# Application
APP_TITLE = "Social Network Analyzer"
APP_VERSION = "2.0.0"
HOST = "0.0.0.0"
PORT = 8051
DEBUG = True

# Authentification
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Performance
CACHE_TIMEOUT = 300  # secondes
MAX_HISTORY_ITEMS = 100
GRAPH_UPDATE_DEBOUNCE = 500  # millisecondes

# UI
THEME = "BOOTSTRAP"
GRAPH_HEIGHT = "90vh"
MODAL_SIZE = "xl"

# Base de données
DB_TIMEOUT = 30
DB_CHECK_SAME_THREAD = False
