import os
import logging

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("app.log", mode="w", encoding="utf-8")
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.setLevel("DEBUG")
formatter = logging.Formatter("{name} - {asctime} - {levelname} : {message}", style="{", datefmt="%Y-%m-%d %H:%M")
console_handler.setFormatter(formatter)

logger.info("Lancement du script")
def main():
    path = str(input("path : "))
    remove_empty(path)


def remove_empty(copies_rep):
    abs_path = os.path.abspath(copies_rep) #abspath retourne le chemin absolu exact de l'objet, utile pour vérifier des paths relatifs
    if not os.path.isdir(abs_path):
        raise ValueError(f"Directory does not exist: {abs_path}")
    elif is_dangerous_root(abs_path): 
        raise ValueError(f"Dangerous path refused: {abs_path}")

    for root, dirs, files in os.walk(abs_path, topdown=False):
        if len(os.listdir(root)) == 0:
            print(len(os.listdir(root)), root)
                # os.rmdir(root)


def is_dangerous_root(path):
    path = os.path.abspath(path)

    # si le chemin absolu indiqué correspond à la racine du système
    if os.path.abspath(path) == os.path.abspath(os.sep):
        return True

    # Windows drive root
    if os.name == "nt":
        drive, tail = os.path.splitdrive(path)
        if path == drive + os.sep:
            return True

    # User home
    home = os.path.abspath(os.path.expanduser("~"))
    try:
        if os.path.samefile(path, home):
            return True
    except FileNotFoundError:
        pass

    return False


if __name__ == "__main__":
    main()

