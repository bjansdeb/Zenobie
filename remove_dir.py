import os

def main():

    path = str(input("path : "))
    remove_empty(path)


def remove_empty(copies_rep):
    for root, dirs, files in os.walk(copies_rep, topdown=False):
        if os.path.isdir(root):
            if len(os.listdir(root)) == 0:
                print(len(os.listdir(root)), root)
                os.rmdir(root)
        # if bytes == 0 :
        #     print(f"this rep is empty {root}")

        # bytes = sum(os.path.getsize(os.path.join(root, file)) for file in files)
        # if bytes == 0:
        #     print(root) #ajouter un tableau ou un rapport reprenant tous les dossiers vides et demande de confirmation avant de supprimer
        #     os.rmdir(root)

if __name__ == "__main__":
    main()

