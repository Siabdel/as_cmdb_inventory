La commande que tu proposes est presque bonne, il manque juste un espace et un `q` pour ne récupérer que les IDs.

### Pour supprimer tous les conteneurs arrêtés

```bash
docker rm $(docker ps -aq)
```

- `docker ps -a` : liste tous les conteneurs.  
- `-q` : n’affiche que les IDs, ce que `docker rm` attend.  

### Pour supprimer **tous** les conteneurs (même en cours d’exécution)

```bash
docker rm -f $(docker ps -aq)
```

`-f` force l’arrêt puis la suppression des conteneurs. À utiliser avec prudence.
