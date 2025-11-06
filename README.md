# 🗺️ Centrale Potins Maps

**Application web de visualisation interactive de réseaux sociaux** - Découvre qui est connecté à qui !

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 📖 Description

**Centrale Potins Maps** est une application interactive permettant de visualiser et gérer un réseau social de relations entre personnes. Conçue avec Dash/Plotly, elle offre une expérience utilisateur moderne et responsive.

### ✨ Fonctionnalités principales

- **📊 Visualisation interactive** : Graphe réseau avec algorithmes de layout multiples
- **👥 Gestion des personnes** : Ajout, modification, fusion, suppression
- **🔗 Types de relations** : Bisou (💋), Dodo (😴), Couché ensemble (🛏️), Couple (💑), Ex (💔)
- **🔐 Système d'authentification** : Comptes utilisateurs et admin
- **📱 Design responsive** : Optimisé mobile et desktop
- **🎨 Thème moderne** : Interface premium bleu foncé/blanc cassé
- **👁️ Affichage personnalisable** : Choix d'afficher tous les noms ou seulement les plus importants
- **💡 Propositions publiques** : Les visiteurs peuvent proposer des personnes et relations

## 🚀 Démarrage rapide

### Installation locale

```bash
# Clone le repo
git clone https://github.com/TON-USERNAME/centrale-potins-maps.git
cd centrale-potins-maps

# Installe les dépendances
pip install -r requirements.txt

# Lance l'application
python3 app_v2.py
```

Ouvre http://localhost:8052 dans ton navigateur.

### Déploiement en production

Voir les guides :
- **Guide complet** : [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Démarrage rapide** : [QUICK_START.md](QUICK_START.md)

## 📂 Structure du projet

```
centrale-potins-maps/
├── app_v2.py                  # Application principale Dash
├── graph.py                   # Génération et rendu du graphe
├── database/                  # Couche d'accès aux données
│   ├── persons.py            # Repository personnes
│   ├── relations.py          # Repository relations
│   ├── users.py              # Repository utilisateurs
│   ├── pending_accounts.py   # Repository comptes en attente
│   └── pending_submissions.py # Repository propositions
├── services/                  # Logique métier
│   └── auth_service.py       # Service d'authentification
├── components/                # Composants UI réutilisables
│   ├── auth_components.py    # Composants auth
│   └── admin_panel.py        # Panneau admin
├── utils/                     # Utilitaires
│   └── constants.py          # Constantes (types de relations, etc.)
└── requirements.txt           # Dépendances Python
```

## 🛠️ Technologies utilisées

- **Backend** : Python 3.9+
- **Framework web** : Dash 2.14+ / Flask
- **Visualisation** : Plotly
- **Graphes** : NetworkX
- **UI** : Dash Bootstrap Components
- **Base de données** : 
  - SQLite (développement local)
  - PostgreSQL via Supabase (production)
- **Déploiement** : Vercel

## 👥 Types de relations

| Emoji | Type | Description |
|-------|------|-------------|
| 💋 | Bisou | Simple bisou |
| 😴 | Dodo | Ont dormi ensemble (platonique) |
| 🛏️ | Couché ensemble | Relation physique |
| 💑 | Couple | En couple |
| 💔 | Ex | Anciens |

## 🎨 Captures d'écran

### Vue publique
- Graphe interactif en plein écran
- Menu hamburger avec contrôles
- Propositions de nouvelles personnes/relations

### Vue admin
- Panneau d'administration complet
- Approbation des propositions
- Gestion des utilisateurs
- Modération du contenu

## 🔐 Sécurité

- Mots de passe hashés avec Scrypt
- Sessions sécurisées avec Flask-Session
- Variables d'environnement pour les secrets
- Protection CSRF
- Validation des entrées utilisateur

## 📊 Algorithmes de visualisation

- **Communautés** (par défaut) : Détection automatique de groupes
- **Circulaire** : Disposition en cercle
- **Hiérarchique** : Structure en arbre
- **Radial** : Disposition radiale depuis un centre
- **Force-Directed** : Simulation physique de forces
- **Kamada-Kawai** : Optimisation des distances
- **Spectral** : Basé sur les valeurs propres

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Crée une branche (`git checkout -b feature/AmazingFeature`)
3. Commit tes changements (`git commit -m 'Add AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvre une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Diego Claes**
- GitHub: [@diegoclaes-student](https://github.com/diegoclaes-student)

## 🙏 Remerciements

- [Plotly Dash](https://dash.plotly.com/) pour le framework
- [NetworkX](https://networkx.org/) pour les algorithmes de graphes
- [Supabase](https://supabase.com/) pour la base de données
- [Vercel](https://vercel.com/) pour l'hébergement

## 📞 Support

Pour toute question ou problème :
- Ouvre une [issue](https://github.com/TON-USERNAME/centrale-potins-maps/issues)
- Consulte le [guide de déploiement](DEPLOYMENT_GUIDE.md)

---

**Fait avec ❤️ à Centrale Lyon**
