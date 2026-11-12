# src/verifier_csv.py
# Contrôle data/verite_terrain.csv : en-tête, noms de lettres, formats, doublons, images.
import collections
import csv
import glob
import os

FICHIER = "data/verite_terrain.csv"
ATTENDUES = ["image", "numero", "lettre", "code", "commentaire"]
MAX_AFFICHES = 20          # nombre maximal de problèmes détaillés à l'écran

with open(FICHIER, newline="", encoding="utf-8-sig") as f:
    lecteur = csv.DictReader(f)
    colonnes = lecteur.fieldnames
    lignes = list(lecteur)

print(f"{len(lignes)} lignes lues dans {FICHIER}")
print("En-tête lu :", colonnes)

# 0) L'en-tête doit être exact, sinon tout le reste est faux
manquantes = [c for c in ATTENDUES if c not in (colonnes or [])]
if manquantes:
    print(f"\nARRÊT : colonne(s) absente(s) ou mal écrite(s) : {manquantes}")
    print("La première ligne du fichier doit être exactement :")
    print("  image,numero,lettre,code,commentaire")
    raise SystemExit

# 1) Les noms de lettres utilisés : un nom rare est souvent une faute de frappe
lettres = collections.Counter((l.get("lettre") or "").strip().lower() for l in lignes)
print("\nLettres utilisées (nom : nombre de plaques) :")
for nom, nb in sorted(lettres.items()):
    alerte = "   <-- rare : faute de frappe ?" if nb <= 2 else ""
    print(f"  {nom:12s}: {nb}{alerte}")

# 2) Les autres contrôles, ligne par ligne (la ligne 1 est l'en-tête)
images_existantes = {os.path.basename(c) for c in glob.glob("data/images/*/images/*")}
vues = collections.Counter(l.get("image") for l in lignes)
problemes = []           # (numéro de ligne, catégorie, détail)
for numero_ligne, l in enumerate(lignes, start=2):
    image = (l.get("image") or "").strip()
    numero = (l.get("numero") or "").strip()
    code = (l.get("code") or "").strip()
    lettre = (l.get("lettre") or "").strip()
    if None in l:
        problemes.append((numero_ligne, "trop de colonnes", "ligne collée à une autre ?"))
    if image not in images_existantes:
        problemes.append((numero_ligne, "image introuvable", image))
    if vues[l.get("image")] > 1:
        problemes.append((numero_ligne, "image en double", image))
    if not (numero.isdigit() and 1 <= len(numero) <= 5):
        problemes.append((numero_ligne, "numéro invalide", numero))
    if not (code.isdigit() and 1 <= len(code) <= 2):
        problemes.append((numero_ligne, "code invalide", code))
    if lettre == "":
        problemes.append((numero_ligne, "lettre vide", ""))

print(f"\nProblèmes trouvés : {len(problemes)}")
par_categorie = collections.Counter(p[1] for p in problemes)
for categorie, nb in par_categorie.items():
    print(f"  {categorie} : {nb}")
for numero_ligne, categorie, detail in problemes[:MAX_AFFICHES]:
    print(f"  ligne {numero_ligne} : {categorie} {detail}")
if len(problemes) > MAX_AFFICHES:
    print(f"  ... et {len(problemes) - MAX_AFFICHES} autres (corrige les premiers, puis relance)")
if not problemes:
    print("  aucun : le fichier est propre.")