
import os
import json
import traceback
# from google import genai

# Dictionary for mapping Vietnamese disease names to English
# Based on the classes from the AI model
DISEASE_MAPPING = {
    "Mụn trứng cá": "Acne",
    "Bệnh vẩy nến": "Psoriasis",
    "Bệnh chàm": "Eczema",
    "Hắc lào": "Ringworm",
    "Lang ben": "Tinea versicolor",
    "Mụn cóc": "Warts",
    "Ung thư da": "Skin cancer",
    "Bớt": "Nevus",
    "Viêm da cơ địa": "Atopic dermatitis",
    "Thủy đậu": "Chickenpox",
    "Zona": "Shingles",
    "Da bình thường": "Normal skin",
    "Dị ứng": "Allergy",
    "Ghẻ": "Scabies",
    "Mề đay": "Urticaria",
    "Viêm nang lông": "Folliculitis",
    "Nấm móng": "Onychomycosis", # Adding potential others just in case
    "Nấm da đầu": "Tinea capitis"
}

def translate_result_json(result_list):
    """
    Translates the 'class' field in the result JSON list from Vietnamese to English.
    Args:
        result_list (list): List of dicts, e.g., [{'class': 'Mụn cóc', 'probability': 0.8}]
    Returns:
        list: Translated list, e.g., [{'class': 'Warts', 'probability': 0.8}]
    """
    if not result_list:
        return []
    
    translated_list = []
    for item in result_list:
        new_item = item.copy()
        vi_name = item.get('class')
        if vi_name:
            # Cleanup potential whitespace
            vi_name = vi_name.strip()
            # Try direct match or simple normalization
            en_name = DISEASE_MAPPING.get(vi_name, vi_name) # Fallback to original if not found
            new_item['class'] = en_name
        translated_list.append(new_item)
    return translated_list

def translate_text_gemini(text, user=None):
    """
    Translates Vietnamese text to English using Gemini API.
    Args:
        text (str): Vietnamese text.
        user: Django user object (optional, for logging context).
    Returns:
        str: English translation.
    """
    if not text:
        return ""

    try:
        from Dermal.views import call_gemini
        # Reuse the existing call_gemini function which handles API keys and fallback
        # We construct a specific prompt for translation
        prompt = f"Translate the following medical/patient text from Vietnamese to English. Keep it concise and professional: '{text}'"
        
        reply = call_gemini(prompt, user=user)
        
        # Cleanup: sometimes models chatter "Here is the translation: ...". 
        # For a simple implementation, we assume the model obeys 'concise'.
        # Or we can refine the prompt to "Output ONLY the English translation."
        
        # Let's try a stricter prompt call if possible, but call_gemini is generic.
        # We'll use the generic one for now.
        return reply
    except Exception as e:
        print(f"Translation error: {e}")
        traceback.print_exc()
        return text # Fallback to original
