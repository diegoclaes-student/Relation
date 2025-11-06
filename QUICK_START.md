# 🚀 Quick Start - Déploiement en 15 minutes

## Étape 1 : Supabase (5 min)

1. Va sur https://supabase.com → Sign in avec GitHub
2. New Project → Nom: `centrale-potins-maps`
3. Copie le mot de passe généré ✅
4. Region: Europe West → Create
5. Attends 2 min ⏱️
6. SQL Editor → New Query → Colle le SQL du `DEPLOYMENT_GUIDE.md` (PARTIE 1.2)
7. Run ✅
8. Settings → Database → Copie l'URI ✅

## Étape 2 : Migration des données (3 min)

```bash
# 1. Installe psycopg2
pip install psycopg2-binary

# 2. Configure l'URL (remplace par ton URL Supabase)
export DATABASE_URL='postgresql://postgres:TON_PASSWORD@db.xxx.supabase.co:5432/postgres'

# 3. Lance la migration
python3 migrate_to_postgres.py
```

## Étape 3 : GitHub (2 min)

```bash
# 1. Init Git (si pas déjà fait)
git init
git add .
git commit -m "Ready for deployment"

# 2. Crée un repo sur GitHub (PRIVÉ)
# 3. Push
git remote add origin https://github.com/TON-USERNAME/centrale-potins-maps.git
git push -u origin main
```

## Étape 4 : Vercel (5 min)

1. Va sur https://vercel.com → Continue with GitHub
2. New Project → Importe `centrale-potins-maps`
3. Environment Variables → Ajoute:
   - `DATABASE_URL` = ton URL Supabase
   - `SECRET_KEY` = génère avec `python -c 'import secrets; print(secrets.token_hex(32))'`
   - `ENVIRONMENT` = `production`
4. Deploy ✅
5. Attends 2 min
6. Ouvre l'URL fournie 🎉

## ✅ C'est en ligne !

Ton app est accessible sur: `https://ton-projet.vercel.app`

## 🔧 En cas de problème

1. **Erreur 500** → Vercel Dashboard → Function Logs
2. **DB error** → Vérifie le `DATABASE_URL`
3. **Module not found** → Vérifie `requirements.txt`

## 📚 Plus de détails

Voir `DEPLOYMENT_GUIDE.md` pour le guide complet.
