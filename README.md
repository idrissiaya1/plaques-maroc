# Reconnaissance des plaques d'immatriculation marocaines

Mini-projet du module Vision par Ordinateur.

## Objectif
Localiser une plaque marocaine sur une image de véhicule et lire
son contenu : numéro, lettre arabe, code régional.

## Installation
```bash
git clone https://github.com/TON_NOM/plaques-maroc.git
cd plaques-maroc
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Organisation
- `data/` : images et fichier de vérité terrain
- `src/` : code source
- `notebooks/` : essais
- `rapport/` : rapport final

## Méthode
1. Localisation de la plaque
2. Redressement et prétraitement
3. Segmentation et reconnaissance
4. Mise en forme et vérification

## Résultats
(à compléter à la fin du projet)