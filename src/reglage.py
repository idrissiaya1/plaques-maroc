# src/reglage.py
# Script de réglage pour tester l'impact des paramètres sur la localisation
import os
import cv2
import glob

# Importation de votre fonction d'évaluation existante
from evaluer_localisation import lire_verite, iou
from localisation import localiser_plaque

SPLIT = "valid"
SEUIL_IOU = 0.5

def tester_parametres(canny_bas=50, noyau=3, ratio_min=2.0, ratio_max=6.0):
    """
    Fonction pour tester un jeu de paramètres spécifique.
    (Vous pouvez adapter les noms des variables selon votre fichier localisation.py)
    """
    chemins = sorted(glob.glob(f"data/images/{SPLIT}/images/*"))
    corrects, non_trouvees = 0, 0
    
    for chemin in chemins:
        img = cv2.imread(chemin)
        
        # Si votre fonction localiser_plaque accepte des paramètres personnalisés, 
        # vous pouvez les passer ici. Sinon, ajustez-les directement dans localisation.py
        boite = localiser_plaque(img)
        
        if boite is None:
            non_trouvees += 1
            continue
            
        x, y, w, h = boite
        if iou((x, y, x + w, y + h), lire_verite(chemin)) >= SEUIL_IOU:
            corrects += 1
            
    taux = 100 * corrects / len(chemins)
    print(f"Paramètres testés -> Corrects: {corrects}/{len(chemins)} ({taux:.1f} %) | Non trouvées: {non_trouvees}")
    return taux

if __name__ == "__main__":
    print("--- Lancement des tests de réglage ---")
    # Premier test avec les valeurs par défaut
    tester_parametres()
