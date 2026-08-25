# 🎓 Skill Badge Platform

Plateforme intelligente d'évaluation de compétences par IA et de délivrance de badges numériques sécurisés par blockchain.

**Stage d'été 2026** — Encadrantes : Mme Souha Bennani & Mme Feriel Abbes
**Équipe :** Heeba Souaf & Wassim Kallel

---

## 📌 État actuel du dépôt (résumé simple)

**Branche `main`** contient actuellement, complet et fonctionnel :
- Gestion des utilisateurs (inscription/connexion, rôles étudiant/instructeur)
- Évaluation des compétences par IA (Google Gemini)
- Gestion des badges numériques (génération SVG, standard OpenBadges 2.0)
- Intégration blockchain (ancrage et vérification on-chain)
- Fonctionnalités instructeur (domaines d'enseignement, suivi des étudiants, suggestions d'activités)

**Branche `feature/student-interface`** (en attente de revue/merge) contient l'interface web complète :
- Page d'authentification commune (`index.html`)
- Dashboard étudiant (`student.html`)
- Dashboard instructeur (`instructor.html`)
- Le champ `fullname` (nom complet) pour un affichage correct sur les badges
- Le système complet de suggestions d'activités avec réponse étudiant et suivi instructeur

**Branches historiques (déjà mergées dans `main`, conservées pour référence) :**
- `feature/Gestion_de_badges`
- `feature/blockchain-setup`
- `feature/instructor-domains`

**Tag `pre-instructor-domains`** — bookmark fixe sur l'état de `main` juste avant l'ajout des fonctionnalités instructeur, au cas où un retour en arrière serait nécessaire.

---

## 🛠️ Stack technique

| Couche | Technologie |
|---|---|
| Backend | Python / FastAPI |
| Base de données | SQLite (SQLAlchemy) |
| Sécurité | JWT (python-jose) / bcrypt (passlib) |
| Intelligence Artificielle | Google Gemini API |
| Blockchain | Solidity / Web3.py / Ganache (local) |
| Frontend | HTML / CSS / JavaScript (vanilla, sans framework) |

---

## 📁 Structure du projet

```
STAGE/
├── main.py                    # Point d'entrée, toutes les routes API
├── models.py                  # Modèles SQLAlchemy (User, Assessment, Badge, InstructorDomain, SuggestedActivity)
├── schemas.py                 # Schémas Pydantic (validation des requêtes/réponses)
├── auth.py                    # JWT, hashing des mots de passe, require_role()
├── database.py                # Configuration SQLite
├── grader.py                  # Évaluation IA (Gemini)
├── badge_service.py           # Génération de badges (SVG + logique d'éligibilité)
├── blockchain_service.py      # Logique Web3 (hachage, ancrage, vérification)
├── BadgeRegistry.sol          # Smart contract Solidity
├── contract_abi.json          # ABI du smart contract
├── rubric.md                  # Grille de compétences utilisée par l'IA
├── requirements.txt           # Dépendances Python
├── .gitignore
├── .env                       # Secrets (NON versionné)
├── static/badges/             # Images SVG des badges générés
└── Frontend/
    ├── index.html              # Point d'entrée : connexion / inscription (rôle-neutre)
    ├── student.html             # Dashboard étudiant
    └── instructor.html           # Dashboard instructeur
```

---

## ⚙️ Configuration de l'environnement

Crée un fichier `.env` à la racine du projet :

```
# Authentification & Base de données
JWT_SECRET_KEY=<valeur secrète longue et aléatoire>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
DATABASE_URL=sqlite:///./users.db

# IA
GEMINI_API_KEY=<clé_api_google_ai>

# Blockchain
WEB3_PROVIDER_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=<adresse du contrat déployé localement>
ISSUER_ADDRESS=<adresse du compte émetteur (Ganache)>
PRIVATE_KEY=<clé privée du compte émetteur (Ganache)>
```

⚠️ **Ne jamais commit ce fichier.** `JWT_SECRET_KEY` doit être identique entre coéquipiers (sinon les tokens générés par l'un ne sont pas valides pour l'autre). `GEMINI_API_KEY`, `CONTRACT_ADDRESS`, `ISSUER_ADDRESS` et `PRIVATE_KEY` peuvent être propres à chaque machine (voir section Blockchain ci-dessous).

---

## 🚀 Installation

```bash
git clone https://github.com/heeba-sf/skill-badge-platform.git
cd skill-badge-platform

python -m venv .venv
# Windows :
.\.venv\Scripts\Activate.ps1
# Mac/Linux :
source .venv/bin/activate

python -m pip install -r requirements.txt
```

### Lancer le serveur

