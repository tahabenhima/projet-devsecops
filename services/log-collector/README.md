# LogCollector Service

Ce microservice est responsable de la collecte des logs CI/CD.

## Prérequis

- Node.js
- Docker & Docker Compose (pour MongoDB)

## Installation

```bash
cd services/log-collector
npm install
```

## Démarrage

1. Lancer la base de données MongoDB :
   ```bash
   # À la racine du projet
   docker-compose up -d
   ```

2. Lancer le service :
   ```bash
   cd services/log-collector
   npm start
   ```
   Le serveur démarrera sur le port `3000`.

## Utilisation de l'API

### 1. Envoyer des logs (Upload)

**Endpoint** : `POST /logs/upload`

**Exemple avec cURL** :
```bash
curl -X POST http://localhost:3000/logs/upload \
  -H "Content-Type: application/json" \
  -d '{
    "source": "github",
    "repo": "mon-projet",
    "pipelineId": "12345",
    "content": "Log content here...",
    "metadata": { "author": "user" }
  }'
```

**Réponse (Succès)** :
```json
{
  "message": "Log uploaded successfully",
  "logId": "654..."
}
```

### 2. Vérifier l'état (Healthcheck / Stub)

**Endpoint** : `GET /logs/github`

Pour l'instant, cet endpoint retourne "Not implemented" mais confirme que le serveur répond.
