#!/usr/bin/env python
"""
migrate_all.py
Script de migration séquentiel — CMDB Inventory
Gère toutes les dépendances dans le bon ordre.

Usage :
    python migrate_all.py [--reset] [--fake] [--assets N] [--movements N]

Options :
    --reset      Remet à zéro toutes les tables (TRUNCATE CASCADE)
    --fake       Génère des données fake après migration
    --assets N   Nombre d'assets fake (défaut: 100)
    --movements N Nombre de mouvements fake (défaut: 200)
"""

import os
import sys
import argparse
import subprocess

# ── Couleurs terminal ──────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):    print(f"{GREEN}  ✅ {msg}{RESET}")
def warn(msg):  print(f"{YELLOW}  ⚠️  {msg}{RESET}")
def err(msg):   print(f"{RED}  ❌ {msg}{RESET}")
def info(msg):  print(f"{BLUE}  ➤  {msg}{RESET}")
def title(msg): print(f"\n{BOLD}{BLUE}{'─'*50}\n  {msg}\n{'─'*50}{RESET}")


def run(cmd, check=True, capture=False):
    """Exécute une commande shell."""
    result = subprocess.run(
        cmd, shell=True,
        capture_output=capture,
        text=True
    )
    if check and result.returncode != 0:
        err(f"Commande échouée : {cmd}")
        if capture:
            print(result.stderr)
        sys.exit(1)
    return result


def manage(cmd, capture=False):
    """Raccourci pour python manage.py."""
    return run(f"python manage.py {cmd}", capture=capture)


# ══════════════════════════════════════════════════════════
# ÉTAPE 1 — Vérifications préliminaires
# ══════════════════════════════════════════════════════════
def check_environment():
    title("ÉTAPE 1 — Vérification environnement")

    # manage.py présent ?
    if not os.path.exists("manage.py"):
        err("manage.py introuvable — lance ce script depuis le dossier backend/")
        sys.exit(1)
    ok("manage.py trouvé")

    # Django importable ?
    result = run("python -c \"import django; print(django.__version__)\"",
                 capture=True)
    ok(f"Django {result.stdout.strip()} disponible")

    # Connexion DB ?
    result = manage("dbshell --command=\"SELECT 1;\"", capture=True)
    if result.returncode != 0:
        err("Connexion base de données impossible — vérifier settings.py / .env")
        sys.exit(1)
    ok("Connexion PostgreSQL OK")


# ══════════════════════════════════════════════════════════
# ÉTAPE 2 — Reset optionnel (TRUNCATE dans le bon ordre)
# ══════════════════════════════════════════════════════════
def reset_database():
    title("ÉTAPE 2 — Reset base de données")

    warn("Suppression des données dans l'ordre des dépendances FK...")

    # Ordre strict : dépendants → parents
    TRUNCATE_ORDER = [
        # ── Apps dépendantes de inventory ─────────────────
        "maintenance_ticketcomment",
        "maintenance_ticketpart",
        "maintenance_statushistory",
        "maintenance_maintenanceticket",
        "scanner_scanlog",
        "scanner_qrcode",
        # ── Inventory ─────────────────────────────────────
        "inventory_assetmovement",
        "inventory_asset_tags",       # table M2M
        "inventory_asset",
        "inventory_tag",
        "inventory_location",
        "inventory_brand",
        "inventory_category",
        # ── Auth Django (optionnel) ────────────────────────
        # "auth_user",  # décommente si tu veux reset les users aussi
    ]

    tables_sql = ", ".join(f'\"{t}\"' for t in TRUNCATE_ORDER)

    # On ignore les tables inexistantes (app pas encore migrée)
    sql = f"""
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[{", ".join(f"\'{x}\'" for x in TRUNCATE_ORDER)}]
    LOOP
        IF EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = t
        ) THEN
            EXECUTE 'TRUNCATE TABLE \"' || t || '\" RESTART IDENTITY CASCADE';
            RAISE NOTICE 'Vidée : %', t;
        ELSE
            RAISE NOTICE 'Ignorée (inexistante) : %', t;
        END IF;
    END LOOP;
END $$;
"""
    # Écrire le SQL dans un fichier temporaire
    with open("/tmp/cmdb_reset.sql", "w") as f:
        f.write(sql)

    result = manage('dbshell < /tmp/cmdb_reset.sql', capture=True)
    ok("Tables vidées avec RESTART IDENTITY CASCADE")


