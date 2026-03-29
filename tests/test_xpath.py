# save this as test_xpath.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.menzili.tn/immo/vente-immobilier-tunisie")
time.sleep(5)

print("="*60)
print("🔍 ANALYSE DE LA PAGE MENZILI")
print("="*60)

# 1. Afficher le titre
print(f"\n📌 Titre: {driver.title}")

# 2. Compter tous les éléments avec des classes communes
for class_name in ['product', 'item', 'annonce', 'card']:
    elements = driver.find_elements(By.CSS_SELECTOR, f"[class*='{class_name}']")
    print(f"Éléments avec '{class_name}': {len(elements)}")

# 3. Chercher spécifiquement les annonces
selectors_a_tester = [
    "//div[contains(@class, 'product-grid')]//div",
    "//div[contains(@class, 'col-md-4')]",
    "//div[@class='item']",
    "//article",
    "//div[contains(@class, 'product')]",
    "//div[contains(@class, 'annonce')]",
]

for xpath in selectors_a_tester:
    elements = driver.find_elements(By.XPATH, xpath)
    print(f"XPath '{xpath}': {len(elements)} éléments")

# 4. Sauvegarder le HTML pour analyse
with open("menzili_page.html", "w", encoding="utf-8") as f:
    f.write(driver.page_source)
print("\n✅ HTML sauvegardé dans menzili_page.html")

driver.quit()