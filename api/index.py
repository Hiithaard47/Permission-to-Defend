from fastapi import FastAPI, Request
from fastapi import HTTPException, status
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from google_play_scraper import permissions
from pydantic import BaseModel
from typing import List, Optional
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from api.agent import run_audit_workflow, run_agent_chat

# loading api key from .env file
load_dotenv()

# initializing FastAPI server
app = FastAPI()

# privacy policy and permissions ingestion request model
class IngestRequest(BaseModel):
    policy_text: str
    route_type: str
    play_store_url: Optional[str] = None
    manifest_xml: Optional[str] = None
    manual_permissions: Optional[List[str]] = None

# chat request model
class ChatRequest(BaseModel):
    policy_text: str
    permissions: List[str]
    chat_history: List[dict]
    user_message: str

# utility function to extract permissions from AndroidManifest.xml
def xml_extract(xml_string: str) -> List[str]:
    try:
        root = ET.fromstring(xml_string)
        permissions = []

        android_ns = "{http://schemas.android.com/apk/res/android}"

        for perm in root.findall('.//uses-permission'):
            name = perm.attrib.get(f"{android_ns}name")
            if name:
                permissions.append(name)
        return permissions
    except ET.ParseError:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Invalid XML format")

# utility function to extract permissions from a Play Store URL
def url_extract(url:str) -> List[str]:
    try:
        parsed_url = urlparse(url)
        app_id_list = parse_qs(parsed_url.query).get('id')
        if not app_id_list:
            raise ValueError("Could not find an app ID in the provided URL.")
        app_id = app_id_list[0]
        
        results = permissions(app_id, lang='en', country='us')
        
        extracted = []
        for category, perms in results.items():
            for p in perms:
                extracted.append(f"{category}: {p}")
                
        return extracted
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {str(e)}")

# for debugging purposes
@app.get("/api/health")
def health_check():
    return {"status": "API running locally."}

# for processing privacy policy and permissions ingestion
@app.post("/api/audit")
def process_audit(req: IngestRequest):
    # returning dummy data for now, will implement actual processing later
    print("Received privacy policy: ", req.policy_text[:50], "...")

    if req.route_type == "xml" and req.manifest_xml:
        extracted_perms = xml_extract(req.manifest_xml)
    elif req.route_type == "url" and req.play_store_url:
        extracted_perms = url_extract(req.play_store_url)
    elif req.route_type == "manual" and req.manual_permissions:
        extracted_perms = req.manual_permissions
    else:
        raise HTTPException(status_code = 400, detail = "Invalid route type or missing data")

    try:
        audit_results = run_audit_workflow(req.policy_text, extracted_perms)
        return audit_results
    except Exception as e:
        print(f"Audit Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# for processing chat requests
@app.post("/api/chat")
def process_chat(req: ChatRequest):
    print("SUCCESS! User says:", req.user_message)
    try:
        reply = run_agent_chat(
            policy_text=req.policy_text,
            permissions=req.permissions,
            chat_history=req.chat_history,
            user_message=req.user_message
        )
        return {"reply": reply}
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
