import requests

r = requests.post(
    "http://localhost:11434/api/embed",
    json={
        "model": "bge-m3",
        "input": ["What is HTML?"]
    }
)

print(r.status_code)
print(r.json())