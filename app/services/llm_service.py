import requests
import json
from app.models import models 

prompt = """ Act as a name checker, You will be give a name will be given you have to return the correct spelling and correction of that name"""

def get_gemini_response(api_key: str, text: str) -> dict:
    """
    Makes an API call to the Gemini 2.0 Flash model and returns the response and citations.
    
    Args:
        api_key: Your Gemini API key
        text: The input text/prompt to send to the model
        
    Returns:
        A dictionary with keys:
            - 'response': The text response from the model
            - 'citation': List of citation URIs from the response
            
        Returns None if the API call fails
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "contents": [{
            "parts": [{"text": text}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        
        # Extract the response text and citations
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            response_text = candidate["content"]["parts"][0]["text"]
            
            citations = []
            if "citationMetadata" in candidate and "citationSources" in candidate["citationMetadata"]:
                citations = [source["uri"] for source in candidate["citationMetadata"]["citationSources"]]
            
            return {
                "response": response_text,
                "citation": citations
            }
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing API response: {e}")
        return None

async def LLM_call(word: str):
    """
        Function will accept a name and return a list of corrected name. 
    """
    
    formatted_prompt = prompt + f"name: {word}"

    try: 
        result = get_gemini_response("AIzaSyDVaGGVPpV5QCPh4fuoK-ILZxbUuEMnCcc", formatted_prompt)
        if result:
            print("Response:", result["response"])
            print("Citations:", result["citation"])

        return result
    except Exception as e:
        print(f"Error parsing API response: {e}")
        return None