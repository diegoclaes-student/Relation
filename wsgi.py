"""
Point d'entrée WSGI pour Vercel
"""
from app_v2 import app

# Vercel cherche une variable appelée 'app' ou 'application'
server = app.server

# Pour compatibilité avec différents serveurs WSGI
application = server

if __name__ == "__main__":
    app.run_server(debug=False)
