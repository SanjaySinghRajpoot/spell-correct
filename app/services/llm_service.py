import re
from typing import Dict, List, Optional, Union
import requests
import json
from app.models import models 

prompt = """You are a name spelling checker and corrector. Your task is to analyze input names and provide corrected spellings with confidence scores.

Instructions:
1. You will receive a name that may contain spelling errors or variations
2. Identify the most likely correct spelling(s) of the name, considering the cultural context of the specified country
3. Calculate a similarity score (0.0 to 1.0) indicating how confident you are in each correction
4. Return your response in the exact JSON format specified below

Response Format:
Always wrap your JSON response in <json> and </json> tags. The JSON must follow this exact structure:

[
  {{
    "name": "corrected_name_1",
    "similarity_score": 0.95
  }},
  {{
    "name": "corrected_name_2", 
    "similarity_score": 0.87
  }}
]

Guidelines:
- Provide 1-3 most likely corrections, ranked by similarity score
- Similarity scores should range from 0.0 (no match) to 1.0 (perfect match)
- Consider common misspellings, phonetic variations, and cultural name variants specific to the given country
- Take into account naming conventions and common names from the specified country/culture
- If the input name appears correct, return it with a high similarity score
- Maintain strict JSON formatting - no additional text outside the tags

Example:
Input: "Jhon Smyth" (Country: United States)
<json>
[
  {{
    "name": "John Smith",
    "similarity_score": 0.92
  }},
  {{
    "name": "John Smyth", 
    "similarity_score": 0.88
  }}
]
</json>

Now analyze the following:
Name: {name}
Country: {country}"""

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
    
def extract_json_from_response(llm_response: str) -> Optional[List[Dict[str, Union[str, float]]]]:
    """
    Extract JSON data from LLM response that contains JSON wrapped in <json> tags.
    
    Args:
        llm_response (str): The raw response from the LLM
        
    Returns:
        Optional[List[Dict]]: Parsed JSON data or None if extraction fails
    """
    try:
        # Method 1: Extract JSON between <json> and </json> tags
        json_pattern = r'<json>\s*(.*?)\s*</json>'
        match = re.search(json_pattern, llm_response, re.DOTALL | re.IGNORECASE)
        
        if match:
            json_str = match.group(1).strip()
            # Parse the JSON string
            parsed_json = json.loads(json_str)
            return parsed_json
        
        # Method 2: Fallback - try to find JSON array pattern directly
        array_pattern = r'\[\s*\{.*?\}\s*\]'
        match = re.search(array_pattern, llm_response, re.DOTALL)
        
        if match:
            json_str = match.group(0).strip()
            parsed_json = json.loads(json_str)
            return parsed_json
            
        # Method 3: Last resort - try to find any valid JSON in the response
        # Look for content that starts with [ and ends with ]
        start_idx = llm_response.find('[')
        end_idx = llm_response.rfind(']')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = llm_response[start_idx:end_idx+1]
            parsed_json = json.loads(json_str)
            return parsed_json
            
        return None
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during JSON extraction: {e}")
        return None

def validate_name_correction_json(data: List[Dict]) -> bool:
    """
    Validate that the extracted JSON matches the expected structure for name corrections.
    
    Args:
        data (List[Dict]): The parsed JSON data
        
    Returns:
        bool: True if valid structure, False otherwise
    """
    if not isinstance(data, list):
        return False
    
    for item in data:
        if not isinstance(item, dict):
            return False
        if 'name' not in item or 'similarity_score' not in item:
            return False
        if not isinstance(item['name'], str):
            return False
        if not isinstance(item['similarity_score'], (int, float)):
            return False
        if not (0.0 <= item['similarity_score'] <= 1.0):
            return False
    
    return True

def safe_extract_json_from_response(llm_response: str) -> Optional[List[Dict[str, Union[str, float]]]]:
    """
    Safely extract and validate JSON from LLM response.
    
    Args:
        llm_response (str): The raw response from the LLM
        
    Returns:
        Optional[List[Dict]]: Validated JSON data or None if extraction/validation fails
    """
    extracted_json = extract_json_from_response(llm_response)
    
    if extracted_json is None:
        print("Failed to extract JSON from response")
        return None
    
    if not validate_name_correction_json(extracted_json):
        print("Extracted JSON does not match expected structure")
        return None
    
    return extracted_json

async def LLM_call(word: str, country: str):
    """
        Function will accept a name and return a list of corrected name. 
    """

    try: 

        formatted_prompt = prompt.format(name=word, country=country)


        result = get_gemini_response("AIzaSyDVaGGVPpV5QCPh4fuoK-ILZxbUuEMnCcc", formatted_prompt)
        if result:
            print("Response:", result["response"])
            print("Citations:", result["citation"])

            extracted_json = safe_extract_json_from_response(result["response"])
            
            if extracted_json:
                print("Extracted JSON:", extracted_json)
                return extracted_json
            else:
                print("Failed to extract valid JSON from response")
                return None
        else:
            print("No valid response received from API")
            return None

    except Exception as e:
        print(f"Error parsing API response: {e}")
        return None
    
async def LLM_process(word: str, country: str) -> str:
    try: 
        res = await LLM_call(word, country)
        if res:
            return res
        
        return "something went wrong while processing LLM process."
           
    except Exception as e:
        return f"Error: {e}"