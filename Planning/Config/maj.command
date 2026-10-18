#!/bin/bash
# Mise a jour des plannings WILBOW sur Mac.
# Double-cliquer ce fichier : il descend la derniere version depuis GitHub.
cd "$(dirname "$0")/../.." || exit 1
echo "Mise a jour des plannings WILBOW..."
if git pull --ff-only; then
  echo
  echo "Plannings a jour."
  sleep 2
else
  echo
  echo "*** La mise a jour a echoue. Previens Claude avec le message ci-dessus. ***"
  read -r -p "Appuie sur Entree pour fermer."
  exit 1
fi
