import re

def clean_text(raw_text: str) -> str:
    text = re.sub(r'\n+', '\n', raw_text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def classify_text(text: str) -> dict:
    result = {
        "is_phone": False,
        "is_url": False
    }
    phone_pattern = r'1[3-9]\d{9}'
    if re.search(phone_pattern, text):
        result["is_phone"] = True
    url_pattern = r'https?://[^\s]+'
    if re.search(url_pattern, text):
        result["is_url"] = True
    return result

def is_content_duplicate(text, record_list):
    for item in record_list:
        if item[2] == text:
            return True
    return False