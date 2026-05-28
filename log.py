import logging
import time
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("zenobie_log.log", mode="w", encoding="utf-8")
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.setLevel("DEBUG")
formatter = logging.Formatter("{name} - {asctime} - {levelname} : {message}", style="{", datefmt="%Y-%m-%d %H:%M")
console_handler.setFormatter(formatter)

def log_it(type, text):
    """
    Docstring for log_it
    Function d'écriture de log et de prompt
    :param type: "debug", "info", "warning", "error" 
    :param text: (str)
    """

    match type:
        case "debug":
            time.sleep(1)
            return logger.debug(text)
        case "info":
            time.sleep(1)
            return logger.info(text)
        case "warning":
            time.sleep(2)
            return logger.warning(text)
        case "error":
            time.sleep(3)
            return logger.warning(text) 