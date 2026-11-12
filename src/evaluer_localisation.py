# src/evaluer_localisation.py
# Taux de localisation correcte sur un sous-ensemble (IoU >= 0.5).
import glob
import os
import cv2
from localisation import localiser_plaque

SPLIT = "valid"      # règle sur valid ; mesure sur test UNE SEULE fois, à la fin
SEUIL_IOU = 0.5


def lire_verite(chemin_image):
    """Rectangle de la plaque (x1, y1, x2, y2) en pixels, lu dans le fichier label.
    Gère deux formats : rectangle (classe xc yc largeur hauteur)
    et polygone (classe x1 y1 x2 y2 x3 y3 ...)."""
    split_dir = os.path.dirname(os.path.dirname(chemin_image))
    nom = os.path.splitext(os.path.basename(chemin_image))[0]
    chemin_label = os.path.join(split_dir, "labels", nom + ".txt")
    img = cv2.imread(chemin_image)
    h, w = img.shape[:2]
    with open(chemin_label) as f:
        ligne = f.readline().split()
    valeurs = [float(v) for v in ligne[1:]]      # on ignore le numéro de classe

    if len(valeurs) == 4:                        # rectangle : xc yc largeur hauteur
        xc, yc, bw, bh = valeurs
        x1, x2 = (xc - bw / 2) * w, (xc + bw / 2) * w
        y1, y2 = (yc - bh / 2) * h, (yc + bh / 2) * h
    else:                                        # polygone : x1 y1 x2 y2 ...
        xs, ys = valeurs[0::2], valeurs[1::2]
        x1, x2 = min(xs) * w, max(xs) * w
        y1, y2 = min(ys) * h, max(ys) * h
    return int(x1), int(y1), int(x2), int(y2)


def iou(a, b):
    """a et b : (x1, y1, x2, y2). Recouvrement entre deux rectangles."""
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    aire_a = (a[2] - a[0]) * (a[3] - a[1])
    aire_b = (b[2] - b[0]) * (b[3] - b[1])
    union = aire_a + aire_b - inter
    return inter / union if union > 0 else 0


if __name__ == "__main__":
    chemins = sorted(glob.glob(f"data/images/{SPLIT}/images/*"))
    corrects, non_trouvees = 0, 0
    for chemin in chemins:
        img = cv2.imread(chemin)
        boite = localiser_plaque(img)
        if boite is None:
            non_trouvees += 1
            continue
        x, y, w, h = boite
        if iou((x, y, x + w, y + h), lire_verite(chemin)) >= SEUIL_IOU:
            corrects += 1

    mauvais = len(chemins) - corrects - non_trouvees
    print(f"{SPLIT} : {len(chemins)} images")
    print(f"Localisations correctes : {corrects} ({100 * corrects / len(chemins):.1f} %)")
    print(f"Aucune plaque trouvée  : {non_trouvees}")
    print(f"Mauvais rectangle      : {mauvais}")