

# Testing Setup and Procedures

## Testing Tools

The testing setup for this project uses the following tools:

- **Pytest**: For running tests.
- **pytest-django**: For Django-specific test utilities.
- **pytest-cov**: For generating coverage reports.
- **pytest-factoryboy**: For creating test data using factories.
- **factory-boy**: For defining test factories.
- **Faker**: For generating fake data.

## Testing Configuration

The testing configuration is defined in the `pyproject.toml` file under the `[tool.pytest.ini_options]` section. Here are the key configurations:

- **Test Options**:
  - `--reuse-db`: Reuse the database between test runs to speed up testing.
  - `--no-migrations`: Skip running database migrations during tests.
  - `--tb=short`: Use a short traceback format for test failures.
  - `--strict-markers`: Ensure all markers are defined.
  - `--strict-config`: Ensure the configuration is valid.

- **Test Paths**: Tests are located in the `tests` directory.
- **Python Files**: Test files follow the pattern `test_*.py`.
- **Python Classes**: Test classes follow the pattern `Test*`.
- **Python Functions**: Test functions follow the pattern `test_*`.
- **Markers**:
  - `unit`: Unit tests.
  - `integration`: Integration tests.
  - `api`: API endpoint tests.
  - `models`: Model tests.
  - `slow`: Slow running tests.

- **Coverage Configuration**:
  - **Source**: Coverage is measured for the `inventory` module.
  - **Omit**: Exclude migrations, tests, and management commands from coverage reports.
  - **Branch**: Measure branch coverage.
  - **Exclude Lines**: Exclude lines that match certain patterns from coverage reports.

## Running Tests

To run the tests, navigate to the project root directory and execute the following command:

```sh
pytest
```

To generate a coverage report, use the following command:

```sh
pytest --cov=inventory --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov` directory.

## Best Practices

- **Use Factories**: Use `factory-boy` to create test data. This ensures that your tests are consistent and easy to maintain.
- **Use Markers**: Use the defined markers to categorize your tests. This helps in running specific types of tests.
- **Keep Tests Independent**: Ensure that each test is independent and can be run in isolation.
- **Use Mocking**: Use mocking to isolate the components being tested.
- **Write Descriptive Test Names**: Use descriptive test names to make it clear what each test is testing.
- **Run Tests Regularly**: Run tests regularly to catch issues early.

---

#### Prompt : 

