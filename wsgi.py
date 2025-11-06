"""
Point d'entrée WSGI pour Render/Gunicorn/Vercel
"""
import os
from app_v2 import app

# Le serveur Flask sous-jacent pour Gunicorn
server = app.server

# Pour compatibilité avec différents serveurs WSGI
application = server

# Configuration pour production
server.config['DEBUG'] = False
server.config['TESTING'] = False

if __name__ == "__main__":
    # Pour test local uniquement
    port = int(os.environ.get('PORT', 8052))
    app.run_server(debug=False, host='0.0.0.0', port=port)
