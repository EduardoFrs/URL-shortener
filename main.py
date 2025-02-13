from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import validators, secrets

app = FastAPI()

# stockage pour les urls raccourcis et le compteur de clic
urls = {}
clicks = {}

# modèle pour verifier avec pydantic les url rentrés
class URLBase(BaseModel):
    target_url: str

class URLShort(URLBase):
    short_url: str
    clicks: int

@app.get("/")
def read_root():
    return {"Hello, you are on URL Shortener API"}

# route pour raccourcir l'URL
@app.post("/shorten", response_model=URLShort)
def shorten_url(url: URLBase):
    if not validators.url(url.target_url):
        raise HTTPException(status_code=400, detail="Provided URL is not valid")

    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmonpqrstuvwxyz0123456789"
    short_key = "".join(secrets.choice(chars) for _ in range(6))
    urls[short_key] = url.target_url
    clicks[short_key] = 0

    return URLShort(target_url=url.target_url, short_url=f"http://127.0.0.1:8000/{short_key}", clicks=0)

# route pour rediriger vers l'URL de base via le raccourci
@app.get("/{short_key}")
def redirect_url(short_key: str, response: Response):
    long_url = urls.get(short_key)
    clicks[short_key] += 1

    if not long_url:
        raise HTTPException(status_code=404, detail="URL not found")
    response.status_code = 307
    response.headers["Location"] = long_url
    return response

# route pour le compteru de clic
@app.get("/{short_key}/stats")
def url_stats(short_key: str):
    if short_key not in clicks:
        raise HTTPException(status_code=404, detail="URL not found")

    return {"short_url": f"http://127.0.0.1:8000/{short_key}", "clicks": clicks[short_key]}
