"""
Point d'entrée WSGI pour Render/Gunicorn
"""
import os
import sys

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(__file__))

from app_v2 import app

# Le serveur Flask sous-jacent pour Gunicorn
server = app.server

# Pour compatibilité avec différents serveurs WSGI
application = server

# Configuration pour production
if not application.config.get('TESTING'):
    application.config['DEBUG'] = False
    application.config['TESTING'] = False

# Log de démarrage
print(f"✅ WSGI application ready on port {os.environ.get('PORT', 'unknown')}")
print(f"🔵 Using {'PostgreSQL' if os.environ.get('DATABASE_URL') else 'SQLite'}")

if __name__ == "__main__":
    # Pour test local uniquement
    port = int(os.environ.get('PORT', 8052))
    app.run_server(debug=False, host='0.0.0.0', port=port)
