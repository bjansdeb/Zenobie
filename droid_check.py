import csv
import os
import subprocess

from log import log_it
from reporting import write_report


def main():

    copies_repository = str(input("Path:"))
    reports = ""
    droid_check(copies_repository, reports)
    droid_premis_match()
    

def droid_check(rep, reports):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    droid_path = os.path.join(base_dir, "droid", "droid.bat") #subprocess refuses relative paths

    if os.path.isfile(droid_path):
        try:
            log_it("info", "DROID has been launched, please note that that can take a few minutes...")
            result = subprocess.run([droid_path, "-a", rep,"-Pr 'profile.generateHash=true'", "-R"], text=True, capture_output=True, check=True)
            write_report("droid_report.csv", reports, "droid", result)
            log_it("info", "DROID has successfully finished ! " \
            f"You can see the report into {reports}")      

        except subprocess.CalledProcessError as e:
            print(e.stderr, e.stdout)

    else :
        log_it("error","droid check has failed because droid.bat is not present on the Zenobie repository (droid/droid.bat). " \
        "Please install it and retry")

def droid_premis_match():
    if os.path.isfile("droid_report.csv"):
        with open("droid_report.csv", "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                print(row.get("NAME"))
                row.get("FILE_PATH")
                row.get("PUID")
                print(row.get("MIME_TYPE"))
                print(row.get("HASH"))
    else:
        log_it("error", "Zenobie does not find the droid_report.csv file")            

if __name__ == "__main__":
    main()