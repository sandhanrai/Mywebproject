import json
import requests
from bs4 import BeautifulSoup

def find_section_content(soup, heading_patterns, content_selectors=None):
    """
    Find content for a section by trying multiple heading patterns.
    Returns the text content found after the heading.
    """
    if content_selectors is None:
        content_selectors = ['p', 'ul', 'ol']

    for pattern in heading_patterns:
        # Try h2, h3, h4 headings
        for heading_tag in ['h2', 'h3', 'h4']:
            heading = soup.find(heading_tag, string=lambda text: text and pattern in text.lower())
            if heading:
                # Get all content until next heading
                content_parts = []
                current = heading.find_next_sibling()

                while current and current.name not in ['h1', 'h2', 'h3', 'h4']:
                    if current.name in content_selectors:
                        if current.name in ['ul', 'ol']:
                            # Extract list items
                            items = current.find_all('li')
                            if items:
                                content_parts.extend([li.get_text(strip=True) for li in items if li.get_text(strip=True)])
                        else:
                            # Extract paragraph text
                            text = current.get_text(strip=True)
                            if text and len(text) > 20:  # Filter out very short texts
                                content_parts.append(text)
                    current = current.find_next_sibling()

                if content_parts:
                    return content_parts

    return []

def extract_list_items(soup, heading_patterns):
    """
    Extract list items from sections matching heading patterns.
    """
    for pattern in heading_patterns:
        for heading_tag in ['h2', 'h3', 'h4']:
            heading = soup.find(heading_tag, string=lambda text: text and pattern in text.lower())
            if heading:
                # Look for next ul or ol
                list_elem = heading.find_next(['ul', 'ol'])
                if list_elem:
                    items = list_elem.find_all('li')
                    return [li.get_text(strip=True) for li in items if li.get_text(strip=True)]
    return []

