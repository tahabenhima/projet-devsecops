# LogParser Service - Guide de Test

## Prérequis

- Docker & Docker Compose
- Le service doit être lancé : `docker-compose up -d`

## Endpoint Principal

**POST** `http://localhost:8000/logs/parse`

## Exemples de Tests

### 1. Test Basique - Détection de Secrets

**Commande :**
```bash
curl -X POST http://localhost:8000/logs/parse \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Build started. AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
    "metadata": {"test": "secret-detection"}
  }'
```

**Résultat attendu :**
- Détection d'une clé AWS
- Retour d'un ID MongoDB

### 2. Test Détection d'Erreurs

**Commande :**
```bash
curl -X POST http://localhost:8000/logs/parse \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Deployment started\nError: Connection refused\nFailed to connect to database",
    "metadata": {"test": "error-detection"}
  }'
```

**Résultat attendu :**
- Détection de "Error" et "Failed"

### 3. Test Détection d'URLs

**Commande :**
```bash
curl -X POST http://localhost:8000/logs/parse \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Check documentation at https://docs.example.com/guide",
    "metadata": {"test": "url-detection"}
  }'
```

**Résultat attendu :**
- Détection de l'URL

### 4. Test Complet (Secrets + Erreurs + URLs)

**Commande :**
```bash
curl -X POST http://localhost:8000/logs/parse \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Pipeline started\nAPI_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwx\nError: Deployment failed\nVisit https://help.example.com",
    "metadata": {"test": "full-analysis"}
  }'
```

**Résultat attendu :**
- 1 secret détecté (GitHub token)
- 2 erreurs détectées ("Error", "failed")
- 1 URL détectée

## Test avec Fichier JSON

**Créer un fichier `test.json` :**
```json
{
  "content": "DB_PASSWORD=super_secret_123\nFatal error occurred",
  "metadata": {"source": "manual-test"}
}
```

**Tester :**
```bash
curl -X POST http://localhost:8000/logs/parse \
  -H "Content-Type: application/json" \
  -d @test.json
```

## Vérifier le Service

**Healthcheck :**
```bash
curl http://localhost:8000/
```

**Résultat attendu :**
```json
{"message": "LogParser Service is running"}
```

## Structure de la Réponse

```json
{
  "status": "success",
  "data": {
    "timestamp": "2025-11-23T17:00:00.000000",
    "metadata": { ... },
    "analysis": {
      "secrets": [
        {
          "type": "Potential Secret",
          "match": "PASSWORD=xxx",
          "position": [10, 25]
        }
      ],
      "errors": [ ... ],
      "urls": [ ... ]
    },
    "original_content_preview": "...",
    "_id": "mongodb_id"
  }
}
```

## Patterns Détectés

### Secrets
- `password=xxx`, `secret=xxx`, `token=xxx`
- Clés AWS : `AKIA...`
- Tokens GitHub : `ghp_...`

### Erreurs
- `error`, `exception`, `fail`, `fatal`

### URLs
- Toute URL commençant par `http://` ou `https://`
