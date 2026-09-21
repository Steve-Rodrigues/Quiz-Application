from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    session_secret : str
    database_url : str
    model_config = SettingsConfigDict(env_file='.env')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #hosts like Render hand out postgres:// or postgresql://, which SQLAlchemy reads as
        #psycopg2. we install psycopg3, so point the URL at that driver explicitly
        for prefix in ("postgresql://", "postgres://"):
            if self.database_url.startswith(prefix):
                self.database_url = "postgresql+psycopg://" + self.database_url[len(prefix):]
                break

settings = Settings() #export this to the other files to access the needed env vars
