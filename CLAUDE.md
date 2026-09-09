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

- **Un seul fichier PDF par document et par semaine.** Pas de copie en double.
- Noms de fichiers :
  - `Planning WILBOW - S<sem> - <jours> <mois> <année>.pdf`
  - `Check in at Work - S<sem> - <jours> <mois> <année>.pdf`
- Emplacements : planning chantier dans `Grille Planning/`,
  Check-in @ Work dans `Check-in @ Work/`.
- **Vérification visuelle obligatoire avant livraison** : convertir le PDF en
  image (`pdftoppm`) et le regarder, pour repérer tout débordement sur une 2e
  page ou problème de mise en page. Si le cas se présente, ajuster (par ex.
  réduire légèrement les marges de page) **sans jamais couper de contenu**.

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
