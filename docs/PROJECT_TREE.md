# Project tree

```text
parkgo/
├── .github/workflows/ci.yml
├── backend/
│   ├── alembic/
│   │   └── versions/20260830_0001_initial.py
│   ├── app/
│   │   ├── api/v1/               # auth, vehicles, parking, health routes
│   │   ├── core/                 # settings, bootstrap, JSON logging, middleware
│   │   ├── db/                   # async engine and declarative base
│   │   ├── exceptions/           # domain errors and safe HTTP envelopes
│   │   ├── models/               # user, vehicle, zones, sessions, payments, devices
│   │   ├── providers/parking/    # contract, DTOs, mock, Parkomatika placeholder
│   │   ├── repositories/         # persistence and PostGIS queries
│   │   ├── schemas/              # Pydantic request/response contracts
│   │   ├── security/             # Argon2, JWT rotation, rate limiting
│   │   ├── services/             # auth, vehicles and parking use cases
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DECISIONS.md
│   ├── DEPLOYMENT.md
│   ├── PARKING_PROVIDER.md
│   ├── PARKOMATIKA_INTEGRATION.md
│   ├── PRESENTATION.md
│   ├── PROJECT_TREE.md
│   └── SECURITY.md
├── infrastructure/nginx/nginx.conf
├── ios/
│   ├── ParkGo.xcodeproj
│   ├── ParkGo/
│   │   ├── App/                  # composition root and global session store
│   │   ├── Core/
│   │   ├── DesignSystem/
│   │   ├── Features/             # Auth, Home, Map, Cars, Parking, History, Profile
│   │   ├── Models/
│   │   ├── Networking/           # API client, Keychain and repositories
│   │   ├── Resources/
│   │   └── Services/             # location, geofence, notification, biometrics, activity
│   ├── ParkGoLiveActivity/
│   ├── Shared/
│   ├── ParkGoTests/
│   ├── ParkGoUITests/
│   └── Package.swift             # portable Swift checks
├── .env.example
├── docker-compose.yml
├── Makefile
└── README.md
```
