# 🗺️ Roadmap Builder

Application web interactive pour créer et personnaliser des roadmaps de projet par sprints.
Générée avec **Streamlit** + **Matplotlib**, avec persistance locale des données.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red?logo=streamlit)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8%2B-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Démarrage rapide

### 1️⃣ Prérequis

- Python **3.10+** installé sur votre machine
- `pip` (gestionnaire de paquets Python)

Vérifier votre version Python :
```bash
python --version
```

### 2️⃣ Cloner le dépôt

```bash
git clone https://github.com/votre-utilisateur/roadmap-builder.git
cd roadmap-builder
```

### 3️⃣ Créer un environnement virtuel (recommandé)

```bash
# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
# ➤ Sur Linux / macOS
source .venv/bin/activate

# ➤ Sur Windows
.venv\Scripts\activate
```

### 4️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5️⃣ Lancer l'application

```bash
streamlit run app.py
```

🎉 **L'application s'ouvre automatiquement dans votre navigateur** à l'adresse :
```
http://localhost:8501
```

Si ce n'est pas le cas, ouvrez manuellement cette URL dans votre navigateur.

---

## Arrêter l'application

Dans le terminal, appuyez sur :
```
Ctrl + C
```

---

## Aperçu

La roadmap générée présente :
- Les **chantiers** (lignes) et leur avancement sprint par sprint
- Les **phases** par cellule (Dev, Test, Infra, Conception, Doc, Analyse)
- Les **statuts** (Terminé, En cours, Récurrent, À venir, Inactif)
- Les **jalons** regroupés par sprint en bas de page
- Le **sprint courant** mis en évidence (encadré vert)
- La **barre de progression** du sprint en cours
- Les **livrables finaux** par chantier
- Les éventuelles **vacances** sur un sprint

---

## Fonctionnalités

| Section | Description |
|---|---|
| **Infos générales** | Titre, date de MAJ, capacité équipe, avancement sprint |
| **Sprints** | Ajouter / supprimer / renommer, choisir le sprint courant |
| **Vacances** | Affichage optionnel sur un sprint donné |
| **Chantiers** | Édition complète : nom, charge, livrable, jalon, statut et phase par sprint |
| **Inactif** | Un chantier peut ne pas être actif sur certains sprints (cellule vide) |
| **Import / Export** | Sauvegarde et chargement de toute la config en JSON |
| **Persistance locale** | Les données sont sauvegardées automatiquement entre les sessions (`shelve`) |
| **Téléchargement** | Export PNG haute résolution (180 dpi) |

---

## Structure du projet

```
roadmap-builder/
│
├── app.py                  # Application principale
├── requirements.txt        # Dépendances Python
├── README.md               # Ce fichier
│
├── roadmap_data.db         # Base de données locale (créée automatiquement)
│                           # ⚠️ Ne pas commiter ce fichier
└── .gitignore
```

---

## Persistance des données

Les données sont sauvegardées automatiquement dans un fichier local (`roadmap_data.db`)
via le module Python standard `shelve`. Aucune base de données externe n'est requise.

- **Sauvegarde** : automatique à chaque modification
- **Chargement** : automatique au démarrage de l'application
- **Reset** : bouton "🔄 Reset défauts" dans l'interface
- **Backup manuel** : bouton "📥 Exporter JSON" pour sauvegarder la config en fichier

> Le fichier `roadmap_data.db` est propre à votre machine.
> Il ne doit pas être commité sur GitHub (voir `.gitignore`).

---

## Import / Export JSON

Vous pouvez exporter toute votre configuration en JSON pour :
- La partager avec un collègue
- La sauvegarder sur un cloud
- La versionner manuellement

Format du fichier exporté :

```json
{
  "titre": "ROADMAP - Vue d'ensemble projet",
  "maj_date": "30/04/2026",
  "capacite": "Max : 4 Dev / 2 Ops / semaine",
  "sprint_progress": 78,
  "sprint_progress_label": "SPRINT 2",
  "current_sprint": 1,
  "sprints": [
    {"label": "S1", "dates": "S11-S14"},
    ...
  ],
  "chantiers": [
    {
      "name": "Refonte UX/UI",
      "charge": "3 Dev",
      "livrable": "Page home\n+ header",
      "jalon_label": "UI valide client",
      "jalon_sprint": 2,
      "progress": [[1, "dev"], [0.3, "test"], [null, "dev"], ...]
    },
    ...
  ]
}
```

---

## Dépendances

| Package | Version minimale | Usage |
|---|---|---|
| `streamlit` | 1.35.0 | Interface web |
| `matplotlib` | 3.8.0 | Génération de la roadmap (PNG) |

> `shelve`, `io`, `json`, `os` sont des modules de la bibliothèque standard Python — aucune installation requise.

---

## Troubleshooting

### ❌ `Command not found: streamlit`

Vous n'avez pas activé l'environnement virtuel.

**Solution** :
```bash
# Activez-le d'abord
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows

# Puis relancez
streamlit run app.py
```

### ❌ `ModuleNotFoundError: No module named 'streamlit'`

Les dépendances ne sont pas installées.

**Solution** :
```bash
pip install -r requirements.txt
```

### ❌ Le port 8501 est déjà utilisé

Une autre application utilise le port 8501.

**Solution** :
```bash
# Lancer sur un port différent
streamlit run app.py --server.port 8502
```

---

## Licence

MIT — libre d'utilisation, de modification et de distribution.
