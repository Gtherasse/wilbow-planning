# Plannings WILBOW

Arborescence du depot, identique sur Mac et sur PC une fois clone :

```
Wilbow/
└── Planning/              <- les grilles de planning en PDF, une par semaine
    └── Config/            <- tout ce qui sert a les fabriquer
        ├── _modele_planning_s<NN>.py   un script autonome par semaine
        ├── _notes_planning.md          le memo de suivi, tenu a jour en continu
        ├── CLAUDE.md                   les regles permanentes
        ├── logo_wilbow.png / .jpg      le logo repris en tete de grille
        ├── Check-in @ Work/            les codes C@W de reference
        ├── maj.command                 mise a jour sur Mac (double-clic)
        └── maj.bat                     mise a jour sur PC (double-clic)
```

## Recuperer la derniere version

**Mac** : double-cliquer `Planning/Config/maj.command`, ou en Terminal

```bash
cd ~/Desktop/Wilbow && git pull
```

**PC** : double-cliquer `Planning\Config\maj.bat`, ou en PowerShell

```powershell
cd "C:\Users\123\Desktop\WILBOW\Claude\Planning"
git pull
```

## Premiere installation sur un Mac

```bash
cd ~/Desktop && git clone https://github.com/Gtherasse/wilbow-planning.git Wilbow
```

## Regenerer une grille

Les scripts tournent avec Python 3 et WeasyPrint. Depuis la racine du depot :

```bash
python3 "Planning/Config/_modele_planning_s43.py" "Planning/Planning WILBOW - S43 - 19-23 oct 2026.pdf"
```

Le chemin de sortie est le premier argument. Sans argument, le PDF est ecrit dans le
dossier courant.
