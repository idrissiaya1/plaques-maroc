# src/reglage.py
# Teste l'impact d'un paramètre de localisation.py sur le taux de localisation.
import glob
import cv2

import localisation as L
from evaluer_localisation import lire_verite, iou

SPLIT = "valid"        # on règle sur valid ; test est réservé à la mesure finale
SEUIL_IOU = 0.5

# --- Chargement unique : les images sont lues une seule fois ---
chemins = sorted(glob.glob(f"data/images/{SPLIT}/images/*"))
images = [cv2.imread(c) for c in chemins]
verites = [lire_verite(c) for c in chemins]


def evaluer():
    """Lance localiser_plaque sur toutes les images et compte les résultats."""
    corrects, non_trouvees = 0, 0
    for img, verite in zip(images, verites):
        boite = L.localiser_plaque(img)
        if boite is None:
            non_trouvees += 1
            continue
        x, y, w, h = boite
        if iou((x, y, x + w, y + h), verite) >= SEUIL_IOU:
            corrects += 1
    taux = 100 * corrects / len(images)
    return corrects, non_trouvees, taux


def tester_parametres(**params):
    """Change temporairement des paramètres de localisation.py, évalue, puis remet tout."""
    for nom in params:
        if not hasattr(L, nom):
            raise AttributeError(f"'{nom}' n'existe pas dans localisation.py")
    originaux = {nom: getattr(L, nom) for nom in params}
    for nom, valeur in params.items():
        setattr(L, nom, valeur)
    try:
        corrects, non_trouvees, taux = evaluer()
    finally:
        for nom, valeur in originaux.items():
            setattr(L, nom, valeur)
    mauvais = len(images) - corrects - non_trouvees
    print(f"{params} -> corrects {corrects}/{len(images)} ({taux:.1f} %) | "
          f"sans résultat {non_trouvees} | mauvais rectangle {mauvais}")
    return taux


def balayer(parametre, valeurs):
    """Teste plusieurs valeurs d'un seul paramètre."""
    print(f"\n--- Test de {parametre} ---")
    for valeur in valeurs:
        tester_parametres(**{parametre: valeur})


if __name__ == "__main__":
    print(f"Images de {SPLIT} : {len(images)}")
    print("\n--- Référence (valeurs actuelles de localisation.py) ---")
    tester_parametres()

    balayer("CANNY_HAUT", [150, 200, 250])
    balayer("RATIO_IDEAL", [3.5, 4.0, 4.5, 5.0])
    balayer("NOYAU", [(7, 3), (9, 3), (11, 3), (9, 5)])