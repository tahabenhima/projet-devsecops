# FixSuggester Microservice

Microservice pour générer des correctifs automatiques (patches YAML) pour les vulnérabilités détectées dans les workflows GitHub Actions.

## Fonctionnalités

- **Verrouillage de versions** : Épingle les GitHub Actions à des SHAs de commit spécifiques
- **Restriction de permissions** : Ajoute des permissions minimales selon le principe du moindre privilège
- **Chiffrement de secrets** : Remplace les secrets en dur par des références GitHub Secrets
- **Amélioration du hardening** : Ajoute des mesures de sécurité (concurrency, timeouts, etc.)

## Technologies

- **Framework** : FastAPI
- **Base de données** : PostgreSQL
- **Templates** : Jinja2
- **Diff Generation** : diff-match-patch
- **Validation** : Pydantic

## API Endpoints

### POST /fix
Génère des suggestions de correctifs pour les vulnérabilités détectées.

**Request:**
```json
{
  "workflow_yaml": "string",
  "vulnerabilities": [
    {
      "type": "unpinned_action | excessive_permissions | hardcoded_secret | weak_hardening",
      "line": 10,
      "details": "Description of the issue"
    }
  ]
}
```

**Response:**
```json
{
  "fixes": [
    {
      "id": 1,
      "vulnerability_type": "unpinned_action",
      "description": "Pinned GitHub Actions to specific commit SHAs",
      "diff": "--- original.yml\n+++ fixed.yml\n...",
      "severity": "high",
      "auto_applicable": true
    }
  ],
  "original_yaml": "...",
  "fixed_yaml": "..."
}
```

### GET /fixes
Récupère toutes les suggestions de correctifs stockées.

### GET /fixes/{fix_id}
Récupère une suggestion de correctif spécifique par ID.

### GET /health
Vérification de l'état du service.

## Installation

### Avec Docker Compose

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs
docker-compose logs fix-suggester

# Arrêter les services
docker-compose down
```

### Tests

```bash
# Tester l'endpoint /fix
curl -X POST http://localhost:8002/fix \
  -H "Content-Type: application/json" \
  -d @test_fix_suggester.json

# Vérifier l'état du service
curl http://localhost:8002/health

# Lister toutes les suggestions
curl http://localhost:8002/fixes
```

## Types de Correctifs

### 1. Version Locking (unpinned_action)
**Problème** : Actions utilisant des tags comme `@main` ou `@v1`  
**Correctif** : Épingle à un SHA de commit spécifique avec commentaire de version  
**Sévérité** : High

### 2. Permission Restriction (excessive_permissions)
**Problème** : Permissions manquantes ou excessives  
**Correctif** : Ajoute des permissions minimales requises  
**Sévérité** : Medium

### 3. Secret Encryption (hardcoded_secret)
**Problème** : Secrets ou credentials en dur dans le code  
**Correctif** : Remplace par la syntaxe `${{ secrets.* }}`  
**Sévérité** : Critical

### 4. Hardening Improvements (weak_hardening)
**Problème** : Manque de mesures de sécurité  
**Correctif** : Ajoute concurrency control, timeouts, conditions  
**Sévérité** : Low

## Structure du Projet

```
fix-suggester/
├── Dockerfile
├── requirements.txt
├── README.md
└── src/
    ├── main.py              # Application FastAPI
    ├── routes.py            # Endpoints API
    ├── models.py            # Modèles SQLAlchemy
    ├── database.py          # Configuration BDD
    ├── fix_engine.py        # Logique de génération de correctifs
    ├── diff_generator.py    # Génération de diffs YAML
    └── templates/           # Templates Jinja2
        ├── version_lock.yaml
        ├── permission_restriction.yaml
        ├── secret_encryption.yaml
        └── hardening.yaml
```

## Base de Données

Le service stocke les suggestions de correctifs dans PostgreSQL avec le modèle suivant :

```
fix_suggestions
├── id (PK)
├── vulnerability_type
├── original_yaml
├── fixed_yaml
├── diff
├── description
├── severity
├── auto_applicable
└── timestamp
```

## Configuration

Variables d'environnement :
- `DATABASE_URL` : URL de connexion PostgreSQL (défaut: `postgresql://user:password@postgres:5432/vulndetector`)

## Développement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer en mode développement
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Intégration avec d'autres services

Le FixSuggester peut être intégré avec :
- **VulnDetector** : Pour recevoir automatiquement les vulnérabilités détectées
- **LogParser** : Pour enregistrer les correctifs appliqués
- **CI/CD Pipeline** : Pour appliquer automatiquement les correctifs sûrs
