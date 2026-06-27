import os
import json
import logging
from google import genai
from google.genai.errors import APIError

# Setup basic logging to help trace 503s and other errors
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_audit_workflow(policy_text: str, extracted_permissions: list) -> dict:
    """
    Forces Gemini to analyze the policy against the extracted permissions 
    and return ONLY a strictly formatted JSON object.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    prompt = f"""
    You are an elite cybersecurity auditor. Your job is to cross-examine a privacy policy against the actual permissions requested by the app.
    
    APP PERMISSIONS REQUESTED:
    {extracted_permissions}
    
    PRIVACY POLICY TEXT:
    {policy_text[:15000]}
    
    Task: Return a JSON object with EXACTLY these keys:
    - "extracted_permissions": (list of strings) The permissions requested.
    - "contradictions": (list of dicts) Where each dict represents a finding. Each dict MUST have:
        - "permission" (str): The specific permission (e.g. 'Camera' or 'Location').
        - "type" (str): Must be 'Critical Discrepancy', 'Omission', or 'Ambiguity'.
        - "quote" (str): The exact text from the policy. CRITICAL: If the type is 'Omission', set this value exactly to 'Not mentioned in policy'.
        - "explanation" (str): Detailed explanation of the contradiction and privacy risk.
    - "overall_score": (int) 0 to 10.
    - "summary": (str) A professional 2-3 sentence summary.
    """
    
    try:
        # Changed model to gemini-2.5-flash (or 2.0-flash).
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'temperature': 0.2,
                # Force the model to return pure JSON, eliminating the need for .strip() and markdown removal
                'response_mime_type': 'application/json' 
            }
        )
        
        # Guardrail against empty or blocked responses (Fixes VSCode/Runtime errors)
        if not response or not response.text:
            logging.error("API returned an empty response. This may be due to safety filters blocking the content.")
            return {"error": "Empty or blocked response from API."}

        # Since we enforced response_mime_type='application/json', we can parse it directly
        return json.loads(response.text)

    except APIError as e:
        # This will catch 503 Service Unavailable and other HTTP errors
        logging.error(f"Google API Error encountered: {e}")
        return {"error": f"API Error: {str(e)}"}
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {e}\nRaw Response: {response.text}")
        return {"error": "Failed to decode JSON from model."}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {"error": str(e)}


def run_agent_chat(policy_text: str, permissions: list, chat_history: list, user_message: str) -> str:
    """
    Acts as the polite, formal concierge that helps users understand the audit.
    """
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    formatted_history = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in chat_history[-4:]])
    
    system_instruction = """You are "Permission to Defend", a highly sophisticated AI Cybersecurity and Privacy Auditor. Your primary objective is to verify, cross-examine, and analyze mobile application privacy policies against their physical Android Manifest permissions.

You must operate under a strict, professional, and supportive code of conduct:
1. PERSONALITY: Be exceptionally formal, polite, supportive, and informative. Your goal is to guide the user constructively, ensuring they feel secure and empowered in this workspace.
2. EXPERTISE: Speak with the absolute authority of a veteran cybersecurity engineer. When explaining Android permissions (such as ACCESS_FINE_LOCATION, READ_CONTACTS, or RECORD_AUDIO), describe their technical capabilities, potential risk profiles, and how they impact consumer privacy.
3. DOMAIN GUARDRAIL: You are restricted entirely to app security, device permissions, privacy regulations, and instructions on how to use this workspace. If a user asks questions outside these topics, you must politely but firmly refuse to answer. Frame your refusal in a formal manner: "While I am here to assist you, my operational protocols limit me strictly to cybersecurity auditing, app privacy verification, and workspace navigation support."
4. FORMATTING: You must output STRICTLY IN PLAIN TEXT. The chat interface does not support Markdown. Do not use asterisks for bolding or italics (e.g., no **bold** or *italics*). Do not use markdown headers, lists, or code blocks.
5. CONCISENESS: Keep your responses highly concise and brief. Limit your answers to 4-6 short sentences. Do not write long paragraphs, as the chat window is optimized for short bursts of text.
"""

    prompt = f"""
    APP CONTEXT:
    Requested Permissions: {permissions}
    Privacy Policy Excerpt: {policy_text[:5000]}
    
    RECENT CHAT HISTORY:
    {formatted_history}
    
    USER'S LATEST MESSAGE:
    {user_message}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'system_instruction': system_instruction,
                'temperature': 0.7
            }
        )
        
        # Guardrail against missing text
        if not response or not response.text:
            return "I apologize, but my response was intercepted by a safety filter or the connection was lost. Could you please rephrase your question?"
            
        return response.text
        
    except APIError as e:
        logging.error(f"Chat API Error: {e}")
        return "I apologize, but my communication servers are currently experiencing difficulties (Error 503). Please try asking your question again in a moment."
    except Exception as e:
        logging.error(f"Unexpected chat error: {e}")
        return "I apologize, an unexpected system error occurred."