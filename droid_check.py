import os
import subprocess


from log import log_it
from models import PremisObjects
from reporting import write_report


def main():

    copies_repository = str(input("Path:"))
    reports = ""
    registre = PremisObjects()

    droid_check(copies_repository, reports, registre)

def droid_check(rep, reports, registre):
    """à rajouter plus tard, pour obtenir certains types de métadonnées"""
    #$ droid -co NAME PUID -a file.jpg
    #"NAME","PUID"
    #"file.jpg","fmt/1507"
    """"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    droid_path = os.path.join(base_dir, "droid", "droid.bat")
    #subprocess refuses relative paths

    if os.path.isfile(droid_path):
        try:
            result = subprocess.run([droid_path, "-a", rep, "-R"], text=True, capture_output=True, check=True)
            write_report("droid_report.txt", reports, "droid", result)
        except subprocess.CalledProcessError as e:
            print(e.stderr, e.stdout)

    else :
        log_it("error","droid check has failed because droid.bat is not present on the Zenobie repository (droid/droid.bat). " \
        "Please install it and retry")

if __name__ == "__main__":
    main()