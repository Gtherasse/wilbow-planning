# Planning WILBOW

Génération hebdomadaire des documents de planning de Wilbow SA à partir d'une
**source de données unique** (le dict `PLANNING` du script Python de la semaine).

Deux documents sont produits par le **même** script, afin qu'ils ne puissent
jamais diverger :

| Document | Destinataire | Contenu | Dossier |
| --- | --- | --- | --- |
| Planning chantier | Équipe terrain | Qui fait quoi, où, quel JMS | `Grille Planning/` |
| Check in @ Work | Secrétariat | Uniquement les codes C@W | `Check-in @ Work/` |

Les deux sont des PDF **A4 paysage, 1 page**.

## Structure du dépôt

| Chemin | Rôle |
| --- | --- |
| `gen_planning_s<sem>.py` | Script de génération de la semaine courante |
| `_modele_planning_s<sem>.py` | Gabarit — copie du script de la semaine |
| `_notes_planning.md` | Mémo : décisions, absences, échanges de chantiers, règles |
| `Grille Planning/` | PDF planning chantier livrés |
| `Check-in @ Work/` | PDF Check in @ Work livrés |
| `CLAUDE.md` | Règles permanentes, lues automatiquement par Claude Code |

## Utilisation

```bash
python3 gen_planning_s37.py          # planning chantier
python3 gen_planning_s37.py caw      # Check in @ Work
```

## Prérequis

- Python 3 et **WeasyPrint** — `pip install weasyprint`
  (nécessite Pango/Cairo installés sur le système ; vérifier avec
  `python3 -c "import weasyprint"`)
- **poppler-utils** (`pdftoppm`) pour la vérification visuelle des PDF

## Monday.com

Board « Chantiers » : `5089236279`. Chaque changement de planning se
répercute sur Monday.com — voir `CLAUDE.md` pour les colonnes et
l'exception BTO.
