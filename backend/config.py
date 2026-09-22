import os

from pydantic_settings import BaseSettings, SettingsConfigDict

#render sets both of these on every service it runs, so they tell us we are deployed
#rather than sitting on someone's laptop
def on_a_host() -> bool:
    return bool(os.getenv("RENDER") or os.getenv("RENDER_EXTERNAL_URL"))

class Settings(BaseSettings):
    session_secret : str
    database_url : str
    #comma separated origins the browser may call us from. CORS with credentials can't
    #use a wildcard, so every frontend has to be named here. the deployed one is in the
    #default so a fresh deploy works without setting anything
    allowed_origins : str = (
        "http://localhost:5173,"
        "https://quiz-application-1-uvg7.onrender.com"
    )
    #a cross-site session cookie needs SameSite=None, and browsers only accept that
    #alongside Secure. left off locally and in tests, which run over plain http, and
    #turned on automatically once we detect we're deployed
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
        #anything set explicitly in the environment wins over the deployed defaults
        if on_a_host():
            if "cookie_samesite" not in self.model_fields_set:
                self.cookie_samesite = "none"
            if "cookie_secure" not in self.model_fields_set:
                self.cookie_secure = True

    @property
    def origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

settings = Settings() #export this to the other files to access the needed env vars
