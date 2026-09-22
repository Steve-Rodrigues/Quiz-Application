from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    session_secret : str
    database_url : str
    #comma separated origins the browser may call us from. CORS with credentials can't
    #use a wildcard, so every deployed frontend has to be listed here explicitly
    allowed_origins : str = "http://localhost:5173"
    #a cross-site session cookie needs SameSite=None, and browsers only accept that
    #alongside Secure. both default off so local dev and the tests keep working on http
    cookie_samesite : str = "lax"
    cookie_secure : bool = False
    model_config = SettingsConfigDict(env_file='.env')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #hosts like Render hand out postgres:// or postgresql://, which SQLAlchemy reads as
        #psycopg2. we install psycopg3, so point the URL at that driver explicitly
        for prefix in ("postgresql://", "postgres://"):
            if self.database_url.startswith(prefix):
                self.database_url = "postgresql+psycopg://" + self.database_url[len(prefix):]
                break

    @property
    def origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

settings = Settings() #export this to the other files to access the needed env vars
