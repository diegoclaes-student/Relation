# ✅ Checklist Pré-Déploiement

## 📋 Avant de déployer sur Vercel

### 1. Code et Configuration

- [ ] Tous les fichiers sont commités sur Git
- [ ] `.gitignore` est configuré (pas de `.db`, `.log`, `.env`)
- [ ] `requirements.txt` contient toutes les dépendances
- [ ] `vercel.json` existe et est correct
- [ ] `.env.example` est créé (sans secrets réels)
- [ ] Pas de hardcoded secrets dans le code

### 2. Base de données Supabase

- [ ] Projet Supabase créé
- [ ] Toutes les tables sont créées (SQL exécuté)
- [ ] Un admin est créé dans la table `users`
- [ ] `DATABASE_URL` récupéré et sauvegardé
- [ ] Migration SQLite → PostgreSQL effectuée
- [ ] Données vérifiées sur Supabase Dashboard

### 3. Variables d'environnement

- [ ] `DATABASE_URL` noté en lieu sûr
- [ ] `SECRET_KEY` généré avec `python -c 'import secrets; print(secrets.token_hex(32))'`
- [ ] Variables prêtes pour Vercel

### 4. Code PostgreSQL

- [ ] Tous les `sqlite3` remplacés par `psycopg2`
- [ ] Tous les `?` remplacés par `%s`
- [ ] Connexion utilise `os.environ.get('DATABASE_URL')`
- [ ] Aucune référence à `social_network.db` en production

### 5. Tests locaux

- [ ] App démarre sans erreur avec `python3 app_v2.py`
- [ ] Graphe s'affiche correctement
- [ ] Login fonctionne
- [ ] Menu hamburger s'ouvre
- [ ] Checkbox "Afficher tous les noms" fonctionne
- [ ] Propositions publiques fonctionnent
- [ ] Panel admin fonctionne

### 6. GitHub

- [ ] Repo créé sur GitHub
- [ ] Repo est en **PRIVÉ** (important !)
- [ ] Code poussé : `git push origin main`
- [ ] Pas de fichiers sensibles dans le repo

### 7. Sécurité

- [ ] Mot de passe admin par défaut sera changé après déploiement
- [ ] Aucun secret dans le code (uniquement variables d'env)
- [ ] `.env` dans `.gitignore`
- [ ] 2FA activé sur GitHub
- [ ] 2FA sera activé sur Vercel après création

### 8. Performance

- [ ] Images optimisées (si utilisées)
- [ ] Pas de `print()` excessifs (peuvent ralentir)
- [ ] Cache configuré si nécessaire

## 🚀 Pendant le déploiement Vercel

- [ ] Projet importé depuis GitHub
- [ ] Framework Preset : Other
- [ ] Variables d'environnement ajoutées :
  - [ ] `DATABASE_URL`
  - [ ] `SECRET_KEY`
  - [ ] `ENVIRONMENT=production`
- [ ] Deploy lancé

## ✅ Après déploiement

- [ ] URL Vercel fonctionne
- [ ] Graphe s'affiche
- [ ] Login admin fonctionne
- [ ] Changement du mot de passe admin
- [ ] Test complet des fonctionnalités :
  - [ ] Visualisation graphe
  - [ ] Ajout personne/relation (admin)
  - [ ] Proposition personne/relation (public)
  - [ ] Approbation propositions (admin)
  - [ ] Menu hamburger
  - [ ] Tous les layouts de graphe
  - [ ] Recherche de personne
  - [ ] Checkbox "Afficher tous les noms"
- [ ] Logs Vercel vérifiés (pas d'erreurs)
- [ ] Métriques Supabase vérifiées

## 🎨 Post-déploiement

- [ ] URL partagée avec quelques testeurs
- [ ] Feedback collecté
- [ ] Bugs éventuels notés
- [ ] Domaine personnalisé configuré (optionnel)
- [ ] Analytics Vercel activé
- [ ] Monitoring configuré

## 🔒 Sécurité finale

- [ ] Tous les mots de passe par défaut changés
- [ ] 2FA activé sur Vercel
- [ ] 2FA activé sur Supabase
- [ ] Backup de `DATABASE_URL` et `SECRET_KEY` dans un gestionnaire de mots de passe

## 📊 Monitoring

- [ ] Vercel Analytics configuré
- [ ] Supabase Usage vérifié régulièrement
- [ ] Alertes configurées si dépassement de quota

---

## ⚠️ Points critiques à ne PAS oublier

1. **JAMAIS** pousser `.env` ou `.db` sur GitHub
2. **TOUJOURS** garder le repo GitHub **PRIVÉ**
3. **CHANGER** le mot de passe admin par défaut immédiatement après déploiement
4. **SAUVEGARDER** `DATABASE_URL` et `SECRET_KEY` dans un endroit sûr
5. **VÉRIFIER** que le déploiement fonctionne avant de partager l'URL

---

*Dernière mise à jour : Novembre 2025*
