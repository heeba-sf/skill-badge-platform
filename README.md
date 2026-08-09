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

🎓 Skill Badge Platform — Blockchain Badge Anchoring & VerificationThis platform provides automated skill evaluations and issues verifiable, tamper-proof Open Badges 2.0 assertions. Badges are cryptographically hashed using SHA-256 and anchored to an Ethereum-compatible local blockchain (Ganache) via a custom Solidity smart contract (BadgeRegistry.sol).🛠️ Prerequisites & Local Setup1. RequirementsPython 3.10+Node.js & npm (to run Ganache)Remix IDE (browser-based) or Truffle/Hardhat for smart contract deployment2. Environment Configuration (.env)Create or verify the .env file in the project root with the following variables:Code snippetJWT_SECRET_KEY=change-me-to-a-long-random-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
DATABASE_URL=sqlite:///./users.db
GEMINI_API_KEY=your_gemini_api_key_here

# Blockchain / Web3 Configuration
WEB3_PROVIDER_URL=http://127.0.0.1:8545
ISSUER_ADDRESS=0x88e218f5279d75982a5Ac2FccB62612E20a6A3b7
PRIVATE_KEY=0x9f2b4375b583da3dc5458d8138bc3b12b90217f37024053c748fe68c3a75757f
CONTRACT_ADDRESS=0xa441e3bFBd6B0Ce296c7ee7D6f6DE53Ee618E3Cb
Note: Ensure key names in .env match exact spellings (WEB3_PROVIDER_URL and CONTRACT_ADDRESS) without missing characters or spaces.🚀 Running the Local ServicesStep 1: Start the Local Blockchain (Ganache)In a dedicated terminal, run:PowerShellnpx ganache
Confirm the terminal output shows: RPC Listening on 127.0.0.1:8545. Keep this process active.Step 2: Deploy BadgeRegistry.sol Smart ContractOpen Remix IDE.Load BadgeRegistry.sol from the project repository into Remix.In the Deploy & Run Transactions tab:Environment: Select Custom - External Http Provider and connect to [http://127.0.0.1:8545](http://127.0.0.1:8545).Account: Select Account 0 (0x88e2...).Click Deploy.Copy the deployed contract address (e.g., 0xa441e3...) and update CONTRACT_ADDRESS in your .env file.Step 3: Start the FastAPI Backend ServerIn your Python virtual environment terminal:PowerShelluvicorn main:app --reload
Access the interactive API documentation at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)🧪 Step-by-Step Testing & Verification GuideFollow this sequential workflow in Swagger UI ([http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)) to test complete badge creation, anchoring, and on-chain verification.Step 1: Authenticate UserExecute POST /register or POST /token to generate a JWT access token.Click Authorize at the top right of Swagger UI, paste the token, and click Authorize.Step 2: Earn a Skill BadgeOpen POST /submit.Submit an answer payload for evaluation:JSON{
  "code": "SELECT * FROM users WHERE username = 'admin' AND '1'='1';",
  "competency": "SQL Injection"
}
Open GET /badges/my-badges and click Execute.Locate your badge and copy its id string (e.g., a8b5c7c4-ace9-4cea-b9a3-ac152a0df30f).Step 3: Anchor Badge On-ChainOpen POST /badges/{badge_id}/anchor.Paste the badge_id into the path parameter box.Click Execute.Expected Output (200 OK):JSON{
  "message": "Badge successfully anchored on blockchain",
  "badge_id": "a8b5c7c4-ace9-4cea-b9a3-ac152a0df30f",
  "blockchain_tx": "0xd1377602cf3c1f8715e10ed33e401af4fb7d780b498c72bf3eea283654b26bba"
}
Step 4: Verify Badge Immutability On-ChainOpen GET /badges/{badge_id}/verify-on-chain.Paste the same badge_id.Click Execute.Expected Output (200 OK):JSON{
  "badge_id": "a8b5c7c4-ace9-4cea-b9a3-ac152a0df30f",
  "is_valid": true,
  "on_chain_hash": "0xc87f7f55257d930cccd3c6932dfd40db7135d97034ee4cec1842a0450db94e3f",
  "computed_hash": "0xc87f7f55257d930cccd3c6932dfd40db7135d97034ee4cec1842a0450db94e3f",
  "issuer": "0x88e218f5279d75982a5Ac2FccB62612E20a6A3b7",
  "block_timestamp": 1788856971
}
Success Criteria: "is_valid": true indicates the computed SHA-256 payload matches the hash immutably recorded in the smart contract.🔍 Troubleshooting & Edge CasesIssue / ErrorCauseResolutionis_valid: falsePayload canonicalization or timestamp microsecond mismatch.Ensure build_badge_assertion formats issuedOn with UTC Z format (%Y-%m-%dT%H:%M:%SZ).VM Exception: invalid opcodeBadge ID queried in GET /verify-on-chain does not exist in contract storage.Run POST /badges/{badge_id}/anchor first before attempting verification.Failed to connect to local Web3 RPCGanache node is offline or running on a non-standard port.Start npx ganache in terminal and confirm port 8545 is specified in .env.Badge already registeredRe-anchoring a badge ID that was previously stored on-chain.Smart contracts reject duplicate key registration. Generate a new badge or run GET /verify-on-chain.

## Répartition actuelle du travail

| Module | Statut | Responsable |
|---|---|---|
| Gestion des utilisateurs | ✅ Terminé | Heeba |
| Évaluation IA des compétences | ✅ Fonctionnel, tests de sécurité en cours | Heeba |
| Gestion des badges | ✅ Terminé | Wassim |
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

