from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import requests
import re
import json

def get_soup(url: str, ts = 2) -> BeautifulSoup:
    """
    Get soup from URL using Selenium (handles JavaScript rendering).
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    time.sleep(ts)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    
    return soup

def get_clubs_list(url: str) -> list:
    """
    Get the soup and collect the urls of every club pages
    """
    soup = get_soup(url)
    #print(soup.prettify())
    links = []
    for div in soup.find_all('div', class_='footer-clubs__logo-container'):
        #print(f"This is a div : {div}")
        links.extend ([a['href'] for a in div.find_all('a', href=True)])
    return links

def get_players_pictureees(url: list) -> list:
    """
    Get the soup and collect the urls of every player picture
    """
    soup = get_soup(url)
    print(soup.prettify())
    players = {}
    for img in soup.find_all('img', class_='player-block__player-img'):
        print("HERE")
        #players[img['alt']] = img['src']
        players[img.get('alt', 'Unknown')] = img.get('src')

    return players

def get_players_pictures(club_url: str) -> dict:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time

    """
    Ouvre la page du club, clique sur 'Effectif & Staff', 
    puis scrape les images des joueurs sans être redirigé.
    """

    # 1️⃣ Configuration du WebDriver
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Évite détection bot
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    try:
        # 2️⃣ Accéder à la page principale du club
        print(f"🔎 Accès à la page du club : {club_url}")
        driver.get(club_url)

        # 3️⃣ Attendre que la page se charge
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # 4️⃣ Chercher et cliquer sur "Effectif & Staff"
        try:
            print("🔍 Recherche du lien 'Effectif & Staff'...")
            staff_link = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Effectif"))
            )
            driver.execute_script("arguments[0].click();", staff_link)
            print("✅ Lien 'Effectif & Staff' cliqué avec succès !")

        except:
            print("❌ Impossible de trouver ou cliquer sur 'Effectif & Staff'.")
            return {}

        # 5️⃣ Attendre le chargement de la page des joueurs
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "player-block__player-img"))
            )
            print("✅ Page 'Effectif & Staff' chargée avec succès !")
        except:
            print("❌ La page 'Effectif & Staff' ne s'est pas chargée correctement.")
            return {}

        # 6️⃣ Scroll pour charger toutes les images (Lazy Loading)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # 7️⃣ Scraper les images des joueurs
        images = driver.find_elements(By.CLASS_NAME, "player-block__player-img")
        print(f"🔍 {len(images)} images trouvées.")  # Debugging

        players = {}
        for img in images:
            alt = img.get_attribute('alt')
            src = img.get_attribute('src')
            if alt and src:
                players[alt] = src

        return players

    finally:
        driver.quit()  # Toujours fermer proprement le WebDriver

url = "https://www.lnr.fr/page/carrieres"

#clubs = get_clubs_list(url)
clubs = ['https://www.lnr.fr/club/clermont', 'https://www.lnr.fr/club/bayonne', 'https://www.lnr.fr/club/castres', 'https://www.lnr.fr/club/lyon', 'https://www.lnr.fr/club/montpellier', 'https://www.lnr.fr/club/toulon', 'https://www.lnr.fr/club/vannes', 'https://www.lnr.fr/club/racing-92', 'https://www.lnr.fr/club/pau', 'https://www.lnr.fr/club/paris', 'https://www.lnr.fr/club/la-rochelle', 'https://www.lnr.fr/club/toulouse', 'https://www.lnr.fr/club/perpignan', 'https://www.lnr.fr/club/bordeaux-begles', 'https://www.lnr.fr/club/beziers', 'https://www.lnr.fr/club/biarritz', 'https://www.lnr.fr/club/brive', 'https://www.lnr.fr/club/colomiers', 'https://www.lnr.fr/club/grenoble', 'https://www.lnr.fr/club/oyonnax', 'https://www.lnr.fr/club/provence-rugby', 'https://www.lnr.fr/club/agen', 'https://www.lnr.fr/club/angouleme', 'https://www.lnr.fr/club/aurillac', 'https://www.lnr.fr/club/mont-de-marsan', 'https://www.lnr.fr/club/nice', 'https://www.lnr.fr/club/dax', 'https://www.lnr.fr/club/montauban', 'https://www.lnr.fr/club/nevers', 'https://www.lnr.fr/club/valence-romans']
top14_clubs, prod2_clubs = clubs[:14], clubs[14:]

all_pictures = {}
for club in top14_clubs:
    nom = re.split(r'/', club)[-1]
    all_pictures[nom] = get_players_pictures(club)
    
with open('data/players_pictures2.json', 'w', encoding='utf-8') as f:
    json.dump(all_pictures, f, indent=4, ensure_ascii=False)