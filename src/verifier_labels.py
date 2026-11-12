# src/verifier_labels.py
# Contrôle le format des fichiers d'annotation (labels) d'un sous-ensemble.
import collections
import glob
import os

SPLIT = "valid"

nb_lignes = collections.Counter()     # combien de lignes par fichier label
nb_valeurs = collections.Counter()    # combien de valeurs par ligne (5 = rectangle)
classes = collections.Counter()       # quelles classes apparaissent
anormaux = []                         # fichiers à regarder à la main

fichiers = sorted(glob.glob(f"data/images/{SPLIT}/labels/*.txt"))
for chemin in fichiers:
    with open(chemin) as f:
        lignes = [ligne.split() for ligne in f if ligne.strip()]
    nb_lignes[len(lignes)] += 1
    for ligne in lignes:
        nb_valeurs[len(ligne)] += 1
        classes[ligne[0]] += 1
    if len(lignes) != 1 or any(len(ligne) != 5 for ligne in lignes):
        anormaux.append(os.path.basename(chemin))

print(f"Fichiers labels dans {SPLIT} : {len(fichiers)}")
print("Lignes par fichier   :", dict(sorted(nb_lignes.items())))
print("Valeurs par ligne    :", dict(sorted(nb_valeurs.items())), "(5 = rectangle simple)")
print("Classes présentes    :", dict(sorted(classes.items())))
print(f"\nFichiers à regarder à la main : {len(anormaux)}")
for nom in anormaux[:10]:
    print("  ", nom)