import json
import requests
from bs4 import BeautifulSoup

def scrape_disease_info(disease_name):
    print(f"DEBUG: scrape_disease_info called with disease_name: {disease_name}")

    disease_urls = {
        "Fungal infection": "https://medlineplus.gov/fungalinfections.html",
        "Allergy": "https://medlineplus.gov/allergy.html",
        "GERD": "https://medlineplus.gov/gerd.html",
        "Chronic cholestasis": "https://medlineplus.gov/ency/article/000215.htm",
        "Drug Reaction": "https://medlineplus.gov/drugreactions.html",
        "Peptic ulcer disease": "https://medlineplus.gov/pepticulcer.html",
        "AIDS": "https://medlineplus.gov/hiv.html",
        "Diabetes": "https://medlineplus.gov/diabetes.html",
        "Gastroenteritis": "https://medlineplus.gov/gastroenteritis.html",
        "Bronchial Asthma": "https://medlineplus.gov/asthma.html",
        "Hypertension": "https://medlineplus.gov/highbloodpressure.html",
        "Migraine": "https://medlineplus.gov/migraine.html",
        "Cervical spondylosis": "https://medlineplus.gov/ency/article/000423.htm",
        "Paralysis (brain hemorrhage)": "https://medlineplus.gov/ency/article/000712.htm",
        "Jaundice": "https://medlineplus.gov/jaundice.html",
        "Malaria": "https://medlineplus.gov/malaria.html",
        "Chicken pox": "https://medlineplus.gov/chickenpox.html",
        "Dengue": "https://medlineplus.gov/dengue.html",
        "Typhoid": "https://medlineplus.gov/typhoid.html",
        "Hepatitis A": "https://medlineplus.gov/hepatitisa.html",
        "Hepatitis B": "https://medlineplus.gov/hepatitisb.html",
        "Hepatitis C": "https://medlineplus.gov/hepatitisc.html",
        "Alcoholic hepatitis": "https://medlineplus.gov/hepatitis.html",
        "Tuberculosis": "https://medlineplus.gov/tuberculosis.html",
        "Common Cold": "https://medlineplus.gov/commoncold.html",
        "Pneumonia": "https://medlineplus.gov/pneumonia.html",
        "Dimorphic hemorrhoids (piles)": "https://medlineplus.gov/ency/article/000261.htm",
        "Heart attack": "https://medlineplus.gov/heartattack.html",
        "Varicose veins": "https://medlineplus.gov/varicoseveins.html",
        "Hypothyroidism": "https://medlineplus.gov/hypothyroidism.html",
        "Hyperthyroidism": "https://medlineplus.gov/hyperthyroidism.html",
        "Hypoglycemia": "https://medlineplus.gov/hypoglycemia.html",
        "Osteoarthritis": "https://medlineplus.gov/osteoarthritis.html",
        "Arthritis": "https://medlineplus.gov/arthritis.html",
        "Vertigo (Benign Paroxysmal Positional Vertigo)": "https://medlineplus.gov/dizzinessandvertigo.html",
        "Acne": "https://medlineplus.gov/acne.html",
        "Urinary tract infection": "https://medlineplus.gov/urinarytractinfections.html",
        "Psoriasis": "https://medlineplus.gov/psoriasis.html",
        "Impetigo": "https://medlineplus.gov/impetigo.html"
    }

    # Normalize disease name for lookup - keep original casing to match JSON keys
    disease_key = disease_name
    url = disease_urls.get(disease_key)
    print(f"DEBUG: disease_key = '{disease_key}', url = {url}")
    if not url:
        return fallback_disease_info(disease_name)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return fallback_disease_info(disease_name, url)

    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"DEBUG: soup created, title: {soup.title.get_text() if soup.title else 'No title'}")

    # Helper to extract text from a section identified by heading text
    def extract_section_text(heading_texts):
        print(f"DEBUG: extract_section_text called with heading_texts: {heading_texts}")
        print(f"DEBUG: soup type: {type(soup)}")
        for heading_text in heading_texts:
            print(f"Looking for heading containing: '{heading_text}'")
            def heading_matcher(tag):
                if tag.name not in ['h2', 'h3', 'h4']:
                    return False
                tag_text = tag.get_text(strip=True).lower()
                search_words = heading_text.lower().split()
                return any(word in tag_text for word in search_words)
            heading = soup.find(heading_matcher)
            if heading:
                print(f"Found heading: {heading.get_text(strip=True)}")
                content = []
                # Special case for summary: look for div#topic-summary
                if 'summary' in heading_text.lower():
                    summary_div = heading.find_next('div', id='topic-summary')
                    if summary_div:
                        paragraphs = summary_div.find_all('p')
                        content = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                        if content:
                            print(f"Extracted summary content: {content[:2]}...")
                            return ' '.join(content)
                # Otherwise, collect paragraphs and list items until next heading
                sibling = heading.find_next_sibling()
                while sibling and sibling.name not in ['h1', 'h2', 'h3', 'h4']:
                    if sibling.name == 'p':
                        text = sibling.get_text(strip=True)
                        if text:
                            content.append(text)
                    elif sibling.name in ['ul', 'ol']:
                        items = sibling.find_all('li')
                        for item in items:
                            item_text = item.get_text(strip=True)
                            if item_text:
                                content.append(item_text)
                    sibling = sibling.find_next_sibling()
                if content:
                    print(f"Extracted content for {heading_text}: {content[:2]}...")
                    return ' '.join(content) if 'summary' in heading_text.lower() else content
        print("No matching heading found for any of the given heading texts.")
        return None

    try:
        summary = extract_section_text(['Summary', 'What is', 'Overview', 'Definition']) or fallback_disease_info(disease_name)['summary']
    except Exception as e:
        print(f"DEBUG: Exception in extract_section_text for summary: {e}")
        summary = fallback_disease_info(disease_name)['summary']
    causes = extract_section_text(['Causes', 'What causes', 'Risk factors', 'Etiology']) or fallback_disease_info(disease_name)['causes']
    symptoms = extract_section_text(['Symptoms', 'What are the symptoms', 'Signs and symptoms']) or fallback_disease_info(disease_name)['symptoms']
    diagnosis = extract_section_text(['Diagnosis', 'How is it diagnosed', 'Tests and diagnosis']) or fallback_disease_info(disease_name)['diagnosis']
    prevention = extract_section_text(['Prevention', 'How can it be prevented', 'Preventing']) or fallback_disease_info(disease_name)['prevention']
    treatments = extract_section_text(['Treatment', 'Treatments and therapies', 'Management', 'Therapy']) or fallback_disease_info(disease_name)['treatments']
    related = extract_section_text(['Related issues', 'Related conditions', 'Complications', 'See also']) or fallback_disease_info(disease_name)['related']

    return {
        'name': disease_name,
        'summary': summary,
        'causes': causes if isinstance(causes, list) else [causes],
        'symptoms': symptoms if isinstance(symptoms, list) else [symptoms],
        'diagnosis': diagnosis if isinstance(diagnosis, list) else [diagnosis],
        'prevention': prevention if isinstance(prevention, list) else [prevention],
        'related': related if isinstance(related, list) else [related],
        'treatments': treatments if isinstance(treatments, list) else [treatments],
        'source': url
    }

def fallback_disease_info(disease_name, url=''):
    return {
        'name': disease_name,
        'summary': f'Information about {disease_name} is not available at the moment. Please consult a healthcare professional.',
        'causes': ['Causes vary depending on the disease; common factors include genetic predisposition, environmental influences, infections, and lifestyle choices. Consult a healthcare professional for specific details.'],
        'symptoms': ['Symptoms may include fatigue, pain, swelling, fever, or other indicators specific to the condition. Seek medical advice for accurate diagnosis.'],
        'diagnosis': ['Diagnosis typically involves medical history review, physical exams, blood tests, imaging, or specialized tests. A doctor will determine the appropriate methods.'],
        'prevention': ['Prevention strategies often include healthy lifestyle habits, vaccinations where applicable, avoiding risk factors, and regular check-ups. Specific measures depend on the disease.'],
        'related': ['Related conditions may include other chronic illnesses or complications; refer to MedlinePlus for linked topics.'],
        'treatments': ['Treatment options generally include medications, lifestyle modifications, physical therapy, or surgical interventions tailored to the individual. Always consult a physician for personalized treatment plans, as self-treatment can be harmful.'],
        'source': url
    }
