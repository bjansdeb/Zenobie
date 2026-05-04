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
    #peut-être penser à inclure un dry run
    logger.info("Removing empty repositories has started")
    abs_path = os.path.abspath(copies_rep) #abspath retourne le chemin absolu exact de l'objet, utile pour vérifier des paths relatifs
    if not os.path.isdir(abs_path):
        raise ValueError(f"Directory does not exist: {abs_path}")
    elif is_dangerous_root(abs_path): 
        raise ValueError(f"Dangerous path refused: {abs_path}")
    logger.info(f"Zenobie has checked {abs_path} before the removing process. The path is secure")

    removed = 0 
    initial_root = abs_path
    for root, dirs, files in os.walk(abs_path, topdown=False):
        try:
            if root == initial_root:
                continue
            if not os.listdir(root):
                os.rmdir(root) 
                logging.info(f"Removed: {root}")            
                removed += 1
        except Exception as e:
            logging.error(f"Error on {root}: {e}")         
    logger.info(f"Removing process done. Zenovie has removed {removed} empty repositories")

def is_dangerous_root(path):
    path = os.path.abspath(path)

    # si le chemin absolu indiqué correspond à la racine du système
    if os.path.abspath(path) == os.path.abspath(os.sep):
        return True

    # vérifie si le chemin donné n'est pas D:/, C:/, etc...
    if os.name == "nt":
        drive, tail = os.path.splitdrive(path)
        if path == drive + os.sep:
            return True

    home = os.path.abspath(os.path.expanduser("~"))
    try:
        if os.path.samefile(path, home):
            return True
    except FileNotFoundError:
        pass

    return False


if __name__ == "__main__":
    main()

