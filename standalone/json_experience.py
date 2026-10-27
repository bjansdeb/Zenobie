import json

def main():
    try:
        with open('objects.json', 'r', encoding='utf-8') as f:
            data = f.read() #sort un string
        json_file = deserialize(data) #transforme le string en dict
        json_object = json_file['38e46a3bd1f211f1b05888a4c23be911']
        json_object['size'] = '5'

        with open('objects.json', 'w', encoding='utf-8') as f:
            data = serialize(json_file)
            f.write(data)

    except json.decoder.JSONDecodeError:
        print("Impossible de lire ou de modifier le fichier JSON.")
        pass


def deserialize(json_file :str) -> dict:
    return json.loads(json_file)

def serialize(json_file :dict) -> str:
    return json.dumps(json_file, indent=4)

if __name__ == "__main__":
    main()