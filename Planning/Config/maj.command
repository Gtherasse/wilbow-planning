#!/bin/bash
# ---------------------------------------------------------------------------
# Mise a jour des plannings WILBOW — Mac
# Double-cliquer ce fichier : il descend la derniere version depuis GitHub.
# Equivalent Mac de maj.bat, place dans le meme dossier.
# ---------------------------------------------------------------------------

# On se place a la racine du depot, deux niveaux au-dessus de Config/.
cd "$(dirname "$0")/../.." || { echo "Dossier introuvable."; read -r; exit 1; }

echo "Mise a jour des plannings WILBOW..."
echo

if [ ! -d .git ]; then
  echo "*** Ce dossier n est pas un depot git."
  echo "    Attendu : ~/Desktop/Wilbow/Planning/Config/maj.command"
  echo "    Previens Claude."
  read -r -p "Appuie sur Entree pour fermer."
  exit 1
fi

avant=$(git rev-parse HEAD)

if ! git pull --ff-only; then
  echo
  echo "*** La mise a jour a echoue. Previens Claude avec le message ci-dessus. ***"
  read -r -p "Appuie sur Entree pour fermer."
  exit 1
fi

apres=$(git rev-parse HEAD)
echo

if [ "$avant" = "$apres" ]; then
  echo "Rien de neuf : tu avais deja la derniere version."
else
  echo "Fichiers mis a jour :"
  git diff --name-only "$avant" "$apres" | sed 's/^/   /'
fi

echo
echo "Plannings a jour."
sleep 3
