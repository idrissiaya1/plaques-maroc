# src/localisation.py
# Localisation d'une plaque : gris, flou, Canny, fermeture, contours, filtre.
import cv2


def localiser_plaque(img):
    """Renvoie (x, y, w, h) de la meilleure plaque candidate, ou None."""
    h_img, w_img = img.shape[:2]

    # 1) Préparation
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    flou = cv2.bilateralFilter(gris, 11, 17, 17)
    bords = cv2.Canny(flou, 150, 200)

    # 2) Fermeture : relie les bords proches en blocs horizontaux
    noyau = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 2))
    blocs = cv2.morphologyEx(bords, cv2.MORPH_CLOSE, noyau)

    # 3) Contours des blocs
    contours, _ = cv2.findContours(blocs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 4) Filtre : ratio, aire, puis le plus rectangulaire
    meilleur, meilleur_score = None, 0
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if h == 0:
            continue
        ratio = w / h
        aire = w * h
        if 2.0 < ratio < 6.0 and 0.002 * h_img * w_img < aire < 0.3 * h_img * w_img:
            rectangularite = cv2.contourArea(c) / aire
            if rectangularite > meilleur_score:
                meilleur, meilleur_score = (x, y, w, h), rectangularite
    return meilleur