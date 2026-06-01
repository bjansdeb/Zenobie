import subprocess
from pathlib import Path
import datetime
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
    print("PDFA launched")
    time.sleep(1)
    print("Note : you may quit the script at any time doing crtl+c")
    time.sleep(3)
    user = ""
    role = ""
    institution = ""
    selected_module = ""
    converted_files = {}
    non_converted_files = {}    
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
            institution = str(input(f"Great {user}, what is the name of your institution ? :"))
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

    while True:
            try:
                selected_module = str(input('Do you want to convert a file or multiple files inside a repository ? (file/repository):').lower())
                if selected_module == "file" or selected_module == "repository":
                    break
                else :
                    raise ValueError
            except ValueError:
                    print("You must answeer by file or repository, retry")
                    pass    
    
    if selected_module == "file":
        while True:
            try:
                file_path = str(input('file to convert:'))
                if os.path.isfile(file_path):
                    break
                else:
                    raise FileNotFoundError
            except FileNotFoundError:
                print("File not found, retry")
                pass
        
        input_file = Path(fr"{file_path}")
        repository_path = os.path.dirname(file_path)
        ouput_dir = Path(fr"{repository_path}")
        if check_file_conflict(input_file, ouput_dir):
            result = subprocess.run([str(libre_office_path), "--headless", "--convert-to", pdf_options, 
                                 "--outdir", str(ouput_dir), str(input_file)], text=True, capture_output=True, check=True)
            if result.returncode == 0 :
                converted_files[str(input_file)] = horodatage()
            elif result.returncode != 0 :
                non_converted_files[str(input_file)] = horodatage()
        else :
            non_converted_files[str(input_file)] = horodatage()

        #-o headless following files for editing, regardless whether they are templates or not.
        # if result.returncode == 0 :
        write_report(converted_files, non_converted_files, repository_path, role, user, institution)

        #converted_files, input_repository, role, user, institution

    elif selected_module == "repository":
        CONVERTIBLE_EXT = {".doc", ".docx"}
        while True:
            try:
                repository_path = str(input('Repository to convert:'))
                break
            except NotADirectoryError:
                    print("Repository not found, retry")
                    pass
        input_repository = Path(fr"{repository_path}")
        for root, _, files in os.walk(input_repository):  #_ était dirs
            for file in files :
                file_path =os.path.join(root, file)
                _, extension = os.path.splitext(file_path)
                if extension in CONVERTIBLE_EXT:
                    input_file = Path(fr"{file_path}")
                    ouput_dir = Path(fr"{root}") #Path(r"C:\Users\bjans\Desktop")
                    result = subprocess.run([str(libre_office_path), "--headless", "--convert-to", pdf_options, "--outdir", str(ouput_dir), str(input_file)], text=True, capture_output=True, check=True)
                    if result.returncode == 0 :
                        converted_files[str(input_file)] = horodatage()
                    elif result.returncode != 0 :
                        non_converted_files[str(input_file)] = horodatage()
        write_report(converted_files, non_converted_files, input_repository, role, user, institution)

    print("process done")

def write_report(converted_files, non_converted_files, log_repository, role, user, institution):
    report_path = os.path.join(log_repository, "migrations_report.txt")
    with open(report_path,"w+t", encoding="utf-8") as pdfa_r:
        pdfa_r.write("-------------")       
        pdfa_r.write(f"\nMigration report")
        pdfa_r.write(f"\nDone at {horodatage()} by {user}, {role} at {institution} using Python 3.10 and Libre Office")       
        pdfa_r.write(f"\n--------")  
        for file in converted_files:
            pdfa_r.write(f"\nEvent id type: migration")
            pdfa_r.write(f"\nEvent id: {uuid.uuid1().hex}")
            pdfa_r.write(f"\nEvent date time: {converted_files[file]}")
            pdfa_r.write(f"\nEvent detail: {str(file)} has been converted into PDF/A-3B")                
            pdfa_r.write(f"\nEvent outcome: success") 
        for file in non_converted_files:
            pdfa_r.write(f"\nEvent id type: migration")
            pdfa_r.write(f"\nEvent id: {uuid.uuid1().hex}")
            pdfa_r.write(f"\nEvent date time: {non_converted_files[file]}")
            pdfa_r.write(f"\nEvent detail: {str(file)} has not been converted into PDF/A-3B")                
            pdfa_r.write(f"\nEvent outcome: failure")        

def check_file_conflict(input_file, output_repository):
    target = output_repository / f"{input_file.stem}.pdf"
    # filename, extension = os.split(input_file)
    if target.exists():
        return False
    else:
        return True
    # for root, _, files in os.walk(input_repository):  #_ était dirs
    #     for file in files :
    #         filename = os.path.join(root, file)
    #         if Path(filename) == input_file.with_suffix(".pdf"):
    #             print("there is a problem")
    #             return False
            
    # return True


def horodatage():
    return datetime.datetime.now().strftime('%a %d %b %Y, %I:%M%p')

if __name__ == "__main__":
    main()