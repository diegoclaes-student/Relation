"""Validateurs pour les données"""

from typing import Optional, List
import re


class ValidationError(Exception):
    """Exception levée lors d'une validation échouée"""
    pass


class Validator:
    """Classe de validation centralisée"""
    
    @staticmethod
    def validate_person_name(name: str) -> bool:
        """Valide un nom de personne"""
        if not name:
            raise ValidationError("Le nom ne peut pas être vide")
        
        name = name.strip()
        if len(name) < 2:
            raise ValidationError("Le nom doit contenir au moins 2 caractères")
        
        if len(name) > 100:
            raise ValidationError("Le nom ne peut pas dépasser 100 caractères")
        
        # Autoriser lettres, espaces, tirets, apostrophes
        if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", name):
            raise ValidationError("Le nom contient des caractères invalides")
        
        return True
    
    @staticmethod
    def validate_relation(person1: str, person2: str, relation_type: int) -> bool:
        """Valide une relation"""
        # Valider les noms
        Validator.validate_person_name(person1)
        Validator.validate_person_name(person2)
        
        # Vérifier que ce n'est pas une auto-relation
        if person1.strip().lower() == person2.strip().lower():
            raise ValidationError("Une personne ne peut pas avoir de relation avec elle-même")
        
        # Valider le type de relation
        from utils.constants import RELATION_TYPES
        if relation_type not in RELATION_TYPES:
            raise ValidationError(f"Type de relation invalide: {relation_type}")
        
        return True
    
    @staticmethod
    def validate_gender(gender: str) -> None:
        """
        Valide un genre
        
        Raises:
            ValidationError si invalide
        """
        # Accepter les clés (M, F, NB, O) et les valeurs (Homme, Femme, etc.)
        from utils.constants import GENDERS
        valid_keys = list(GENDERS.keys())
        valid_values = list(GENDERS.values())
        
        if gender and gender not in valid_keys and gender not in valid_values:
            raise ValidationError(f"Genre invalide: {gender}. Valeurs acceptées: {', '.join([str(k) for k in valid_keys if k is not None])}")
    
    @staticmethod
    def validate_orientation(orientation: Optional[str]) -> bool:
        """Valide une orientation sexuelle"""
        if orientation is None:
            return True
        
        from utils.constants import SEXUAL_ORIENTATIONS
        if orientation not in SEXUAL_ORIENTATIONS:
            raise ValidationError(f"Orientation sexuelle invalide: {orientation}")
        
        return True
    
    @staticmethod
    def sanitize_name(name: str) -> str:
        """Nettoie et normalise un nom"""
        if not name:
            return ""
        
        # Supprimer espaces en début/fin
        name = name.strip()
        
        # Normaliser les espaces multiples
        name = re.sub(r'\s+', ' ', name)
        
        # Capitaliser la première lettre de chaque mot
        name = ' '.join(word.capitalize() for word in name.split())
        
        return name
