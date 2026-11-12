# src/analyse_echecs.py
# Classe chaque image de SPLIT (correct / mal classé / absente / aucun candidat),
# calcule le "plafond" du score, sauvegarde un CSV et une galerie d'échecs.
import csv
import glob
import os

import cv2
import matplotlib.pyplot as plt

from localisation import lister_candidats
from evaluer_localisation import lire_verite, iou

SPLIT = "valid"          # on analyse sur valid ; test reste réservé à la mesure finale
SEUIL_IOU = 0.5
NB_PAR_CATEGORIE = 6     # nombre d'exemples par catégorie dans la galerie

os.makedirs("rapport/figures", exist_ok=True)


def en_xyxy(boite):
    x, y, w, h = boite
    return (x, y, x + w, y + h)


chemins = sorted(glob.glob(f"data/images/{SPLIT}/images/*"))
resultats = []   # un dictionnaire par image

for chemin in chemins:
    img = cv2.imread(chemin)
    verite = lire_verite(chemin)
    candidats = lister_candidats(img)
    ious = [iou(en_xyxy(boite), verite) for _, boite in candidats]

    # rang du premier candidat qui recouvre vraiment la plaque (None s'il n'y en a pas)
    rang = next((i + 1 for i, v in enumerate(ious) if v >= SEUIL_IOU), None)

    if not candidats:
        statut = "aucun_candidat"        # le filtre a tout éliminé
    elif rang == 1:
        statut = "correct"               # le bon candidat est le premier
    elif rang is not None:
        statut = "mal_classe"            # la plaque est candidate mais pas choisie
    else:
        statut = "absente"               # des candidats existent, mais aucun n'est la plaque

    resultats.append({
        "image": os.path.basename(chemin),
        "chemin": chemin,
        "statut": statut,
        "iou_choisi": round(ious[0], 3) if ious else 0.0,
        "rang_plaque": rang if rang is not None else "",
        "nb_candidats": len(candidats),
        "verite": verite,
        "choisi": en_xyxy(candidats[0][1]) if candidats else None,
    })

# ---------------------------------------------------------------- Statistiques
n = len(resultats)
compte = {s: sum(1 for r in resultats if r["statut"] == s)
          for s in ["correct", "mal_classe", "absente", "aucun_candidat"]}

print(f"\nAnalyse sur {SPLIT} : {n} images")
for statut, nb in compte.items():
    print(f"  {statut:15s}: {nb:4d}  ({100 * nb / n:.1f} %)")
plafond = compte["correct"] + compte["mal_classe"]
print(f"\nTaux actuel                               : {100 * compte['correct'] / n:.1f} %")
print(f"Plafond si le score choisissait toujours bien : {100 * plafond / n:.1f} %")
print("  (= images où la vraie plaque figure parmi les candidats)")

# ---------------------------------------------------------------- CSV
with open("rapport/echecs_" + SPLIT + ".csv", "w", newline="", encoding="utf-8-sig") as f:
    ecrivain = csv.writer(f, delimiter=";")
    ecrivain.writerow(["image", "statut", "iou_choisi", "rang_plaque",
                       "nb_candidats", "cause_manuelle"])
    for r in resultats:
        if r["statut"] != "correct":
            ecrivain.writerow([r["image"], r["statut"], r["iou_choisi"],
                               r["rang_plaque"], r["nb_candidats"], ""])
print(f"\nCSV écrit : rapport/echecs_{SPLIT}.csv (remplis la colonne cause_manuelle)")

# ---------------------------------------------------------------- Galerie
exemples = []
for statut in ["mal_classe", "absente", "aucun_candidat"]:
    exemples += [r for r in resultats if r["statut"] == statut][:NB_PAR_CATEGORIE]

if exemples:
    colonnes = 4
    lignes = (len(exemples) + colonnes - 1) // colonnes
    plt.figure(figsize=(4 * colonnes, 3.4 * lignes))
    for k, r in enumerate(exemples):
        img = cv2.imread(r["chemin"])
        x1, y1, x2, y2 = r["verite"]
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)          # vérité : vert
        if r["choisi"] is not None:
            a, b, c, d = r["choisi"]
            cv2.rectangle(img, (a, b), (c, d), (0, 0, 255), 3)          # choisi : rouge
        plt.subplot(lignes, colonnes, k + 1)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title(f"{r['statut']} | IoU {r['iou_choisi']}", fontsize=8)
        plt.axis("off")
    plt.suptitle("Vert = vraie plaque (annotation) ; rouge = choix du programme", fontsize=10)
    plt.tight_layout()
    plt.savefig(f"rapport/figures/galerie_echecs_{SPLIT}.png", dpi=130)
    print(f"Galerie écrite : rapport/figures/galerie_echecs_{SPLIT}.png")
    plt.show()