```bash
python -m uvicorn main:app
```
*(Utiliser `python -m uvicorn` plutôt que `uvicorn` directement si une Application Control Policy bloque l'exécutable sur Windows.)*

Accès : `http://127.0.0.1:8000/docs` (documentation interactive Swagger)

### ⚠️ Réinitialisation de la base de données

À chaque fois qu'un changement de schéma est mergé (nouvelle colonne/table), supprime et régénère la base locale :
```bash
Remove-Item users.db
python -m uvicorn main:app
```

---

## 🖥️ Utiliser l'interface web

Ouvre `Frontend/index.html` directement dans un navigateur (le backend doit être lancé en parallèle).

1. Choix : se connecter ou créer un compte
2. Inscription : choix du rôle (étudiant/instructeur) → informations du compte → si instructeur, sélection des domaines d'enseignement
3. Redirection automatique vers `student.html` ou `instructor.html` selon le rôle

**Espace étudiant :** parcourir les compétences, soumettre un travail (assignment/project), voir le résultat de l'évaluation IA, consulter ses badges, voir et répondre aux suggestions reçues des instructeurs.

**Espace instructeur :** voir ses domaines d'enseignement, la liste des étudiants actifs dans ces domaines, le rapport détaillé de chaque étudiant, envoyer des suggestions d'activités et suivre les réponses.

---

## ⛓️ Configuration blockchain (optionnel, pour tester l'ancrage)

1. Installer Ganache : `npm install -g ganache`
2. Lancer un nœud local :
   ```bash
   npx ganache --wallet.mnemonic "votre phrase mnémonique"
   ```
3. Déployer `BadgeRegistry.sol` via [Remix IDE](https://remix.ethereum.org) :
   - Environment : "Custom - External Http Provider" → `http://127.0.0.1:8545`
   - **Important :** définir l'EVM Version sur `shanghai` dans les options avancées du compilateur (Ganache par défaut ne supporte pas les versions plus récentes comme `cancun`, ce qui cause une erreur `invalid opcode` sinon)
4. Copier l'adresse du contrat déployé et les identifiants du compte utilisé dans `.env`

---

## 🔄 Workflow Git

On ne travaille jamais directement sur `main`.

```bash
git checkout main
git pull origin main
git checkout -b feature/nom-de-ta-tache
# ... travail, commits réguliers ...
git push -u origin feature/nom-de-ta-tache
```

Puis ouvrir une Pull Request sur GitHub. **On ne merge jamais sa propre PR sans relecture de l'autre**, même rapide.

---

## 👥 Répartition du travail

| Module | Statut | Responsable |
|---|---|---|
| Gestion des utilisateurs | ✅ Terminé | Heeba |
| Évaluation IA des compétences | ✅ Terminé | Heeba |
| Gestion des badges | ✅ Terminé | Wassim |
| Intégration blockchain | ✅ Terminé | Wassim |
| Interface web (auth, étudiant, instructeur) | ✅ Terminé (branche `feature/student-interface`, en revue) | Wassim & Heeba |

---

## 🆘 Dépannage

| Problème | Cause | Solution |
|---|---|---|
| `pip` non reconnu | PATH manquant | `python -m pip install -r requirements.txt` |
| `uvicorn.exe` bloqué (Application Control Policy) | Politique Windows | Utiliser `python -m uvicorn main:app` |
| `Failed to fetch` dans `/docs` | Serveur arrêté | Relancer `python -m uvicorn main:app` |
| `table X has no column named Y` | Schéma changé, DB non régénérée | Supprimer `users.db` et relancer |
| 401 Unauthorized | Token expiré ou absent | Refaire `/login` et ré-autoriser |
| 403 Forbidden sur `/instructor/...` | Compte non-instructeur | Comportement attendu (`require_role`) |
| `VM Exception: invalid opcode` (blockchain) | Mismatch de version EVM entre Remix et Ganache | Recompiler avec EVM Version = `shanghai` dans Remix |
| `insufficient funds for gas` | Compte émetteur non financé sur cette instance Ganache | Vérifier que `ISSUER_ADDRESS`/`PRIVATE_KEY` correspondent à un compte de l'instance Ganache active |
| Erreur liée au modèle Gemini | Modèle déprécié | Vérifier le nom du modèle dans `grader.py` sur la documentation Google |

---

## 📚 Points clés pour le rapport final

- **Prompt injection** : testé sur le module d'évaluation IA — le modèle résiste aux tentatives directes d'instructions injectées dans les soumissions
- **Sécurité smart contract** : `BadgeRegistry.sol` testé avec des cas d'accès non autorisé (`onlyOwner`) et de doublons — comportement validé par des tests Solidity dédiés
- **Standard OpenBadges 2.0** : les badges générés sont conformes au format d'assertion standard, incluant émetteur, critères, et vérification
- **Séparation des rôles** : contrôle d'accès basé sur les rôles (`require_role`) appliqué à toutes les routes instructeur
