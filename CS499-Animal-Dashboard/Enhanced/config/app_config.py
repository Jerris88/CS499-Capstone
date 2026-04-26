# basic config values used across the app
class AppConfig:

    # database connection settings
    USERNAME = ""
    PASSWORD = ""
    HOST = "localhost"
    PORT = 27017

    # main database + collections
    DB_NAME = "AAC"
    ANIMAL_COLLECTION = "animals"
    ADMIN_COLLECTION = "admin_users"

    # app display settings
    APP_TITLE = "Grazioso Salvare Dashboard"