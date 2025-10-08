import json
from app.scraper import scrape_disease_info

# Load disease URLs
with open('data/disease_urls.json', 'r') as f:
    disease_urls = json.load(f)

diseases = list(disease_urls.keys())

print(f"Testing {len(diseases)} diseases...")

for disease in diseases:
    result = scrape_disease_info(disease)
    if result:
        has_details = bool(result.get('summary') or result.get('causes') or result.get('symptoms') or result.get('diagnosis') or result.get('prevention') or result.get('related'))
        has_treatments = bool(result.get('treatments'))
        status = "OK" if has_details and has_treatments else "Partial" if has_details or has_treatments else "No Data"
        print(f"{disease}: {status} (Details: {has_details}, Treatments: {has_treatments})")
    else:
        print(f"{disease}: Failed to scrape")

print("Testing complete.")
