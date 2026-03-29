# test_afariat.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://afariat.com/recherche?q=vente&category=Immobilier")
time.sleep(5)

print("="*60)
print("🔍 ANALYSE DE LA PAGE AFARIAT")
print("="*60)

# 1. Compter les éléments avec différentes classes
for class_name in ['card', 'item', 'annonce', 'ad', 'listing']:
    elements = driver.find_elements(By.CSS_SELECTOR, f"[class*='{class_name}']")
    print(f"Éléments avec '{class_name}': {len(elements)}")

# 2. Chercher les titres h2 (comme dans votre code)
h2_elements = driver.find_elements(By.TAG_NAME, "h2")
print(f"\nBalises h2: {len(h2_elements)}")
for i, h2 in enumerate(h2_elements[:5]):
    print(f"  h2 {i+1}: {h2.text[:50]}...")

# 3. Chercher les conteneurs d'annonces probables
conteneurs = [
    "//div[contains(@class, 'col-12')]",
    "//div[contains(@class, 'card')]",
    "//div[contains(@class, 'product')]",
    "//article",
    "//li[contains(@class, 'ad')]",
]

for xpath in conteneurs:
    elements = driver.find_elements(By.XPATH, xpath)
    print(f"XPath '{xpath}': {len(elements)} éléments")

# 4. Sauvegarder le HTML pour analyse
with open("afariat_page.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)
print("\n✅ HTML sauvegardé dans afariat_page.html")

driver.quit()