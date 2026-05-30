import subprocess
from pathlib import Path
from datetime import datetime
import os
import subprocess
import uuid
import time

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
    try:
        while True:
            selected_module = str(input('Do you want to convert a file or multiple files inside a repository ? (file/repository):'))
            if selected_module == "file" or "repository":
                break
            else :
                raise ValueError
    except FileNotFoundError:
            print("File not found, retry")
            pass    
    
    if selected_module == "file":
        try:
            while True:
                file_path = str(input('file to convert:'))
                break
        except FileNotFoundError:
                print("File not found, retry")
                pass
        
        libre_office_path = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
        input_file = Path(fr"{file_path}")
        ouput_dir = Path(r"C:\Users\bjans\Desktop")

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
        result = subprocess.run([str(libre_office_path), "--headless", "--convert-to", pdf_options, "--outdir", str(ouput_dir), str(input_file)], text=True, capture_output=True, check=True)
        #-o headless following files for editing, regardless whether they are templates or not.
        write_report(input_file, role, user)
        print(result.stderr, result.stdout)
        print("Process done")    

    elif selected_module == "repository":
        try:
            while True:
                repository_path = str(input('repository to convert:'))
                break
        except NotADirectoryError:
                print("Repository not found, retry")
                pass
        libre_office_path = Path(r"C:\Program Files\LibreOffice\program\soffice.exe")
        input_repository = Path(fr"{repository_path}")
    


def write_report(input_file, role, user):
    log_repository= "/"
    report_path = os.path.join(log_repository, "hashs_report.txt")
    with open(report_path,"w+t", encoding="utf-8") as hash_r:
        hash_r.write("-------------")       
        hash_r.write(f"\nHash report")
        hash_r.write(f"\nDone at {horodatage()} by {user}, {role} at AVG-Carhif using Python 3.10")       
        hash_r.write(f"\n--------")  
        hash_r.write(f"\nEvent id type: digital signature generation")
        hash_r.write(f"\nEvent id: {uuid.uuid1().hex}")
        hash_r.write(f"\nEvent date time: {horodatage()}")        
        hash_r.write(f"\nEvent outcome: success") 

def horodatage():
    return datetime.datetime.now().strftime('%a %d %b %Y, %I:%M%p')

if __name__ == "__main__":
    main()