# src/etiqueter.py
# Aide à écrire data/verite_terrain.csv : affiche la plaque, tu tapes ce que tu lis.
import csv
import glob
import os

import cv2

from evaluer_localisation import lire_verite

SPLIT = "valid"
FICHIER = "data/verite_terrain.csv"
ENTETE = ["image", "numero", "lettre", "code", "commentaire"]


def preparer_fichier():
    """Crée le fichier avec son en-tête s'il n'existe pas ; sinon vérifie la fin de ligne."""
    if not os.path.exists(FICHIER) or os.path.getsize(FICHIER) == 0:
        with open(FICHIER, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(ENTETE)
        return
    with open(FICHIER, "rb") as f:
        f.seek(-1, os.SEEK_END)
        dernier = f.read(1)
    if dernier not in (b"\n", b"\r"):          # évite de coller la nouvelle ligne à l'ancienne
        with open(FICHIER, "a", encoding="utf-8", newline="") as f:
            f.write("\n")


def deja_etiquetees():
    with open(FICHIER, newline="", encoding="utf-8") as f:
        return {ligne["image"] for ligne in csv.DictReader(f)}


def demander(message, valide):
    """Repose la question tant que la réponse n'est pas valide (q = quitter)."""
    while True:
        saisie = input(message).strip()
        if saisie.lower() == "q" or valide(saisie):
            return saisie
        print("  Valeur non valide, réessaie (ou q pour quitter).")


preparer_fichier()
faites = deja_etiquetees()
chemins = [c for c in sorted(glob.glob(f"data/images/{SPLIT}/images/*"))
           if os.path.basename(c) not in faites]
print(f"{len(faites)} images déjà étiquetées, {len(chemins)} restantes.")
print("Pour chaque plaque : numéro, lettre, code. Entrée = passer l'image, q = quitter.\n")

for chemin in chemins:
    nom = os.path.basename(chemin)
    img = cv2.imread(chemin)
    h, w = img.shape[:2]
    x1, y1, x2, y2 = lire_verite(chemin)
    marge = 10
    plaque = img[max(0, y1 - marge):min(h, y2 + marge), max(0, x1 - marge):min(w, x2 + marge)]
    if plaque.size == 0:
        continue
    facteur = max(1, 400 // max(1, plaque.shape[1]))          # agrandit les petites plaques
    plaque = cv2.resize(plaque, None, fx=facteur, fy=facteur, interpolation=cv2.INTER_CUBIC)
    cv2.imshow("Plaque", plaque)
    cv2.waitKey(200)

    print(f"Image : {nom}")
    numero = demander("  numéro (1 à 5 chiffres) : ",
                      lambda s: s == "" or (s.isdigit() and 1 <= len(s) <= 5))
    if numero.lower() == "q":
        break
    if numero == "":
        print("  passée.\n")
        continue
    lettre = demander("  lettre (nom en lettres latines, ex. alif, ba, jim) : ",
                      lambda s: s != "").lower()
    if lettre == "q":
        break
    code = demander("  code régional (1 à 2 chiffres) : ",
                    lambda s: s.isdigit() and 1 <= len(s) <= 2)
    if code.lower() == "q":
        break
    commentaire = input("  commentaire (nette, floue, nuit, inclinée...) : ").strip()

    with open(FICHIER, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([nom, numero, lettre, code, commentaire])
    print("  enregistré.\n")

cv2.destroyAllWindows()
print("Terminé. Fichier :", FICHIER)