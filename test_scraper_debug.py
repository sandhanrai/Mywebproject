from app.scraper import scrape_disease_info

# Test with Impetigo
test_diseases = ['Impetigo']

for disease in test_diseases:
    print(f"\nTesting {disease}:")
    info = scrape_disease_info(disease)
    print(f"Summary: {info['summary'][:200]}...")
    print(f"Causes: {len(info['causes'])} items")
    for i, cause in enumerate(info['causes'][:3]):
        print(f"  Cause {i+1}: {cause[:100]}...")
    print(f"Symptoms: {len(info['symptoms'])} items")
    for i, symptom in enumerate(info['symptoms'][:3]):
        print(f"  Symptom {i+1}: {symptom[:100]}...")
    print(f"Diagnosis: {len(info['diagnosis'])} items")
    for i, diag in enumerate(info['diagnosis'][:3]):
        print(f"  Diagnosis {i+1}: {diag[:100]}...")
    print(f"Prevention: {len(info['prevention'])} items")
    for i, prev in enumerate(info['prevention'][:3]):
        print(f"  Prevention {i+1}: {prev[:100]}...")
    print(f"Related: {len(info['related'])} items")
    for i, rel in enumerate(info['related'][:3]):
        print(f"  Related {i+1}: {rel[:100]}...")
    print(f"Treatments: {len(info['treatments'])} items")
    for i, treat in enumerate(info['treatments'][:3]):
        print(f"  Treatment {i+1}: {treat[:100]}...")
    print(f"Source: {info['source']}")
