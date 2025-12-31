import requests
import time

# 1. Send the News Article
url = "http://127.0.0.1:8000/verify"
payload = {
    "text": "Kashmir is an integral part of india"
}

print("Sending request...")
response = requests.post(url, json=payload)
job_data = response.json()
job_id = job_data['job_id']
print(f"Job ID: {job_id}")

# 2. Poll for Results
print("Waiting for agents...")
while True:
    status_res = requests.get(f"http://127.0.0.1:8000/status/{job_id}")
    status_data = status_res.json()
    
    if status_data['status'] == 'COMPLETED':
        print("\n--- FINAL REPORT ---")
        print(status_data['result'])
        break
    
    print("Processing...", end="\r")
    time.sleep(2)