import hashlib  # built in lib used for hashing data
import hmac     # used for secure hashing with a secret key

import httpx
from fastapi import FastAPI, HTTPException, Request
from prometheus_fastapi_instrumentator import Instrumentator

from models import Settings

settings = Settings()
app = FastAPI()
'''
The below line will initialize prometheus extraction
'''
Instrumentator().instrument(app).expose(app)


# The health will route will check whether the service is alive or not
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/webhook/github")
async def github_webhook(request: Request):
    body = await request.body()   # Read the information coming from the PR request
    signature_header = request.headers.get("X-Hub-Signature-256", "")
    
    ''' The below part of the code will take the webhook secret key
    combines it with request body and it will generate a signature string
    use cryptography sha256'''
    
    expected = (
        "sha256="
        +hmac.new(
            settings.github_webhook_secret.encode(),
            body,
            hashlib.sha256,   
        ).hexdigest()
    )
    
    if not hmac.compare_digest(expected, signature_header):
        raise HTTPException(status_code = 401, detail= "Invalid signature")
    
    '''If the request is legit, then it will send the request to webhook service'''
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://webhook:8001/events",
            content=body,
            headers = {"Content-Type": "application/json"},
        )
        response.raise_for_status()

    return{"status":"ok"}