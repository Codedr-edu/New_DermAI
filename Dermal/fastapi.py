import requests

url = "https://codedr-skin-detection.hf.space/predict_with_gradcam"


def fast_api(image_b64):
    payload = {
        "data": image_b64
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("Request successful")
        print("Response:", response.json())
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
