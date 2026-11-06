# src/explorer_dataset.py
# Compte les images et affiche 6 plaques avec leur cadre vert.
import glob
import os
import cv2
import matplotlib.pyplot as plt

RACINE = "data/images"

# 1) Nombre d'images par sous-ensemble
for split in ["train", "valid", "test"]:
    n = len(glob.glob(f"{RACINE}/{split}/images/*"))
    print(f"{split} : {n} images")


def lire_boite(chemin_image):
    """Lit l'annotation YOLO et renvoie l'image et les cadres en pixels."""
    split_dir = os.path.dirname(os.path.dirname(chemin_image))
    nom = os.path.splitext(os.path.basename(chemin_image))[0]
    chemin_label = os.path.join(split_dir, "labels", nom + ".txt")

    img = cv2.imread(chemin_image)
    h, w = img.shape[:2]
    boites = []
    with open(chemin_label) as f:
        for ligne in f:
            # format YOLO : classe x_centre y_centre largeur hauteur (entre 0 et 1)
            _, xc, yc, bw, bh = map(float, ligne.split()[:5])
            x1 = int((xc - bw / 2) * w)
            y1 = int((yc - bh / 2) * h)
            x2 = int((xc + bw / 2) * w)
            y2 = int((yc + bh / 2) * h)
            boites.append((x1, y1, x2, y2))
    return img, boites


# 2) Affiche 6 images avec leur cadre vert
images = sorted(glob.glob(f"{RACINE}/train/images/*"))[:6]
plt.figure(figsize=(12, 6))
for i, chemin in enumerate(images):
    img, boites = lire_boite(chemin)
    for (x1, y1, x2, y2) in boites:
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
    plt.subplot(2, 3, i + 1)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(os.path.basename(chemin)[:25], fontsize=8)
    plt.axis("off")
plt.tight_layout()
plt.show()