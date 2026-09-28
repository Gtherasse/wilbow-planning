# CLAUDE.md — Planning WILBOW

Règles permanentes de génération du planning hebdomadaire de Wilbow SA
(fibre optique / télécom). Interlocuteur : **Geoffrey Therasse**, manager.

## À lire avant toute action

1. `_notes_planning.md` — **en entier**. C'est le mémo qui trace toutes les
   décisions, absences, échanges de chantiers et règles prises au fil des
   semaines. Il fait autorité sur l'historique.
2. Le script `gen_planning_s<sem>.py` du numéro de semaine le plus élevé
   présent, pour la structure exacte du dict `PLANNING`.

## Objectif

Produire chaque semaine **deux PDF A4 paysage, 1 page**, à partir d'une
**seule source de données** (le dict `PLANNING`) :

1. **Planning chantier** — qui fait quoi, où, quel JMS — pour l'équipe terrain.
2. **Check in @ Work** — pour le secrétariat, avec **uniquement** les codes
   C@W (aucun détail chantier), généré par le même script en mode `caw`, afin
   que les deux documents ne puissent jamais diverger.

## Règles strictes de contenu

- **Seuls les dossiers confirmés apparaissent.** Rien de « à planifier » n'est
  affiché — case grisée à la place.
- 1 colonne = 1 jour. Les noms d'équipe / de jointeur sont rappelés dans
  **chaque** colonne, au-dessus de leur JMS.
- **Absences** affichées avec leur motif exact — `CONGÉ`, `MALADIE`,
  `FORMATION`, `RÉCUP`, `ABSENT`, `EN ATTENTE` — via les pastilles de couleur
  déjà définies dans `ABS_STYLE`.
- **Notes** :
  - `commun` (pastille bleue) — plusieurs personnes ou équipes partagent un
    même chantier **confirmé** (ex. « + P. Mattiuz », « + Équipe 2 ») ;
  - `alt` (grise, pointillés) — tags informationnels (ex. « PW ») ;
  - `prov` (orange, pointillés) — associations **non confirmées**.
- Numéros JMS **cliquables** vers Monday.com. Chercher le numéro à la fois
  dans le **nom** de l'item et dans sa colonne **Référence**
  (`text_mkyv4qd0`).
- **Horodatage automatique** (date + heure, Europe/Brussels) régénéré à chaque
  génération de PDF.

## Ne jamais deviner — demander

- **Chaque fois qu'un JMS ou un chantier est attribué sans code Check-in @ Work
  (C@W) précisé : demander le code avant de générer les PDF.** Ne jamais
  deviner, ne jamais laisser une case C@W vide silencieusement.
- Plus généralement : **toute instruction ambiguë** (quelle semaine ? quel jour
  exact ? qui remplace qui ?) fait l'objet d'une question **avant** d'agir,
  jamais d'une supposition.

## Monday.com

Board « Chantiers » : **`5089236279`**.

Toute modification de planning se répercute **en parallèle** sur Monday.com —
date prévue et personnes assignées :

| Travail | Colonne date | Colonne personnes |
| --- | --- | --- |
| Soufflage | `date_mkyvzxy9` | `multiple_person_mkyvbk74` |
| Jointage | `date_mkyvm1ch` | `multiple_person_mkyvz89e` |

> **Exception absolue : les chantiers BTO ne sont JAMAIS modifiés sur
> Monday.com.**

Lors d'un ajout de personnes, **relire la valeur brute** de la colonne et
reconstruire la liste complète : une écriture partielle écrase les personnes
déjà assignées. Vérifier ensuite l'état réel sur le board, pas seulement le
retour de la mutation.

## Livrables

**Un seul fichier PDF par semaine, deux pages** (règle du 13/09/2026) :

| Page | Contenu | Destinataire |
| --- | --- | --- |
| 1 | Planning chantier — qui fait quoi, où, quel JMS | Équipe terrain |
| 2 | Check in @ Work — uniquement les codes C@W | Secrétariat |

Les deux pages sont générées à partir du **même** dict `PLANNING`, elles ne peuvent donc
pas diverger. Chaque page conserve sa propre hauteur de ligne optimale.

- Nom du fichier : `Planning WILBOW - S<sem> - <jours> <mois> <année>.pdf`
- Emplacement : **`Grille Planning/`** — tout y va, le dossier `Check-in @ Work/` n'est plus
  alimenté.
- **Un seul fichier par semaine.** Pas de copie en double, pas de PDF C@W séparé.
- Le script prend le chemin de sortie en unique argument :
  `python3 _modele_planning_s<sem>.py "Grille Planning/Planning WILBOW - S<sem> - ....pdf"`
