# src/evaluer_localisation.py
# Taux de localisation correcte sur un sous-ensemble (IoU >= 0.5).
import glob
import os
import cv2
from localisation import localiser_plaque

SPLIT = "valid"      # règle tes paramètres sur valid, mesure sur test à la fin
SEUIL_IOU = 0.5


def lire_verite(chemin_image):
    """Première boîte annotée (x1, y1, x2, y2) en pixels."""
    split_dir = os.path.dirname(os.path.dirname(chemin_image))
    nom = os.path.splitext(os.path.basename(chemin_image))[0]
    chemin_label = os.path.join(split_dir, "labels", nom + ".txt")
    img = cv2.imread(chemin_image)
    h, w = img.shape[:2]
    with open(chemin_label) as f:
        ligne = f.readline().split()
    _, xc, yc, bw, bh = map(float, ligne[:5])
    return (int((xc - bw / 2) * w), int((yc - bh / 2) * h),
            int((xc + bw / 2) * w), int((yc + bh / 2) * h))


def iou(a, b):
    """a et b : (x1, y1, x2, y2). Recouvrement entre deux rectangles."""
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    aire_a = (a[2] - a[0]) * (a[3] - a[1])
    aire_b = (b[2] - b[0]) * (b[3] - b[1])
    union = aire_a + aire_b - inter
    return inter / union if union > 0 else 0


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

print(f"{SPLIT} : {len(chemins)} images")
print(f"Localisations correctes : {corrects} ({100 * corrects / len(chemins):.1f} %)")
print(f"Aucune plaque trouvée  : {non_trouvees}")