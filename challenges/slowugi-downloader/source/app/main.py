from slowugi import SlowUGI
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles

app = Starlette()
app.mount("/ugi-bin", SlowUGI("ugi-bin"))
app.mount("/", StaticFiles(directory="static", html=True))
