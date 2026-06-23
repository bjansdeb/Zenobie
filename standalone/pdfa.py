import subprocess
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import uuid
import time


CONVERTIBLE_EXT = {".doc", ".docx"}
HASHABLE_EXT = {".doc", ".docx", ".pdf"} #utilisé pour calculer les hashs uniquement pour les fichiers concernés par la conversion (input et ouput)

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
veraPDF_path = Path(r'C:\Users\BenjaminJanssensdeBi\OneDrive - Archief- en Onderzoekscentrum voor Vrouwengeschiedenis\Desktop\veraPDF\verapdf.bat')


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
    time.sleep(1)
    if selected_module == "file":
        while True:
            try:
                file_path = str(input('file to convert:'))
                if os.path.isfile(file_path):
                    _, extension = os.path.splitext(file_path)
                    if extension.lower() in CONVERTIBLE_EXT:
                        print("converting file...")
                        break
                    else :
                        raise TypeError
                else:
                    raise FileNotFoundError
            except FileNotFoundError:
                print("File not found, retry")
                pass
            except TypeError:
                print("The file must have a .doc or .docx extension, retry")
        
        input_file = Path(fr"{file_path}")
        repository_path = os.path.dirname(file_path)
        rel_path_file = get_relative_path(input_file, repository_path)

        ouput_dir = Path(fr"{repository_path}")
        if check_file_conflict(input_file, ouput_dir):
            result = subprocess.run([str(libre_office_path), "--headless", "--convert-to", pdf_options, 
                                 "--outdir", str(ouput_dir), str(input_file), f"/log+:{ouput_dir}/libre_office_migration_report.txt"], text=True, capture_output=True, check=True)
            if result.returncode == 0 :
                converted_files[str(f"{input_file.stem}.pdf")] = f"{str(rel_path_file)} was converted into PDF/A-3B - {horodatage()}"
            elif result.returncode != 0 :
                non_converted_files[str(input_file)] = f"{str(rel_path_file)} was not converted into PDF/A-3B due to a technical failure - {horodatage()}"
        else :
            non_converted_files[str(input_file)] = f"{str(rel_path_file)} was not converted into PDF/A-3B because a file with the same name already exists - {horodatage()}"

    # write_report(converted_files, non_converted_files, repository_path, role, user, institution)


    elif selected_module == "repository":
        while True:
            try:
                repository_path = str(input('Repository to convert:'))
                print("converting repository...")
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
                    rel_path_file = get_relative_path(input_file, input_repository)
                    ouput_dir = Path(fr"{root}") #Path(r"C:\Users\bjans\Desktop")
                    if check_file_conflict(input_file, ouput_dir):
                        result = subprocess.run([str(libre_office_path), "--headless", "--convert-to", pdf_options, 
                                            "--outdir", str(ouput_dir), str(input_file), f"/log+:{ouput_dir}/libre_office_migration_report.txt"], text=True, capture_output=True, check=True)
                        if result.returncode == 0 :
                            pdf_path = ouput_dir / f"{input_file.stem}.pdf"
                            converted_files[str(pdf_path)] = f" {str(rel_path_file)} was converted into PDF/A-3B. His name is now {input_file.stem}.pdf - {horodatage()}"
                        elif result.returncode != 0 :
                            non_converted_files[str(input_file)] = f"{str(rel_path_file)} was not converted into PDF/A-3B due to a technical failure - {horodatage()}"
                    else :
                        non_converted_files[str(input_file)] = f"{str(rel_path_file)} was not converted into PDF/A-3B because a file with the same name already exists - {horodatage()}"

    write_report(converted_files, non_converted_files, input_repository, role, user, institution)

    #validation des PDF/A
    print("validating pdf/a...")
    time.sleep(2)
    validation_data = {}
    for pdf_path in converted_files:
        # if file.lower().endswith(".pdf"): 
        validation_data[pdf_path] = pdfa_validation(veraPDF_path, pdf_path)

    report_path = os.path.join(input_repository, "PDFA_validation_report.json")
    with open (report_path, "w", encoding="utf-8") as validation_r :
        json.dump(validation_data, validation_r, indent=3)


    #calcul des hashs pour tous les fichiers indiqués et écriture dans un rapport
    print("calculating hashs...")
    time.sleep(2)
    sha_dict = {}
    for root, _, files, in os.walk(input_repository):
        for file in files :
            file_path = os.path.join(root, file)
            _, extension = os.path.splitext(file_path)
            if extension.lower() in HASHABLE_EXT:
                sha_sum = hash_calculator(file_path)
                rel_path_file = get_relative_path(file_path, input_repository)
                sha_dict[rel_path_file] = sha_sum

    report_path = os.path.join(input_repository, "hash_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(sha_dict, f, indent=3)

    print("process done, you can close the script with crtl+c")

def write_report(converted_files, non_converted_files, log_repository, role, user, institution):
    report_path = os.path.join(log_repository, "migrations_report.txt")
    with open(report_path,"w+t", encoding="utf-8") as pdfa_r:
        pdfa_r.write("-------------")       
        pdfa_r.write(f"\nMigration report")
        pdfa_r.write(f"\nDone at {horodatage()} by {user}, {role} at {institution} using Python 3.10 and Libre Office")       
        pdfa_r.write(f"\n--------")  
        for file in converted_files:
            pdfa_r.write(f"\nEvent id type: migration")
            pdfa_r.write(f"\nEvent id: {uuid.uuid4().hex}")
            pdfa_r.write(f"\nEvent date time: {horodatage()}")
            pdfa_r.write(f"\nEvent detail: {converted_files[file]}")                
            pdfa_r.write(f"\nEvent outcome: success") 
        for file in non_converted_files:
            pdfa_r.write(f"\nEvent id type: migration")
            pdfa_r.write(f"\nEvent id: {uuid.uuid4().hex}")
            pdfa_r.write(f"\nEvent date time: {horodatage()}")
            pdfa_r.write(f"\nEvent detail: {non_converted_files[file]}")                
            pdfa_r.write(f"\nEvent outcome: failure")        

def check_file_conflict(input_file, output_repository):
    target = output_repository / f"{input_file.stem}.pdf"
    if target.exists():
        return False
    else:
        return True

def get_relative_path(child_path: str, absolute_parent_path: str) -> str:
    """Calcule le chemin relatif pour un chemin individuel donné à partir du répertoire parent absolu"""
    child = Path(child_path)
    parent = Path(fr'{absolute_parent_path}')
    path = str(parent.name / child.relative_to(parent)) #.as_posix()
    return path #.as_posix()
    
def hash_calculator(source) -> str:
    sha = hashlib.sha256()
    with open(source, 'rb') as file:
        while chunk := file.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

def pdfa_validation(vera_path, source):
    #veraPDF 1.30.1
    result = subprocess.run([str(vera_path), "-f", "3b", "--format", "json", str(source)], text=True, capture_output=True)
    # print(result.stdout, result.stderr)

    return json.loads(result.stdout)

def horodatage():
    return datetime.datetime.now().strftime('%a %d %b %Y, %I:%M%p')

if __name__ == "__main__":
    main()
