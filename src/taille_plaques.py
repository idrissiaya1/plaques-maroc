# src/taille_plaques.py
# Taille de la vraie plaque (en fraction de l'image) et lien avec les filtres d'aire.
import glob
import os

import cv2

import localisation as L
from evaluer_localisation import lire_verite, iou

SPLIT = "valid"


def trier(aire):
    if aire < L.AIRE_MIN:
        return "plus petite que AIRE_MIN"
    if aire > L.AIRE_MAX:
        return "plus grande que AIRE_MAX"
    return "entre les bornes"


resultats = []      # (nom, fraction d'aire, correct ?, aucun candidat ?)
for chemin in sorted(glob.glob(f"data/images/{SPLIT}/images/*")):
    img = cv2.imread(chemin)
    h, w = img.shape[:2]
    x1, y1, x2, y2 = lire_verite(chemin)
    aire = (x2 - x1) * (y2 - y1) / (w * h)
    candidats = L.lister_candidats(img)
    correct = False
    if candidats:
        x, y, bw, bh = candidats[0][1]
        correct = iou((x, y, x + bw, y + bh), (x1, y1, x2, y2)) >= 0.5
    resultats.append((os.path.basename(chemin), aire, correct, not candidats))

print(f"Images de {SPLIT} : {len(resultats)}")
print(f"Bornes actuelles : AIRE_MIN = {L.AIRE_MIN}, AIRE_MAX = {L.AIRE_MAX}\n")
print("Taille de la vraie plaque (aire de la plaque / aire de l'image) :")
for groupe in ["plus petite que AIRE_MIN", "entre les bornes", "plus grande que AIRE_MAX"]:
    dedans = [r for r in resultats if trier(r[1]) == groupe]
    bons = sum(1 for r in dedans if r[2])
    taux = 100 * bons / len(dedans) if dedans else 0
    print(f"  {groupe:26s}: {len(dedans):3d} images, localisées correctement : {bons:3d} ({taux:.0f} %)")

print("\nImages sans aucun candidat (aucun_candidat) :")
for nom, aire, correct, vide in resultats:
    if vide:
        print(f"  {nom[:45]:45s} aire = {aire:.4f}  -> {trier(aire)}")