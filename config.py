import configparser
def read_config():
    config = configparser.ConfigParser()
    config.read('settings/config.ini')
    max_files = config.get('Dezipper', 'max_files')
    max_total_size = config.get('Dezipper', 'max_total_size')
    mimes_niv_1 = config.get('Dezipper', 'mimes_niv_1')
    authorized_packs = config.get('Dezipper', 'authorized_packs')
    unauthorized_packs = config.get('Dezipper', 'unauthorized_packs')
    forbidden_chars = config.get('Renamer', 'forbidden_chars')

    config_values = {
        'max_files' : max_files,
        'max_total_size' : max_total_size,
        'authorized_packs': authorized_packs,
        'unauthorized_packs': unauthorized_packs,
        'forbidden_chars': forbidden_chars,
        'mimes_niv_1' : mimes_niv_1
    }

    return config_values
