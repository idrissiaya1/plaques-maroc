# src/tester_localisation.py
import glob
import cv2
import matplotlib.pyplot as plt
from localisation import localiser_plaque

images = sorted(glob.glob("data/images/valid/images/*"))[:6]

plt.figure(figsize=(12, 6))
for i, chemin in enumerate(images):
    img = cv2.imread(chemin)
    boite = localiser_plaque(img)
    if boite is not None:
        x, y, w, h = boite
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)  # rouge (BGR)
    plt.subplot(2, 3, i + 1)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title("trouvée" if boite else "aucune plaque", fontsize=9)
    plt.axis("off")
plt.tight_layout()
plt.show()