import tempfile

# DATABASE SETTINGS

DATABASE_PATH: str = "./src/database/"
DATABASE_NAME: str = "database.db"

# CLIENT_SETTINGS

STYLE_DIR: str = "/src/client/style/"
CLIENT_DIR: str = "/src/client/"
CONFIG_FILE: str = tempfile.gettempdir() + '/' + "config.json"
TEMPFILE_PREFIX: str = 'FREQUENCYTEMPFILE_'
HITMO_URL: str = 'https://rus.hitmotop.com'
