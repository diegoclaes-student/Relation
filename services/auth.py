"""
Authentication Service
Gère l'authentification, les sessions et les autorisations
"""

from typing import Optional, Dict
from database.users import UserRepository, PendingAccountRepository


class AuthService:
    """Service pour gérer l'authentification"""
    
    @staticmethod
    def login(username: str, password: str) -> Optional[Dict]:
        """
        Authentifie un utilisateur
        Returns: User dict if success, None if failure
        """
        user = UserRepository.authenticate(username, password)
        if user:
            # Ne pas renvoyer le password_hash
            return {
                'id': user['id'],
                'username': user['username'],
                'is_admin': user['is_admin']
            }
        return None
    
    @staticmethod
    def register_request(username: str, password: str) -> tuple[bool, str]:
        """
        Crée une demande de compte
        Returns: (success, message)
        """
        # Vérifier si l'username existe déjà
        if UserRepository.get_user_by_username(username):
            return False, "Ce nom d'utilisateur existe déjà"
        
        # Créer la demande
        request_id = PendingAccountRepository.create_request(username, password)
        if request_id:
            return True, "Demande envoyée ! Un admin doit approuver votre compte."
        else:
            return False, "Une demande avec ce nom d'utilisateur existe déjà"
    
    @staticmethod
    def is_admin(user: Optional[Dict]) -> bool:
        """Vérifie si l'utilisateur est admin"""
        return user is not None and user.get('is_admin', False)
    
    @staticmethod
    def is_authenticated(user: Optional[Dict]) -> bool:
        """Vérifie si l'utilisateur est authentifié"""
        return user is not None


# Export
auth_service = AuthService()