- **Vérification visuelle obligatoire avant livraison** : convertir **les deux pages** en
  image et les regarder. Le script refuse déjà de produire autre chose que 2 pages, mais il
  ne juge pas la mise en page. Si une page déborde, ajuster (marges, taille de police)
  **sans jamais couper de contenu**.

## Livraison des documents — récupération automatique

Les PDF sont générés et commités dans ce dépôt, mais **Claude Code n'a aucun accès au
disque de Geoffrey** (session distante) : il ne peut donc pas déposer lui-même les fichiers.

**Depuis le 28/09/2026, la récupération est automatique.** Une tâche planifiée Windows
(« Planning WILBOW - maj ») exécute `maj.bat auto` **toutes les 10 minutes** sur le poste de
Geoffrey, qui fait le `git pull`. Les PDF arrivent seuls dans `Grille Planning\`, avec le
script de la semaine et le mémo. Les fichiers de même nom sont écrasés : c'est voulu — un
seul fichier par document et par semaine.

**Conséquence sur les réponses : ne plus terminer chaque livraison par la commande
`git pull`.** Se contenter d'indiquer **quels fichiers** ont été mis à jour, et de préciser
que les documents arrivent **dans les 10 minutes**.

Ne redonner la commande manuelle que dans deux cas :

- Geoffrey signale que la tâche est désactivée, supprimée ou en échec ;
- un document est attendu **immédiatement**, sans attendre le prochain déclenchement.

```powershell
cd "C:\Users\123\Desktop\WILBOW\Claude\Planning"
git pull
```

Le double-clic sur `maj.bat` fait la même chose, sans terminal.

### Trois façons de récupérer les documents

Claude Code tourne dans un conteneur distant : **il n'a aucun accès au disque de Geoffrey**
et ne peut donc pas exécuter lui-même la mise à jour. Trois solutions, de la plus manuelle
à la plus automatique :

1. **La commande à la main** (ci-dessus) — c'est le mode de secours, toujours valable.
2. **`maj.bat`**, à la racine du dossier : un double-clic fait le `git pull` et affiche une
   erreur lisible s'il échoue. Rien à retenir, rien à taper.
3. **Tâche planifiée Windows** : `maj.bat auto` exécuté automatiquement toutes les
   10 minutes. Les PDF se mettent à jour seuls, plus aucune action. À installer une fois,
   dans un PowerShell **ordinaire** (pas besoin d'administrateur — la tâche est enregistrée
   pour l'utilisateur courant) :

   ```powershell
   $dossier = "C:\Users\123\Desktop\WILBOW\Claude\Planning"
   $action  = New-ScheduledTaskAction -Execute "$dossier\maj.bat" -Argument "auto" -WorkingDirectory $dossier
   $decl    = New-ScheduledTaskTrigger -Once -At (Get-Date) `
                -RepetitionInterval (New-TimeSpan -Minutes 10)
   Register-ScheduledTask -TaskName "Planning WILBOW - maj" -Action $action `
                -Trigger $decl -Description "git pull des plannings WILBOW" -Force
   ```

   Pour la retirer : `Unregister-ScheduledTask -TaskName "Planning WILBOW - maj" -Confirm:$false`.

   ⚠️ `schtasks /create /tr "\"...\""` **ne fonctionne pas en PowerShell** : `\"` n'y est
   pas un échappement valide et la commande est rejetée (« Argument ou option non valide »).
   Les applets `New-ScheduledTaskAction` / `Register-ScheduledTask` ci-dessus évitent ce
   piège de guillemets.

   Le paramètre `auto` supprime les `pause` et les temporisations du script : sans lui, une
   tâche planifiée qui échoue resterait bloquée indéfiniment sur une fenêtre invisible.
   Une brève fenêtre de console apparaît à chaque exécution ; c'est le comportement normal
   d'un `.bat` planifié.

**Solution 3 recommandée** : c'est la seule qui supprime complètement l'étape manuelle.
Tant qu'elle n'est pas installée, continuer à donner la commande à chaque livraison.

## Après chaque modification

- Mettre à jour le gabarit `_modele_planning_s<sem>.py` (copie du script de la
  semaine).
- Ajouter au mémo `_notes_planning.md` une entrée décrivant le changement.
- Committer : le dépôt doit refléter l'état réel, sans rattrapage a posteriori.

## Rythme de travail

On ne maintient activement **qu'une semaine à la fois** en général. Préparer
les semaines suivantes à l'avance quand des instructions datées dans le futur
sont données est un **pattern accepté et courant** : plusieurs semaines peuvent
être « actives » en parallèle.
