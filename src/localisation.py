# src/localisation.py
# Localisation d'une plaque : gris, flou, Canny, fermeture, contours,
# puis choix du meilleur candidat par un score (densité de bords, forme, ratio).
import cv2

# ---- Paramètres à régler (ils sont lus à chaque appel de la fonction) ----
CANNY_BAS = 100                     # seuil bas de Canny
CANNY_HAUT = 200                    # seuil haut de Canny
NOYAU = (9, 3)                      # fermeture : (largeur, hauteur) du noyau
RATIO_MIN = 2.0                     # rapport largeur/hauteur minimal
RATIO_MAX = 9.0                     # rapport largeur/hauteur maximal
RATIO_IDEAL = 4.5                   # rapport typique d'une plaque marocaine
AIRE_MIN = 0.008                   # aire minimale du cadre / aire de l'image
AIRE_MAX = 0.15                     # aire maximale du cadre / aire de l'image


def localiser_plaque(img):
    """Renvoie (x, y, w, h) de la meilleure plaque candidate, ou None."""
    h_img, w_img = img.shape[:2]
    surface = h_img * w_img

    # 1) Préparation : gris, flou qui garde les bords, bords de Canny
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    flou = cv2.bilateralFilter(gris, 11, 17, 17)
    bords = cv2.Canny(flou, CANNY_BAS, CANNY_HAUT)

    # 2) Fermeture : relie les bords proches en blocs horizontaux
    noyau = cv2.getStructuringElement(cv2.MORPH_RECT, NOYAU)
    blocs = cv2.morphologyEx(bords, cv2.MORPH_CLOSE, noyau)

    # 3) Contours des blocs
    contours, _ = cv2.findContours(blocs, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    # 4) Filtre puis score pour chaque candidat
    meilleur, meilleur_score = None, 0.0
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if h == 0:
            continue
        ratio = w / h
        aire = w * h
        if not (RATIO_MIN < ratio < RATIO_MAX):
            continue
        if not (AIRE_MIN * surface < aire < AIRE_MAX * surface):
            continue

        # Densité de bords : une plaque (texte) en contient beaucoup
        densite = cv2.countNonZero(bords[y:y + h, x:x + w]) / aire
        # Rectangularité : proche de 1 = forme bien rectangulaire
        rectangularite = cv2.contourArea(c) / aire
        # Ratio : meilleur score quand il est proche du ratio idéal
        score_ratio = 1 - min(abs(ratio - RATIO_IDEAL) / RATIO_IDEAL, 1)

        score = densite * rectangularite * score_ratio
        if score > meilleur_score:
            meilleur, meilleur_score = (x, y, w, h), score

    return meilleur