def scrape_disease_info(disease_name):
    # Load disease URLs from JSON
    with open('data/disease_urls.json', 'r') as f:
        disease_urls = json.load(f)

    # Get URL for the disease
    url = disease_urls.get(disease_name)
    if not url:
        # Return fallback mock data if disease not found in URLs
        return {
            "name": disease_name,
            "summary": f"Information about {disease_name} is not available at the moment. Please consult a healthcare professional.",
            "causes": ["Causes vary depending on the disease; common factors include genetic predisposition, environmental influences, infections, and lifestyle choices. Consult a healthcare professional for specific details."],
            "symptoms": ["Symptoms may include fatigue, pain, swelling, fever, or other indicators specific to the condition. Seek medical advice for accurate diagnosis."],
            "diagnosis": ["Diagnosis typically involves medical history review, physical exams, blood tests, imaging, or specialized tests. A doctor will determine the appropriate methods."],
            "prevention": ["Prevention strategies often include healthy lifestyle habits, vaccinations where applicable, avoiding risk factors, and regular check-ups. Specific measures depend on the disease."],
            "related": ["Related conditions may include other chronic illnesses or complications; refer to MedlinePlus for linked topics."],
            "treatments": ["Treatment options generally include medications, lifestyle modifications, physical therapy, or surgical interventions tailored to the individual. Always consult a physician for personalized treatment plans, as self-treatment can be harmful."],
            "source": ""
        }

    # Fetch the page with error handling
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        # Fallback mock data for fetch failures
        return {
            "name": disease_name,
            "summary": "No summary available from the source due to access issues. This disease involves various health impacts; please refer to a medical expert for detailed information.",
            "causes": ["Causes vary depending on the disease; common factors include genetic predisposition, environmental influences, infections, and lifestyle choices. Consult a healthcare professional for specific details."],
            "symptoms": ["Symptoms may include fatigue, pain, swelling, fever, or other indicators specific to the condition. Seek medical advice for accurate diagnosis."],
            "diagnosis": ["Diagnosis typically involves medical history review, physical exams, blood tests, imaging, or specialized tests. A doctor will determine the appropriate methods."],
            "prevention": ["Prevention strategies often include healthy lifestyle habits, vaccinations where applicable, avoiding risk factors, and regular check-ups. Specific measures depend on the disease."],
            "related": ["Related conditions may include other chronic illnesses or complications; refer to MedlinePlus for linked topics."],
            "treatments": ["Treatment options generally include medications, lifestyle modifications, physical therapy, or surgical interventions tailored to the individual. Always consult a physician for personalized treatment plans, as self-treatment can be harmful."],
            "source": url
        }

    # Parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove government funding notice if present
    notice = soup.find('div', class_='alert')
    if notice:
        notice.decompose()

    # Extract summary from the specific summary div
    summary_div = soup.find('div', id='topic-summary')
    summary = ""
    if summary_div:
        paragraphs = summary_div.find_all('p')
        summary_texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        summary = ' '.join(summary_texts)

    # If no summary found, try multiple patterns
    if not summary:
        summary_patterns = ['what is', 'summary', 'overview', 'definition']
        summary_content = find_section_content(soup, summary_patterns, ['p'])
        summary = ' '.join(summary_content[:2]) if summary_content else ""

    # If still no summary, try first meaningful paragraph
    if not summary:
        main_content = soup.find('div', class_='main') or soup.find('main') or soup
        first_p = main_content.find('p')
        if first_p:
            text = first_p.get_text().strip()
            if text and 'united states government' not in text.lower() and len(text) > 50:
                summary = text

    # Extract causes
    causes_patterns = ['what causes', 'causes', 'risk factors', 'etiology']
    causes = find_section_content(soup, causes_patterns)

    # Extract symptoms
    symptoms_patterns = ['what are the symptoms', 'symptoms', 'signs and symptoms', 'what to look for']
    symptoms = find_section_content(soup, symptoms_patterns)

    # Extract diagnosis
    diagnosis_patterns = ['how is it diagnosed', 'diagnosis', 'diagnosing', 'tests and diagnosis']
    diagnosis = find_section_content(soup, diagnosis_patterns)

    # Extract prevention
    prevention_patterns = ['how can it be prevented', 'prevention', 'preventing', 'can it be prevented']
    prevention = find_section_content(soup, prevention_patterns)

    # Extract treatments
    treatments_patterns = ['how is it treated', 'treatment', 'treatments and therapies', 'management', 'therapy']
    treatments = find_section_content(soup, treatments_patterns)

    # Extract related issues
    related_patterns = ['related issues', 'related conditions', 'complications', 'see also']
    related = extract_list_items(soup, related_patterns)

    # Apply fallbacks if sections not found
    if not summary:
        summary = "No summary available from the source. This disease involves various health impacts; please refer to a medical expert for detailed information."

    if not causes:
        causes = ["Causes vary depending on the disease; common factors include genetic predisposition, environmental influences, infections, and lifestyle choices. Consult a healthcare professional for specific details."]

    if not symptoms:
        symptoms = ["Symptoms may include fatigue, pain, swelling, fever, or other indicators specific to the condition. Seek medical advice for accurate diagnosis."]

    if not diagnosis:
        diagnosis = ["Diagnosis typically involves medical history review, physical exams, blood tests, imaging, or specialized tests. A doctor will determine the appropriate methods."]

    if not prevention:
        prevention = ["Prevention strategies often include healthy lifestyle habits, vaccinations where applicable, avoiding risk factors, and regular check-ups. Specific measures depend on the disease."]

    if not treatments:
        treatments = ["Treatment options generally include medications, lifestyle modifications, physical therapy, or surgical interventions tailored to the individual. Always consult a physician for personalized treatment plans, as self-treatment can be harmful."]

    if not related:
        related = ["Related conditions may include other chronic illnesses or complications; refer to MedlinePlus for linked topics."]

    # Return the dictionary
    return {
        "name": disease_name,
        "summary": summary,
        "causes": causes,
        "symptoms": symptoms,
        "diagnosis": diagnosis,
        "prevention": prevention,
        "related": related,
        "treatments": treatments,
        "source": url
    }
