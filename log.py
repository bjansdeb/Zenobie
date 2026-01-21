import logging

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("zenobie.log", mode="w", encoding="utf-8")
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.setLevel("DEBUG")
formatter = logging.Formatter("{name} - {asctime} - {levelname} : {message}", style="{", datefmt="%Y-%m-%d %H:%M")
console_handler.setFormatter(formatter)

def log_it(type, text):
    match type:
        case "debug":
            return logger.debug(text)
        case "info":
            return logger.info(text)
        case "warning":
            return logger.warning(text)
        case "error":
            return logger.warning(text)       
