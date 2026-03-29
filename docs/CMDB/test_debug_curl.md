# Commandes CURL pour le test et debug
J'ai créé un rapport Markdown contenant les commandes CURL utilisées dans les dernières tâches de debug. Ce fichier se trouve dans `docs/CMDB/test_debug_curl.md` et contient les commandes pour tester :

1. Vérification de l'existence des assets
2. Vérification du nombre d'assets
3. Test de recherche d'assets
4. Accès à l'admin Django
5. Vérification des URLs
6. Test de l'API d'assets
7. Test de l'API de recherche
8. Vérification des catégories
9. Vérification des marques
10. Vérification des emplacements

Ces commandes peuvent être utilisées pour diagnostiquer les problèmes d'administration et de recherche d'assets.

## Commandes utilisées dans les dernières tâches

### 1. Vérification de l'existence des assets
```bash
curl -X GET http://localhost:8000/api/v1/assets/ -H "Authorization: Token <token>"
```

### 2. Vérification du nombre d'assets
```bash
curl -X GET http://localhost:8000/api/v1/assets/stats/ -H "Authorization: Token <token>"
```

### 3. Test de recherche d'assets
```bash
curl -X GET "http://localhost:8000/api/v1/assets/?search=PC" -H "Authorization: Token <token>"
```

### 4. Accès à l'admin Django
```bash
curl -X GET http://localhost:8000/admin/assets/ -H "Cookie: sessionid=<session_id>"
```

### 5. Vérification des URLs
```bash
curl -X GET http://localhost:8000/admin/assets/ -H "Authorization: Token <token>"
```

### 6. Test de l'API d'assets
```bash
curl -X GET http://localhost:8000/api/v1/assets/1/ -H "Authorization: Token <token>"
```

### 7. Test de l'API de recherche
```bash
curl -X GET "http://localhost:8000/api/v1/assets/?search=test" -H "Authorization: Token <token>"
```

### 8. Vérification des catégories
```bash
curl -X GET http://localhost:8000/api/v1/assets/category/ -H "Authorization: Token <token>"
```

### 9. Vérification des marques
```bash
curl -X GET http://localhost:8000/api/v1/assets/brand/ -H "Authorization: Token <token>"
```

### 10. Vérification des emplacements
```bash
curl -X GET http://localhost:8000/api/v1/assets/location/ -H "Authorization: Token <token>"