# ══════════════════════════════════════════════════════════
# ÉTAPE 3 — Migrations séquentielles par app
# ══════════════════════════════════════════════════════════

# Ordre strict : parents avant dépendants
APPS_ORDER = [
    # ── Django core ────────────────────────────────────────
    ("contenttypes",  "django.contrib.contenttypes"),
    ("auth",          "django.contrib.auth"),
    ("admin",         "django.contrib.admin"),
    ("sessions",      "django.contrib.sessions"),
    # ── Apps projet ────────────────────────────────────────
    ("inventory",     "inventory"),     # base — pas de dépendances
    ("maintenance",   "maintenance"),   # dépend de inventory.Asset
    ("scanner",       "scanner"),       # dépend de inventory.Asset
]

def migrate_apps():
    title("ÉTAPE 3 — Migrations séquentielles")

    for app_label, app_module in APPS_ORDER:
        info(f"App : {app_label}")

        # makemigrations (si fichiers manquants)
        result = run(
            f"python manage.py makemigrations {app_label} --check",
            check=False, capture=True
        )
        if result.returncode != 0:
            info(f"  Création migrations manquantes pour {app_label}...")
            manage(f"makemigrations {app_label}")
            ok(f"  Migrations créées pour {app_label}")
        else:
            info(f"  Migrations à jour pour {app_label}")

        # migrate
        result = manage(f"migrate {app_label}", capture=True)
        if result.returncode == 0:
            ok(f"  migrate {app_label} — OK")
        else:
            err(f"  migrate {app_label} — ÉCHEC")
            print(result.stderr)
            sys.exit(1)

    # migrate global final (capte tout ce qui reste)
    info("Migration finale globale...")
    manage("migrate")
    ok("Toutes les migrations appliquées")


# ══════════════════════════════════════════════════════════
# ÉTAPE 4 — Superuser auto
# ══════════════════════════════════════════════════════════
def ensure_superuser():
    title("ÉTAPE 4 — Superuser")

    script_py = """
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@cmdb.local', 'admin123')
    print('CREATE')
else:
    print('EXISTS')
"""
    with open("/tmp/ensure_su.py", "w") as f:
        f.write(script_py)

    result = manage("shell < /tmp/ensure_su.py", capture=True)
    if "CREATE" in result.stdout:
        ok("Superuser créé : admin / admin123")
    else:
        ok("Superuser admin déjà existant")


# ══════════════════════════════════════════════════════════
# ÉTAPE 5 — Données fake (optionnel)
# ══════════════════════════════════════════════════════════
def generate_fake(assets=100, movements=200):
    title(f"ÉTAPE 5 — Données fake ({assets} assets, {movements} mouvements)")
    manage(f"generate_fake_data --assets {assets} --movements {movements}")
    ok("Données fake générées")


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="Migration séquentielle CMDB Inventory"
    )
    parser.add_argument("--reset",     action="store_true",
                        help="Vider toutes les tables avant migration")
    parser.add_argument("--fake",      action="store_true",
                        help="Générer des données fake après migration")
    parser.add_argument("--assets",    type=int, default=100)
    parser.add_argument("--movements", type=int, default=200)
    args = parser.parse_args()

    print(f"\n{BOLD}{'═'*50}")
    print("  CMDB Inventory — Migration séquentielle")
    print(f"{'═'*50}{RESET}")

    check_environment()

    if args.reset:
        reset_database()

    migrate_apps()
    ensure_superuser()

    if args.fake:
        generate_fake(args.assets, args.movements)

    print(f"\n{BOLD}{GREEN}{'═'*50}")
    print("  DONE — Système prêt !")
    print(f"{'═'*50}{RESET}\n")


if __name__ == "__main__":
    main()
