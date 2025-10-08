from app.scraper import scrape_disease_info

result = scrape_disease_info('Fungal infection')
print('Summary:', result['summary'][:500] if result['summary'] else 'No summary found')