analyser et produire un cahier de charge + prompt :
la partie  frontend  backend (HTML5/bootstrap/jquery/vue.js/axios correspondant a ce business  pour les intervenant de la societe IT  pour leur activite sachant qu'une gd partie du travail se fait cote admin  du backend  et les ecran vitrine pour les autre 
Integrer un moteur de rechreche , module du scanner  QRCode ou code a barre 
et en consommant principalement les api du backend .
separer le admin/ et django-admin/ qui contient fontion system users groups , auth ect ..

-----------------------

### Debug curl

* ```
  curl -X POST http://localhost:8000/api/auth/token/ -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'
  ```

  

* ```
  cd backend && . ../venv/bin/activate && python manage.py shell -c "
  from django.contrib.auth.models import User
  u = User.objects.get(username='admin')
  u.set_password('admin123')
  u.save()
  print('Password updated')
  "
  ```

* ```shell
  # Maintenant, je vais tester à nouveau l'authentification.
  curl -X POST http://localhost:8000/api/auth/token/ -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'
  ```

* ```shell
  ## Super ! L'authentification fonctionne et retourne un token. Maintenant, je vais tester l'endpoint `/api/auth/user/` avec ce token pour vérifier que la vue `CurrentUserView` fonctionne.
  
  #Je vais d'abord extraire le token de la réponse précédente (8949e598ef8f975fc25747349daa50aad09ed4a7) et l'utiliser dans un curl.
  
  curl -X GET http://localhost:8000/api/auth/user/ -H "Authorization: Token 8949e598ef8f975fc25747349daa50aad09ed4a7"
  ```

* ```shell
  # Vérifier le chargement des assets Bootstrap
  curl -I http://localhost:3000/src/main.js
  ```

* ```shell
  # Le serveur frontend tourne sur le port 3000. Je vais tester l'accès à ce port.
  curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
  ```

  

* ```shell
  #  le serveur Vite écoute sur le port 3000, pas 5173. Donc je dois utiliser http://localhost:3000/. Je vais tester avec curl.
  curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/
  ```

* ```
  # vérifier que la route /dashboard affiche bien LandingPage. Je vais faire un test rapide avec curl pour voir si le contenu contient "Bienvenue sur notre Application de Gestion d'Inventaire".
  curl -s http://localhost:3000/dashboard | grep -o "Bienvenue sur notre Application de Gestion d'Inventaire"
  ```

* ```shell
  # je vais tester l'API avec ce token pour vérifier que les données sont correctes.
  
  
  cd backend && . ../venv/bin/activate && python manage.py shell -c "
  from django.contrib.auth.models import User
  from rest_framework.authtoken.models import Token
  user = User.objects.first()
  if user:
      token, created = Token.objects.get_or_create(user=user)
      print(token.key)
  else:
      print('No user')
  "
  
  ```

  ```shell
  ## Je vais maintenant tester rapidement la configuration en vérifiant que les fichiers sont syntaxiquement valides :
  $ docker-compose config
  ```

* ```shell
  ## Maintenant testons /api/v1/inventory/assets/by-category/ :
  curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Token 8949e598ef8f975fc25747349daa50aad09ed4a7" http://localhost:8000/api/v1/inventory/assets/by-category/
  
  ```

  

* ```
  ## e vais exécuter une commande pour voir les dernières lignes du serveur Django.
  sleep 3 && echo "Checking logs..."
  ```

* ```shell
  # Je vais créer un token de test en utilisant la commande createsuperuser et obtain_auth_token. Mais d'abord, vérifions si un utilisateur existe. Je vais exécuter une commande Django pour créer un token et tester.
  
  # Je vais utiliser execute_command pour exécuter un script Python dans le backend.
  
  cd backend && . ../venv/bin/activate && python manage.py shell -c "
  from django.contrib.auth import get_user_model
  from rest_framework.authtoken.models import Token
  User = get_user_model()
  user = User.objects.filter(is_superuser=True).first()
  if user:
      token, created = Token.objects.get_or_create(user=user)
      print('Token:', token.key)
  else:
      print('No superuser found')
  "
  
  ```

* ```
  # Pour confirmer, testons avec une méthode non supportée comme DELETE (qui n'est pas mappée non plus). Exécutons une requête DELETE sans token
  cd backend && curl -X PUT -H "Content-Type: application/json" -d '{"name":"Test"}' http://localhost:8000/api/v1/assets/198/ 2>&1 | head -5
  
  ```

* ```shell
  # Je vais plutôt vérifier que l'API PUT fonctionne avec un token valide en utilisant curl avec un token que je peux extraire de la base de données. Je vais exécuter une commande Django pour générer un token pour l'utilisateur superuser (s'il existe). Je vais d'abord vérifier si un superuser existe.
  
  Je vais exécuter une commande dans le terminal du backend pour obtenir un token.
  cd backend && . ../venv/bin/activate && python -c "
  from django.contrib.auth import get_user_model
  from rest_framework.authtoken.models import Token
  User = get_user_model()
  try:
      user = User.objects.filter(is_superuser=True).first()
      if user:
          token, created = Token.objects.get_or_create(user=user)
          print(token.key)
      else:
          print('No superuser found')
  except Exception as e:
      print('Error:', e)
  " 2>&1
  ```

  

* ```shell
  # Maintenant, je vais tester une requête PUT sur l'asset 198 avec ce token pour vérifier que l'API fonctionne.
  cd backend && curl -X PUT -H "Content-Type: application/json" -H "Authorization: Token 8949e598ef8f975fc25747349daa50aad09ed4a7" -d '{"name":"Test Updated via API"}' http://localhost:8000/api/v1/assets/198/ 2>&1
  ```

* ```shell
  ## je vais tester une requête PUT sur l'asset 198 avec ce token pour vérifier que l'API fonctionne.
  cd backend && curl -X PUT -H "Content-Type: application/json" -H "Authorization: Token 8949e598ef8f975fc25747349daa50aad09ed4a7" -d '{"name":"Test Updated via API"}' http://localhost:8000/api/v1/assets/198/ 2>&1
  
  ```

* ```shell
  # Je vais maintenant tester une mise à jour complète avec toutes les valeurs requises. Je vais créer un JSON avec les données actuelles mais en modifiant le nom. Utilisons curl avec le token.
  
  Je vais extraire les valeurs nécessaires de la réponse précédente (j'ai vu category_id: 29, brand_id: 29, current_location_id: 28, model: "RS1221+", serial_number: "SN-2603161", etc.). Je vais aussi inclure internal_code (non présent dans la réponse? peut-être internal_code n'est pas un champ du modèle? Regardons le modèle. Mais pour l'instant, je vais l'omettre.
  
  
  cd backend && curl -X PUT -H "Content-Type: application/json" -H "Authorization: Token 8949e598ef8f975fc25747349daa50aad09ed4a7" -d '{
    "name": "Synology RS1221+ Updated",
    "model": "RS1221+",
    "serial_number": "SN-2603161",
    "category_id": 29,
    "brand_id": 29,
    "current_location_id": 28,
    "status": "active",
    "condition_state": "new",
    "purchase_date": "2025-02-04",
    "purchase_price": "572.92",
    "warranty_end": "2028-11-21",
    "description": "Ensemble sérieux lit danser nouveau finir armer. Situation jaune brûler dont longtemps immobile. Objet interroger révolution long lèvre."
  }' http://localhost:8000/api/v1/assets/198/ 2>&1
  ```

* ```shell
  ## ans les logs du terminal 1, on voit "Bad Request: /api/v1/assets/" mais pas le détail. Peut-être que Django ne logue pas le contenu de la réponse. Je vais exécuter une commande Python dans le shell Django pour tester le serializer.
  
  Je vais créer un script de test rapide
  cd backend && . ../venv/bin/activate && python manage.py shell -c "
  from inventory.models import Asset, Category, Brand, Location
  from inventory.serializers import AssetDetailSerializer
  import json
  
  # Vérifier si le champ internal_code existe
  print('Champs du modèle Asset:', [f.name for f in Asset._meta.fields])
  print('internal_code présent?', 'internal_code' in [f.name for f in Asset._meta.fields])
  
  # Créer des instances de test si elles n'existent pas
  cat = Category.objects.first()
  brand = Brand.objects.first()
  loc = Location.objects.first()
  
  if cat and brand and loc:
      data = {
          'name': 'Test Asset',
          'model': 'Test Model',
          'serial_number': 'TEST123',
          'category_id': cat.id,
          'brand_id': brand.id,
          'current_location_id': loc.id,
          'status': 'active',
          'condition_state': 'new',
          'internal_code': 'PC-999',  # champ supplémentaire
          'notes': 'test notes'
      }
      serializer = AssetDetailSerializer(data=data)
      print('Serializer valide?', serializer.is_valid())
      print('Erreurs:', serializer.errors)
  else:
      print('Données de référence manquantes')
  "
  ```

* ```shell
  cd backend && . ../venv/bin/activate && curl -X POST http://localhost:8000/api/v1/assets/ \
    -H "Authorization: Token 8949e598ef8f975fc25747349daa50aad09ed4a7" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Test Asset Curl",
      "model": "Test Model",
      "serial_number": "CURL123",
      "category_id": 1,
      "brand_id": 1,
      "current_location_id": 1,
      "status": "active",
      "condition_state": "new"
    }'
  
  ```

  

* ```shell
  cd backend && . ../venv/bin/activate && curl -X POST http://localhost:8000/api/v1/assets/ \
    -H "Authorization: Token 8949e598ef8f975fc25747349daa50aad09ed4a7" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Test Asset No Category",
      "model": "Test Model",
      "serial_number": "NOCAT123",
      "status": "active",
      "condition_state": "new"
    }'
  
  ```

  

* ```shell
  ## Je vais d'abord examiner les logs du serveur Django pour voir plus de détails sur l'erreur 400. Je peux exécuter une commande pour voir les logs plus récents ou examiner le fichier de logs.
  
  
  cd backend && tail -f logs/django.log 2>/dev/null || echo "Log file not found"
  
  ```

* ```shell
  ## Je vois que le payload envoyé contient `category_id`, `brand_id`, `current_location_id`. Cependant, le serializer AssetDetailSerializer attend `category_id`, `brand_id`, `current_location_id` comme champs write-only (voir lignes 130-138). C'est correct.
  
  # Mais il y a un problème potentiel : le champ `internal_code` est présent dans le formulaire mais pas dans le payload (il est supprimé car il n'est pas inclus). Le modèle Asset n'a pas de champ `internal_code`. Cela pourrait causer une erreur si le backend s'attend à ce champ? Non, le serializer ne le mentionne pas.
  
  # Je dois vérifier les logs Django pour voir le détail de l'erreur 400. Je vais arrêter la commande tail et exécuter une commande pour voir les logs récents du serveur.
  
  
  cd backend && grep -A 5 -B 5 "Bad Request: /api/v1/assets/" logs/django.log 2>/dev/null | tail -30
  ```

  

* ```shell
  ## Je vois que la base URL est `http://localhost:8000/api`. Donc l'appel à `/v1/assets/` devient `http://localhost:8000/api/v1/assets/`. C'est correct.
  Maintenant, je dois comprendre pourquoi la requête échoue avec 400. Je vais faire un test manuel avec curl pour voir la réponse détaillée. D'abord, je vais vérifier si le serveur est en cours d'exécution et si je peux envoyer une requête POST
  
  Maintenant, je dois comprendre pourquoi la requête échoue avec 400. Je vais faire un test manuel avec curl pour voir la réponse détaillée. D'abord, je vais vérifier si le serveur est en cours d'exécution et si je peux envoyer une requête POST.
  
  Je vais exécuter une commande curl pour créer un asset avec des données minimales.
  
  
  $ url -X POST http://localhost:8000/api/v1/assets/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Token $(cat /tmp/token.txt 2>/dev/null || echo '')" \
    -d '{
      "name": "Test Asset",
      "model": "Test Model",
      "serial_number": "TEST123456",
      "status": "active",
      "condition_state": "new"
    }' -v 2>&1 | head -30
  
  ```

* ```shell
  ## Je vais maintenant examiner la réponse de l'API en activant le logging Django plus détaillé. Je peux ajouter un middleware de logging temporairement, mais c'est plus simple de regarder la réponse dans le terminal du serveur. Le serveur affiche "Bad Request: /api/v1/assets/" mais pas le détail. Peut-être que la réponse JSON contient des détails. Je vais essayer de capturer la requête avec un outil comme httpie ou curl avec un token valide.
  
  D'abord, je dois obtenir un token d'authentification. Je vais vérifier si un utilisateur existe et générer un token. Je vais exécuter une commande Django pour créer un token pour un utilisateur existant.
  
  
  
  
  $ python -c "import os os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_project.settings')
  import django
  django.setup()
  from django.contrib.auth.models import User
  from rest_framework.authtoken.models import Token
  user, created = User.objects.get_or_create(username='admin', defaults={'email':'admin@example.com'})
  if created:
      user.set_password('admin')
      user.save()
  token, created = Token.objects.get_or_create(user=user)
  print(token.key)
  " 2>/dev/null
  ```

  

* ```sh
  ## Le serveur a rechargé. Maintenant, je vais déclencher une nouvelle requête POST depuis le frontend pour voir les logs. Je vais demander à l'utilisateur de tester la création d'un asset, mais je peux aussi le faire moi-même via curl avec un token valide.
  
  Je vais d'abord essayer de me connecter via l'API pour obtenir un token. Je vais utiliser les identifiants par défaut (admin/admin). Je vais exécuter une commande curl pour obtenir un token et le stocker
  cd backend && curl -s -X POST http://localhost:8000/api/auth/token/ \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' 2>/dev/null | grep -o '"token":"[^"]*"' | cut -d'"' -f4
  ```

  

* ```sh
  ## Je vais maintenant déclencher une requête POST via curl avec des données minimales et un token valide. Je dois d'abord obtenir un token en créant un utilisateur via la console Django. Je vais exécuter une commande manage.py shell avec le bon environnement.
  $ cd backend && . ../venv/bin/activate && python manage.py shell << 'EOF'
  from django.contrib.auth.models import User
  from rest_framework.authtoken.models import Token
  user, created = User.objects.get_or_create(username='testuser', defaults={'email':'test@example.com'})
  if created:
      user.set_password('testpass')
      user.save()
  token, created = Token.objects.get_or_create(user=user)
  print(token.key)
  EOF
  # Super, j'ai un token : `dc5b3b3ebc310bf4476fd58ecf71c25e6dcc91e3`. Maintenant je vais envoyer une requête POST avec ce token et voir les logs.
  
  ## Je vais exécuter curl avec le token et des données minimales.
  cd backend && curl -X POST http://localhost:8000/api/v1/assets/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Token dc5b3b3ebc310bf4476fd58ecf71c25e6dcc91e3" \
    -d '{
      "name": "Test Asset",
      "model": "Test Model",
      "serial_number": "TEST1234567",
      "status": "active",
      "condition_state": "new"
    }' -v 2>&1 | tail -30	
  
  
  
  ```

  