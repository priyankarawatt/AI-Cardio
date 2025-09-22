import requests

url = "http://127.0.0.1:5000/predict"

data = {
    "age": 50,
    "gender": 1,
    "height": 160,
    "weight": 70,
    "ap_hi": 120,
    "ap_lo": 80,
    "cholesterol": 1,
    "gluc": 1,
    "smoke": 0,
    "alco": 0,
    "active": 1
}

response = requests.post(url, json=data)
print(response.json())
