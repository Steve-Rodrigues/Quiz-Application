from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    session_secret : str
    database_url : str
    model_config = SettingsConfigDict(env_file='.env')
settings = Settings() #export this to the other files to access the needed env vars