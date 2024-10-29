class Config:
    APP_NAME="SongCoMark Project"

class LiveConfig(Config):
    DBNAME ="scmlive"
    DBPWD = "live12345"

class TestConfig(Config):
    DBNAME = "scmtest"
    DBPWD = "test12345"