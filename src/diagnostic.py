# src/diagnostic.py
# Montre les blocs trouvés et TOUS les candidats, pas seulement le "meilleur".
import glob
import cv2
import matplotlib.pyplot as plt

INDICE = 0     # change ce numéro pour tester d'autres images
chemin = sorted(glob.glob("data/images/valid/images/*"))[INDICE]
img = cv2.imread(chemin)
h_img, w_img = img.shape[:2]

gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
flou = cv2.bilateralFilter(gris, 11, 17, 17)
bords = cv2.Canny(flou, 30, 200)
noyau = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 3))
blocs = cv2.morphologyEx(bords, cv2.MORPH_CLOSE, noyau)

contours, _ = cv2.findContours(blocs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

resultat = img.copy()
for c in contours:
    x, y, w, h = cv2.boundingRect(c)
    if h == 0:
        continue
    ratio = w / h
    if 1.5 < ratio < 8 and w * h > 0.001 * h_img * w_img:
        cv2.rectangle(resultat, (x, y), (x + w, y + h), (255, 0, 0), 2)  # bleu
        print(f"x={x} y={y} w={w} h={h} ratio={ratio:.1f} "
              f"rect={cv2.contourArea(c) / (w * h):.2f}")

fig, ax = plt.subplots(1, 3, figsize=(14, 5))
ax[0].imshow(bords, cmap="gray");  ax[0].set_title("Canny")
ax[1].imshow(blocs, cmap="gray");  ax[1].set_title("après fermeture")
ax[2].imshow(cv2.cvtColor(resultat, cv2.COLOR_BGR2RGB)); ax[2].set_title("tous les candidats")
for axe in ax:
    axe.axis("off")
plt.tight_layout()
plt.show()