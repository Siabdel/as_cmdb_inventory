# Diagramme d'Architecture Système - CMDB

## Architecture Globale

```mermaid
graph TB
    subgraph "Frontend Vue.js"
        A[Vue.js SPA] --> B[Vue Router]
        A --> C[Pinia Store]
        A --> D[Bootstrap UI]
        A --> E[html5-qrcode]
    end
    
    subgraph "Backend Django"
        F[Django REST API] --> G[PostgreSQL]
        F --> H[Celery Tasks]
        F --> I[QR Code Generator]
        F --> J[Token Auth]
    end
    
    subgraph "Infrastructure"
        K[Docker Containers]
        L[NGINX Proxy]
        M[Redis Cache]
    end
    
    A -->|HTTP/HTTPS| F
    H --> M
    K --> A
    K --> F
    K --> G
    L --> K
```

## Modèle de Données

```mermaid
erDiagram
    Location {
        id int PK
        name varchar
        type varchar
        parent_id int FK
        description text
    }
    
    Category {
        id int PK
        name varchar
        slug varchar
        parent_id int FK
    }
    
    Brand {
        id int PK
        name varchar
    }
    
    Tag {
        id int PK
        name varchar
    }
    
    Asset {
        id uuid PK
        internal_code varchar UK
        name varchar
        category_id int FK
        brand_id int FK
        model varchar
        serial_number varchar
        description text
        purchase_date date
        status varchar
        current_location_id int FK
        qr_code_image varchar
        created_at datetime
        updated_at datetime
    }
    
    AssetMovement {
        id int PK
        asset_id uuid FK
        from_location_id int FK
        to_location_id int FK
        moved_by_id int FK
        move_type varchar
        note text
        created_at datetime
    }
    
    User {
        id int PK
        username varchar
        email varchar
    }
    
    Location ||--o{ Location : "parent"
    Category ||--o{ Category : "parent"
    Location ||--o{ Asset : "current_location"
    Category ||--o{ Asset : "category"
    Brand ||--o{ Asset : "brand"
    Asset ||--o{ AssetMovement : "asset"
    Location ||--o{ AssetMovement : "from_location"
    Location ||--o{ AssetMovement : "to_location"
    User ||--o{ AssetMovement : "moved_by"
    Asset }|--|| Tag : "tags"
```

## Flux de Données - Scan QR

```mermaid
sequenceDiagram
    participant M as Mobile/Camera
    participant F as Frontend Vue
    participant A as Django API
    participant D as Database
    
    M->>F: Scan QR Code
    F->>F: Extract UUID from QR
    F->>A: GET /api/assets/{uuid}/
    A->>D: Query Asset
    D-->>A: Asset Data
    A-->>F: Asset JSON
    F->>F: Display Asset Info
    
    alt User chooses to move
        F->>A: POST /api/assets/move-from-scan/
        A->>D: Create AssetMovement
        A->>D: Update Asset Location
        D-->>A: Success
        A-->>F: Movement Confirmed
        F->>F: Show Success Message
    end
```

## Architecture API REST

```mermaid
graph LR
    subgraph "API Endpoints"
        A[/api/assets/] --> B[AssetViewSet]
        C[/api/locations/] --> D[LocationViewSet]
        E[/api/categories/] --> F[CategoryViewSet]
        G[/api/brands/] --> H[BrandViewSet]
        I[/api/tags/] --> J[TagViewSet]
        
        K[/api/assets/{id}/qr_image/] --> L[QR Generator]
        M[/api/assets/move-from-scan/] --> N[Move Handler]
        O[/api/dashboard/summary/] --> P[Dashboard Stats]
        Q[/api/assets/{id}/movements/] --> R[Movement History]
    end
    
    subgraph "Services"
        B --> S[Asset Service]
        L --> T[QR Service]
        N --> U[Movement Service]
        P --> V[Analytics Service]
    end
    
    subgraph "Models"
        S --> W[Asset Model]
        U --> X[AssetMovement Model]
        V --> Y[All Models]
    end
```

## Composants Frontend Vue.js

```mermaid
graph TB
    subgraph "App.vue"
        A[Main Layout]
        A --> B[Navbar]
        A --> C[Sidebar]
        A --> D[Router View]
    end
    
    subgraph "Views"
        E[Dashboard.vue]
        F[AssetList.vue]
        G[AssetDetail.vue]
        H[ScanQR.vue]
        I[AssetForm.vue]
    end
    
    subgraph "Components"
        J[Scan.vue]
        K[AssetCard.vue]
        L[DataTable.vue]
        M[QRDisplay.vue]
        N[StatsWidget.vue]
    end
    
    subgraph "Services"
        O[API Service]
        P[QR Scanner Service]
        Q[Utils Service]
    end
    
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
    
    E --> N
    F --> L
    G --> M
    H --> J
    I --> K
    
    J --> P
    L --> O
    M --> O
    N --> O
```

## Workflow Principal - Gestion d'Asset

```mermaid
flowchart TD
    A[Créer Asset] --> B[Générer QR Code]
    B --> C[Imprimer QR]
    C --> D[Coller sur Équipement]
    D --> E[Asset en Stock]
    
    E --> F[Scan QR]
    F --> G{Action?}
    
    G -->|Déplacer| H[Sélectionner Destination]
    G -->|Voir Détails| I[Afficher Fiche]
    G -->|Marquer Panne| J[Changer Statut]
    
    H --> K[Créer Mouvement]
    K --> L[Mettre à jour Location]
    L --> M[Historique Mis à Jour]
    
    I --> N[Voir Historique]
    I --> O[Modifier Asset]
    
    J --> P[Asset en Panne]
    P --> Q[Notification Maintenance]
```

## Sécurité et Authentification

```mermaid
graph LR
    A[User Login] --> B[Django Auth]
    B --> C[Generate Token]
    C --> D[Store in Frontend]
    
    D --> E[API Requests]
    E --> F[Token Validation]
    F --> G{Valid?}
    
    G -->|Yes| H[Process Request]
    G -->|No| I[401 Unauthorized]
    
    H --> J[Check Permissions]
    J --> K{Authorized?}
    
    K -->|Yes| L[Execute Action]
    K -->|No| M[403 Forbidden]
```

Cette architecture garantit une séparation claire des responsabilités, une scalabilité future et une maintenance facilitée du code.