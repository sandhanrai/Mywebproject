import json
import requests

# Load disease URLs
with open('data/disease_urls.json', 'r') as f:
    disease_urls = json.load(f)

print("Checking URLs for all diseases...")
invalid_urls = []
for disease, url in disease_urls.items():
    try:
        response = requests.head(url, timeout=10)
        status = response.status_code
        if status == 200:
            print(f"{disease}: OK ({status})")
        else:
            print(f"{disease}: FAILED ({status}) - {url}")
            invalid_urls.append((disease, url))
    except requests.exceptions.RequestException as e:
        print(f"{disease}: ERROR - {url} ({str(e)})")
        invalid_urls.append((disease, url))

print(f"\nSummary: {len(disease_urls) - len(invalid_urls)} working URLs, {len(invalid_urls)} invalid.")
if invalid_urls:
    print("\nInvalid URLs:")
    for disease, url in invalid_urls:
        print(f"- {disease}: {url}")
