import json
import logging
import math
import os
import sys

from PIL import Image


GREEN_ID = 11

logging.basicConfig(level=logging.INFO)


def closest_color(pixel_rgb, colors):
    r, g, b = pixel_rgb
    min_distance = float("inf")
    closest_id = None

    for color in colors:
        # Calculate Euclidean distance between colors
        dr = r - color["red"]
        dg = g - color["green"]
        db = b - color["blue"]
        distance = math.sqrt(dr * dr + dg * dg + db * db)

        if distance < min_distance:
            min_distance = distance
            closest_id = color["id"]
            if closest_id == GREEN_ID:  # Si c'est vert, on retourne None
                return None

    return closest_id


def convert_image(image_path, output_path):
    # Définition des couleurs
    colors = [
        {"id": 1, "name": "white", "red": 236, "green": 240, "blue": 241},
        {"id": 2, "name": "lightgray", "red": 165, "green": 180, "blue": 190},
        {"id": 3, "name": "darkgray", "red": 105, "green": 121, "blue": 135},
        {"id": 4, "name": "black", "red": 44, "green": 62, "blue": 80},
        {"id": 5, "name": "pink", "red": 255, "green": 167, "blue": 209},
        {"id": 18, "name": "darkred", "red": 190, "green": 0, "blue": 57},
        {"id": 6, "name": "red", "red": 231, "green": 76, "blue": 60},
        {"id": 7, "name": "orange", "red": 230, "green": 126, "blue": 34},
        {"id": 8, "name": "brown", "red": 160, "green": 106, "blue": 66},
        {"id": 17, "name": "beige", "red": 255, "green": 224, "blue": 180},
        {"id": 9, "name": "yellow", "red": 241, "green": 196, "blue": 15},
        {"id": 10, "name": "lime", "red": 54, "green": 222, "blue": 127},
        {"id": 11, "name": "green", "red": 2, "green": 162, "blue": 1},
        {"id": 12, "name": "cyan", "red": 0, "green": 211, "blue": 212},
        {"id": 13, "name": "blue", "red": 0, "green": 152, "blue": 255},
        {"id": 14, "name": "indigo", "red": 0, "green": 65, "blue": 176},
        {"id": 15, "name": "magenta", "red": 207, "green": 110, "blue": 228},
        {"id": 16, "name": "purple", "red": 155, "green": 28, "blue": 182},
    ]

    # Charger l'image
    img = Image.open(image_path)

    # Convertir en RGB si nécessaire
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Récupérer les dimensions de l'image source
    width, height = img.size

    # Préparer le résultat
    result = {"width": width, "height": height, "pattern": []}

    # Parcourir chaque pixel
    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            color_id = closest_color(pixel, colors)

            # Ajouter seulement si une couleur valide est trouvée (non verte)
            if color_id is not None:
                result["pattern"].append({"x": x, "y": y, "color": color_id})

    # Sauvegarder en JSON
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)


def main():
    # Vérifier si un argument a été fourni
    arg_count = 2
    if len(sys.argv) != arg_count:
        logging.info("Usage: python script.py <chemin_image.png>")
        sys.exit(1)

    # Récupérer le chemin de l'image source
    file_argc = 1
    input_path = sys.argv[file_argc]

    # Vérifier si le fichier existe
    if not os.path.exists(input_path):
        logging.info("Erreur: Le fichier %s n'existe pas", input_path)
        sys.exit(1)

    # Vérifier l'extension du fichier
    if not input_path.lower().endswith((".png", ".jpg", ".jpeg")):
        logging.info("Erreur: Le fichier doit être une image (PNG, JPG, JPEG)")
        sys.exit(1)

    # Créer le nom du fichier de sortie
    output_path = os.path.splitext(input_path)[0] + ".json"

    convert_image(input_path, output_path)
    logging.info("Conversion réussie ! Fichier de sortie : %s", output_path)


if __name__ == "__main__":
    main()
