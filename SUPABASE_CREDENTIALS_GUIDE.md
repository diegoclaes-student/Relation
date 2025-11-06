# 🔑 Guide : Où trouver tes credentials Supabase

## 1️⃣ Connection String URI (ce qu'il te faut)

### Où la trouver ?

1. **Connecte-toi** à [app.supabase.com](https://app.supabase.com)
2. Clique sur ton **projet** (exemple : `centrale-potins-maps`)
3. Va dans le menu gauche → **Settings** (⚙️)
4. Clique sur **Database** dans le sous-menu
5. Cherche la section **Connection string**
6. **Sélectionne "URI"** dans le dropdown
7. 📋 **Copie tout** (commence par `postgresql://`)

### Format de la connection string :

```
postgresql://postgres:[PASSWORD]@[SUPABASE_HOST]:5432/postgres
```

Exemple complet (fictif) :
```
postgresql://postgres:abc123XYZ789@abc123xyz789.supabase.co:5432/postgres
```

---

## 2️⃣ Comment décoder les parties

| Partie | Explication | Où la trouver |
|--------|-------------|---|
| `postgres` | Nom d'utilisateur par défaut | Toujours "postgres" |
| `[PASSWORD]` | Mot de passe de la base de données | Settings → Database → Password (visible avec l'icône 👁️) |
| `[SUPABASE_HOST]` | Domaine Supabase du projet | Settings → Database → Host |
| `5432` | Port PostgreSQL standard | Toujours 5432 |
| `postgres` | Nom de la base de données | Toujours "postgres" |

---

## 3️⃣ Étapes détaillées pour récupérer chaque partie

### **Étape A : Récupérer le PASSWORD**

1. Va dans **Settings → Database**
2. Cherche **"Password"** ou **"Database Password"**
3. Clique sur l'icône 👁️ pour révéler le mot de passe
4. Copie-le (exemple : `abc123XYZ789`)

### **Étape B : Récupérer le SUPABASE_HOST**

1. Dans le même écran **Settings → Database**
2. Cherche **"Host"** ou **"Server Address"**
3. Copie l'adresse complète (exemple : `abc123xyz789.supabase.co`)

---

## 4️⃣ Alternative : Copier directement depuis l'URI

**Le plus simple** : Supabase te donne tout d'un coup !

1. **Settings → Database**
2. Section **"Connection string"**
3. Dropdown en haut : choisis **"URI"** (pas "SQL" ou "Javascript")
4. 📋 **Copie-colle TOUTE la string** - c'est prêt à utiliser !

```bash
# Exemple d'utilisation
export DATABASE_URL='postgresql://postgres:SuperMotDePasse123@abc123xyz.supabase.co:5432/postgres'
python3 migrate_to_postgres.py
```

---

## 5️⃣ Où utiliser cette connection string ?

### **Option A : Variable d'environnement (migration locale)**
```bash
export DATABASE_URL='postgresql://postgres:TON_MOT_DE_PASSE@abc123.supabase.co:5432/postgres'
python3 migrate_to_postgres.py
```

### **Option B : Vercel (déploiement)**
1. Va sur [vercel.com](https://vercel.com)
2. Sélectionne ton projet
3. **Settings → Environment Variables**
4. Ajoute une nouvelle variable :
   - **Name** : `DATABASE_URL`
   - **Value** : `postgresql://postgres:TON_MOT_DE_PASSE@abc123.supabase.co:5432/postgres`
5. Sauvegarde et redéploie

---

## ⚠️ IMPORTANT : Sécurité

- ❌ **NE PAS** committer la connection string dans Git
- ✅ Utilise toujours des **variables d'environnement**
- ✅ Garde le `.env` local **dans `.gitignore`**
- ✅ Dès que tu as un problème, **réinitialise le mot de passe** dans Supabase

### Comment réinitialiser le mot de passe ?

1. **Settings → Database**
2. **Reset Database Password** (bouton en bas)
3. Une nouveau mot de passe est généré automatiquement
4. Copie la nouvelle connection string

---

## 🔍 Troubleshooting

### Error : "connection refused"
→ Vérifie que tu utilises la bonne **Host** (avec `.supabase.co`)

### Error : "authentication failed"
→ Réinitialise le password Supabase → copie la nouvelle URI

### Error : "database does not exist"
→ La base s'appelle `postgres` (pas le nom de ton projet)

---

## ✅ Checklist avant de migrer

- [ ] Tu as créé un **projet Supabase**
- [ ] Tu as exécuté le **SQL schema** (supabase_schema.sql)
- [ ] Tu as copié la **Connection String URI**
- [ ] Tu as testé en locale : `export DATABASE_URL='...'`
- [ ] Aucune erreur lors du `python3 migrate_to_postgres.py`
- [ ] Les données s'affichent sur **Supabase Dashboard**
