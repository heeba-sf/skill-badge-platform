# Skill Badge Platform

Plateforme intelligente d'évaluation de compétences par IA et de délivrance de badges numériques sécurisés par blockchain.

**Stage d'été 2026** — Encadrantes : Mme Souha Bennani & Mme Feriel Abbes

---

## Stack technique

- **Backend :** Python / FastAPI
- **Base de données :** SQLite (via SQLAlchemy)
- **Authentification :** JWT (python-jose) + bcrypt (passlib)
- **IA :** Google Gemini API (google-generativeai)
- **Blockchain :** à venir (Ethereum / Solidity / Web3.py)

---

## Structure du projet

```
STAGE/
├── main.py            # Point d'entrée de l'application, déclaration des routes
├── models.py           # Modèles SQLAlchemy (tables : users, assessments)
├── schemas.py           # Schémas Pydantic (validation des requêtes/réponses)
├── auth.py              # Logique JWT, hashing des mots de passe, dépendances d'authentification
├── database.py            # Connexion et session à la base de données
├── grader.py               # Logique d'évaluation par IA (appel à Gemini)
├── rubric.md                # Grille de compétences utilisée pour l'évaluation IA
├── requirements.txt          # Dépendances Python
├── .gitignore                # Fichiers/dossiers exclus du dépôt Git
└── .env                       # Variables secrètes (NON versionné — à créer localement)
```

---

## Installation (première fois sur ta machine)

### 1. Cloner le dépôt

```bash
git clone https://github.com/heeba-sf/skill-badge-platform.git
cd skill-badge-platform
```

### 2. Créer l'environnement virtuel

```bash
python -m venv .venv
```

Activer l'environnement :

- **Windows (PowerShell) :**
  ```bash
  .\.venv\Scripts\Activate.ps1
  ```
- **Mac/Linux :**
  ```bash
  source .venv/bin/activate
  ```

Tu dois voir `(.venv)` apparaître au début de ta ligne de commande.

### 3. Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

### 4. Créer le fichier `.env`

Ce fichier n'est **pas** inclus dans le dépôt (il contient des secrets). Crée-le manuellement à la racine du projet avec ce contenu :

```
JWT_SECRET_KEY=<demande la valeur à Heeba>
GEMINI_API_KEY=<demande la valeur à Heeba, ou génère la tienne sur https://aistudio.google.com>
```

⚠️ Ne jamais commit ce fichier ni le partager publiquement.

### 5. Lancer le serveur

```bash
uvicorn main:app
```

Tu dois voir :
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 6. Tester

Ouvre `http://127.0.0.1:8000/docs` dans ton navigateur — c'est l'interface de test intégrée de FastAPI (Swagger UI).

Ordre de test recommandé :
1. `POST /register` — crée un compte test
2. `POST /login` — récupère un `access_token`
3. Clique sur **Authorize** (en haut à droite) et colle le token
4. `GET /me` — vérifie que l'authentification fonctionne
5. `POST /submit` — teste l'évaluation IA avec un exemple de soumission

---

## Workflow Git (important — à lire avant de coder)

On ne travaille **jamais directement sur `main`**. Chacun travaille sur sa propre branche.

### Avant de commencer une tâche

```bash
git checkout main
git pull origin main
```

### Créer une branche pour ta tâche

```bash
git checkout -b feature/nom-de-ta-tache
```

Exemples : `feature/badge-module`, `feature/blockchain-setup`

### Pendant que tu travailles

Commit régulièrement, avec des messages clairs :

```bash
git add .
git commit -m "Ajout de la génération de badges"
```

### Une fois ta tâche terminée et testée

```bash
git push -u origin feature/nom-de-ta-tache
```

Puis va sur GitHub → tu verras une bannière "Compare & pull request" → clique dessus → décris brièvement ce que tu as fait → ouvre la Pull Request.

**On ne merge jamais sa propre Pull Request sans que l'autre l'ait relue**, même rapidement — ça permet à chacun de comprendre l'ensemble du projet, pas seulement sa propre partie.

---

## Répartition actuelle du travail

| Module | Statut | Responsable |
|---|---|---|
| Gestion des utilisateurs | ✅ Terminé | Heeba |
| Évaluation IA des compétences | ✅ Fonctionnel, tests de sécurité en cours | Heeba |
| Gestion des badges | 🔜 À venir | — |
| Intégration blockchain | 🔜 À venir | — |
| Interface web | 🔜 À venir | — |

*(à mettre à jour au fur et à mesure)*

---

## En cas de problème

- **`pip` non reconnu :** utiliser `python -m pip install -r requirements.txt` au lieu de `pip install ...`
- **Erreur "Failed to fetch" dans `/docs` :** le serveur n'est probablement plus lancé, relancer avec `uvicorn main:app`
- **401 Unauthorized sur `/submit` ou `/me` :** le token a expiré ou n'a pas été collé dans "Authorize" — refaire `/login` et ré-autoriser
- **Erreur liée au modèle Gemini :** vérifier que le nom du modèle utilisé dans `grader.py` est toujours valide (Google déprécie régulièrement d'anciens modèles) — voir https://ai.google.dev/gemini-api/docs/models

Pour toute autre erreur, contacter Heeba avant de push sur ta branche.
