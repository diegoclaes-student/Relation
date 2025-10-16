"""Database Layer - Exports"""

# Nouvelle architecture
from database.base import DatabaseManager, db_manager
from database.persons import PersonRepository, person_repository
from database.relations import RelationRepository, relation_repository

# Compatibilité avec ancien code (à migrer progressivement)
# Import de l'ancienne classe RelationDB
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Try to import old database module (one level up)
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("old_database", parent_dir / "database.py")
    if spec and spec.loader:
        old_database = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(old_database)
        RelationDB = old_database.RelationDB
        RELATION_TYPES = old_database.RELATION_TYPES
except Exception as e:
    print(f"⚠️  Warning: Could not import old database module: {e}")
    RelationDB = None
    RELATION_TYPES = {}

__all__ = [
    'DatabaseManager',
    'db_manager',
    'PersonRepository',
    'person_repository',
    'RelationRepository',
    'relation_repository',
    'RelationDB',  # Pour compatibilité
    'RELATION_TYPES',  # Pour compatibilité
]
