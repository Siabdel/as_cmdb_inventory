## Pour supprimer toutes les images Docker, utilise cette commande :

### Supprimer toutes les images
```bash
docker rmi $(docker images -q)
```

### Supprimer toutes les images y compris les intermédiaires/orphelines
```bash
docker image prune -a -f
```

### Script complet (arrêt + suppression conteneurs + images)
```bash
#!/bin/bash
echo "🛑 Arrêt des conteneurs en cours..."
docker stop $(docker ps -q)

echo "🗑️ Suppression des conteneurs..."
docker rm $(docker ps -aq)

echo "🗑️ Suppression des images..."
docker rmi $(docker images -q)

echo "🧹 Nettoyage final..."
docker system prune -a -f
```

**Explications des options :**
- `docker images -q` : liste seulement les IDs des images
- `docker rmi` : remove image  
- `-f` : force la suppression
- `prune -a` : supprime toutes les images non utilisées

**⚠️ Attention :** Ces commandes sont **destructrices**. Sauvegarde tes données/volumes avant !
Pour supprimer **uniquement les images intermédiaires** (dangling/intermédiaires/orphelines) :

### 1. Voir les images intermédiaires
```bash
docker images -f "dangling=true"
```

### 2. Les supprimer
```bash
docker image prune -f
```
ou
```bash
docker image prune
```

### 3. Script complet pour nettoyage sélectif
```bash
#!/bin/bash
echo "📋 Images intermédiaires trouvées :"
docker images -f "dangling=true" -q | wc -l

echo "🗑️ Suppression des images intermédiaires..."
docker image prune -f

echo "✅ Nettoyage terminé !"
```

### Explications
- **Images "dangling"** = couches/images sans tag ET non référencées par une image "parent"  
- `docker image prune -f` supprime **seulement** ces images, garde tes images principales  
- `-f` évite la confirmation interactive  

**Parfait pour nettoyer après plusieurs `docker build` sans supprimer tes images utiles !**
**Non, les images prune (intermédiaires/dangling) ne sont pas totalement inutiles, mais elles sont superflues et gaspillent de l'espace.**

### Pourquoi elles existent
- Ce sont des **couches orphelines** créées lors des `docker build` multiples
- Quand tu refais un build, l'ancienne version perd son tag → devient "dangling"
- `<none>:<none>` dans `docker images`

### Pourquoi les supprimer
- **Occupent de l'espace disque** inutilement (souvent plusieurs GB)
- **Pas réutilisables** : aucun conteneur ne peut les lancer directement
- **Nettoient ton environnement** pour mieux voir tes vraies images

### Vérification rapide
```bash
# Voir l'espace gaspillé
docker system df

# Voir les dangling uniquement
docker images -f "dangling=true"
```

**En résumé :** Elles sont **fonctionnellement inutiles** (ne servent plus) mais **physiquement utiles à supprimer** pour libérer de l'espace ! C'est du **ramasse-miettes Docker**. 🧹
