import subprocess
from pathlib import Path
from datetime import datetime
import os
import subprocess
import uuid
import time

options =  {
    "SelectPdfVersion": {
        "type": "long",
        "value": "3" #3: PDF/A-3b
    },
    "UseTaggedPDF": {
        "type": "boolean",
        "value": "true"
    },
    "EmbedStandardFonts": {
        "type": "boolean",
        "value": "true"
    },
    "ExportBookmarks": {
        "type": "boolean",
        "value": "true"
    },
    "ReduceImageResolution": {
        "type": "boolean",
        "value": "false"
    },
    "Quality": {
        "type": "long",
        "value": "100"
    }
    }
pdf_options = (f'pdf:writer_pdf_Export:{options}')
libre_office_path = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")


def main():
    print("Robocopy launched")
    time.sleep(1)
    print("Note : you may quit the script at any time doing crtl+c")
    time.sleep(3)
    user = ""
    role = ""
    institution = ""
    selected_module = ""
    while True : 
        try:
            user = str(input("Hello buddy, what's your name ? :"))
            if user == "":
                raise ValueError
            else :
                break

        except ValueError:
            pass
    while True:
        try:
            institution = str(input(f"Great {user}, what is the name of your instution ? :"))
            if institution == "":
                raise ValueError
            else :
                break
        except ValueError:
            pass
    while True:
        try: 
            role = str(input(f"Super! Now what's your role at {institution} (archivist, librarian...) ? : "))
            if role == "":
                raise ValueError
            else :
                print("Ok, so you are an", role)
                time.sleep(2)
                break

        except ValueError:
            pass
    # while True:
    #     try:
    #         log_repository = fr'{str(input("Path report (repository where to put your reports, f.i. : C:/archives/report):"))}'
    #         if not os.path.exists(log_repository):
    #             raise ValueError
    #         else:
    #             break
    #     except ValueError:
    #         print('This path does not exist. Please retry')
    #         pass     
    try:
        while True:
            selected_module = str(input('Do you want to convert a file or multiple files inside a repository ? (file/repository):').lower())
            if selected_module == "file" or "repository":
                break
            else :
                raise ValueError
    except FileNotFoundError:
            print("You must answeer by file or repository, retry")
            pass    
    
    if selected_module == "file":
        try:
            while True:
                file_path = str(input('file to convert:'))
                break
        except FileNotFoundError:
                print("File not found, retry")
                pass
        
        input_file = Path(fr"{file_path}")
        ouput_dir = Path(r"C:\Users\bjans\Desktop")
        result = subprocess.run([str(libre_office_path), "--headless", "--convert-to", pdf_options, 
                                 "--outdir", str(ouput_dir), str(input_file)], text=True, capture_output=True, check=True)
        #-o headless following files for editing, regardless whether they are templates or not.
        write_report(input_file, role, user)
        print(result.stderr, result.stdout)
        print("Process done")    

    elif selected_module == "repository":
        CONVERTIBLE_EXT = {".doc", ".docx"}
        try:
            while True:
                repository_path = str(input('Repository to convert:'))
                break
        except NotADirectoryError:
                print("Repository not found, retry")
                pass
        libre_office_path = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
        input_repository = Path(fr"{repository_path}")
        for root, _, files in os.walk(input_repository):  #_ était dirs
            for file in files :
                file_path =os.path.join(root, file)
                _, extension = os.path.splitext(file_path)
                if extension in CONVERTIBLE_EXT:
                    input_file = Path(fr"{file_path}")
                    ouput_dir = Path(r"C:\Users\bjans\Desktop")
                    result = subprocess.run([str(libre_office_path), "--headless", "--convert-to", pdf_options, "--outdir", str(ouput_dir), str(input_file)], text=True, capture_output=True, check=True)
                    write_report(input_file, role, user, institution)



def write_report(input_file, role, user, institution):
    log_repository= "/"
    # integrity_path = os.path.join(log_repository, "integrity_problems.txt")
    report_path = os.path.join(log_repository, "migrations_report.txt")
    with open(report_path,"w+t", encoding="utf-8") as pdfa_r:
        pdfa_r.write("-------------")       
        pdfa_r.write(f"\nMigration report")
        pdfa_r.write(f"\nDone at {horodatage()} by {user}, {role} at {institution} using Python 3.10")       
        pdfa_r.write(f"\n--------")  
        pdfa_r.write(f"\nEvent id type: migration")
        pdfa_r.write(f"\nEvent id: {uuid.uuid1().hex}")
        pdfa_r.write(f"\nEvent date time: {horodatage()}")
        pdfa_r.write(f"\nEvent detail: {str(input_file)} has been converted into PDF/A-3B")                
        pdfa_r.write(f"\nEvent outcome: success") 

def horodatage():
    return datetime.datetime.now().strftime('%a %d %b %Y, %I:%M%p')

if __name__ == "__main__":
    main()