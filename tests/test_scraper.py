import unittest
from app.scraper import scrape_disease_info

class TestScraper(unittest.TestCase):
    def test_gastroenteritis(self):
        disease = "Gastroenteritis"
        info = scrape_disease_info(disease)
        self.assertIsNotNone(info)
        self.assertIn("summary", info)
        self.assertTrue(len(info["summary"]) > 0)
        self.assertIn("treatments", info)
        self.assertTrue(len(info["treatments"]) > 0)

    def test_flu(self):
        disease = "Flu"
        info = scrape_disease_info(disease)
        self.assertIsNotNone(info)
        self.assertIn("summary", info)
        self.assertTrue(len(info["summary"]) > 0)
        self.assertIn("treatments", info)
        self.assertTrue(len(info["treatments"]) > 0)

    def test_nonexistent_disease(self):
        disease = "NonexistentDiseaseXYZ"
        info = scrape_disease_info(disease)
        self.assertIsNotNone(info)
        self.assertIn("summary", info)
        self.assertTrue("not available" in info["summary"].lower())

if __name__ == "__main__":
    unittest.main()
