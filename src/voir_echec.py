# src/voir_echec.py
# Usage : python src/voir_echec.py 20200725-WA0069            (cherche dans valid)
#         python src/voir_echec.py 20200725-WA0069 tous       (cherche dans train, valid et test)
# Affiche les images dont le nom contient le code :
#   vert = vraie plaque, rouge = choix du programme, orange = 2e candidat.
import glob
import os
import sys

import cv2
import matplotlib.pyplot as plt

from localisation import lister_candidats
from evaluer_localisation import lire_verite

if len(sys.argv) < 2:
    print("Usage : python src/voir_echec.py 20200725-WA0069 [valid|train|test|tous]")
    raise SystemExit

code = sys.argv[1]
split = sys.argv[2] if len(sys.argv) > 2 else "valid"
dossier = "*" if split == "tous" else split
chemins = sorted(c for c in glob.glob(f"data/images/{dossier}/images/*")
                 if code in os.path.basename(c))
if not chemins:
    print(f"Aucune image de '{split}' ne contient : {code}")
    raise SystemExit
chemins = chemins[:4]                     # au plus 4 images (copies d'une même photo)

print("Images affichées (de gauche à droite) :")
for chemin in chemins:
    print("  ", chemin.replace("\\", "/"))


def en_xyxy(boite):
    x, y, w, h = boite
    return (x, y, x + w, y + h)


plt.figure(figsize=(6 * len(chemins), 6))
for k, chemin in enumerate(chemins):
    img = cv2.imread(chemin)
    candidats = lister_candidats(img)      # calculé AVANT de dessiner sur l'image
    dessin = img.copy()
    x1, y1, x2, y2 = lire_verite(chemin)
    cv2.rectangle(dessin, (x1, y1), (x2, y2), (0, 255, 0), 3)               # vérité : vert
    for rang, (score, boite) in enumerate(candidats[:2], start=1):
        a, b, c, d = en_xyxy(boite)
        couleur = (0, 0, 255) if rang == 1 else (0, 165, 255)               # rouge puis orange
        cv2.rectangle(dessin, (a, b), (c, d), couleur, 3)
    plt.subplot(1, len(chemins), k + 1)
    plt.imshow(cv2.cvtColor(dessin, cv2.COLOR_BGR2RGB))
    plt.title(f"{os.path.basename(chemin)[:28]} | {len(candidats)} candidats", fontsize=9)
    plt.axis("off")
plt.suptitle("Vert = vraie plaque | Rouge = choix | Orange = 2e candidat")
plt.tight_layout()
plt.show()