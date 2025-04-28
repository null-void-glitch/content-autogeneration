#Importing all needed modules
import os
import time
import openai
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#loading key features
logging.basicConfig(level=logging.INFO)
load_dotenv(dotenv_path="gpt_automate.env")
openai.api_key = os.getenv('OPENAI_KEY')

# Backend Credentials
username = os.getenv('LOGIN_UN')
password = os.getenv('LOGIN_PW')

#Helper for WebdriverWait
def wait_and_click(driver, by, selector, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        element.click()
        return True
    except Exception as e:
        logging.error(f"Klicken fehlgeschlagen: {selector} – {e}")
        return False

# Regions
region_mapping = {
    "aai24": "Aachen-Eifel",
    "ami24": "Altmark",
    "ai24": "Anhalt",
    "abi24": "Augsburg",
    "bsi24": "Bayerisch-Schwaben",
    "bdi24": "Bergisches-Dreieck",
    "bgli24": "Bergisches-Land",
    "bi24": "Berlin",
    "bosi24": "Bodensee",
    "brai24": "Braunschweig",
    "brei24": "Bremen",
    "ci24": "Chemnitz",
    "di24": "Dortmund",
    "ddi24": "Dresden",
    "dui24": "Duisburg",
    "duei24": "Düsseldorf",
    "eli24": "Elbeland",
    "emsi24": "Emsland",
    "efi24": "Erfurt",
    "erzi24": "Erzgebirge",
    "eei24": "Essen",
    "fi24": "Frankfurt",
    "gii24": "Mittelhessen",
    "goti24": "Göttingen",
    "hai24": "Halle",
    "hhi24": "Hamburg",
    "hani24": "Hannover",
    "hi24": "Harz",
    "hli24": "Havelland",
    "hbi24": "Heilbronn",
    "hoi24": "Holstein",
    "jei24": "Jerichow",
    "ki24": "Karlsruhe",
    "kai24": "Kassel",
    "kiei24": "Kiel",
    "koei24": "Köln",
    "lwi24": "Leineweser",
    "li24": "Leipzig",
    "luei24": "Lübeck",
    "lli24": "Ludwigslust",
    "lbi24": "Lüneburg",
    "mbi24": "Magdeburg",
    "maii24": "Mainz",
    "mani24": "Mannheim",
    "mfi24": "Mittelfranken",
    "mri24": "Mittelrhein",
    "msi24": "Mittelsachsen",
    "mthi24": "Mittelthüringen",
    "mi24": "München",
    "mli24": "Münsterland",
    "nbi24": "Niederbayern",
    "nri24": "Niederrhein",
    "nsai24": "Nordsaarland",
    "nsi24": "Nordsachsen",
    "nti24": "Nordhthüringen",
    "nwmi24": "Nordwestmecklenburg",
    "obi24": "Oberbayern",
    "ofi24": "Oberfranken",
    "ohi24": "Oberhavel",
    "oli24": "Oberlausitz",
    "opi24": "Oberpfalz",
    "osi24": "Oberschwaben",
    "obli24": "Oderland",
    "osni24": "Osnabrück",
    "osai24": "Ostsaarland",
    "othi24": "Ostthüringen",
    "reki24": "Rhein-Erft-Kreis",
    "rski24": "Rhein-Sieg-Kreis",
    "rhhi24": "Rheinhessen",
    "rni24": "Rheinneckar",
    "rpi24": "Rheinpfalz",
    "rhti24": "Rheintal",
    "roi24": "Rostock",
    "rgi24": "Ruhrgebiet",
    "sui24": "Saaleunstrut",
    "sbi24": "Saarbrücken",
    "sosi24": "Sächsiche Schweiz - Osterzgebirge",
    "sli24": "Salzland",
    "saui24": "Sauerland",
    "slwi24": "Schleswig",
    "sai24": "Schwäbische Alb",
    "swwi24": "Schwarzwald",
    "si24": "Schwerin",
    "sigi24": "Siegerland",
    "swi24": "Spreewald",
    "sti24": "Stuttgart",
    "dai24": "Südhessen",
    "smbi24": "Südmecklenburg",
    "swti24": "Südwestthüringen",
    "wii24": "Taunus",
    "tbi24": "Teutoburger Wald",
    "ti24": "Trier",
    "umi24": "Uckermark",
    "ufi24": "Unterfranken",
    "vi24": "Vogtland",
    "vpi24": "Vorpommern",
    "wei24": "Weserems",
    "wesi24": "Westeifel",
    "wwi24": "Westerwald",
    "wpfi24": "Westpfalz",
    "wsai24": "Westsaarland",
    "weti24": "Wetterau",
    "zi24": "Zwickau"
}


# Backend Login
def login_to_adm(driver):
    try:
        driver.get(os.getenv('BACKEND_LINK'))
        logging.info("Backend-Seite wird aufgerufen.")
    except Exception as e:
        logging.error(f"Fehler beim Aufrufen der Seite: {e}")
        return False

    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "adm_user"))
        )
        password_field = driver.find_element(By.NAME, "adm_pw")
        logging.info("Login-Formular gefunden.")
    except Exception as e:
        logging.error(f"Login-Formular nicht gefunden: {e}")
        return False

    username_field.send_keys(username)
    password_field.send_keys(password)

    if not wait_and_click(driver, By.CLASS_NAME, "btn-inverse"):
        return False

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "content-header"))
        )
        logging.info("Login erfolgreich.")
        return True
    except Exception as e:
        logging.error(f"Login fehlgeschlagen oder Dashboard nicht geladen: {e}")
        return False

# Navigate Backend
def navigate_to_editor(driver, region_code):
    try:
        if not wait_and_click(driver, By.PARTIAL_LINK_TEXT, "alle Regionen"):
            return None

        regions_xpath = f"//a[contains(@href, 'edit_region_sites') and contains(@href, 'regio={region_code}')]"
        if not wait_and_click(driver, By.XPATH, regions_xpath):
            return None

        # Pathfinding
        click_paths = [
            "div.span6:nth-child(1) > div:nth-child(1) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(5) > a:nth-child(1) > span:nth-child(1)",
            "tr.form_inline:nth-child(5) > td:nth-child(4) > a:nth-child(1) > span:nth-child(1)",
            ".form_inline > td:nth-child(8) > a:nth-child(1) > span:nth-child(1)"
        ]

        for css_selector in click_paths:
            if not wait_and_click(driver, By.CSS_SELECTOR, css_selector):
                return None

        logging.info("Region erfolgreich geöffnet.")

        # Sourcecode edit
        source_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.cke_button__source"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", source_button)
        source_button.click()
        logging.info("In Quellcode-Modus gewechselt.")

        # Find Source-Textarea
        source_textarea = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea.cke_source"))
        )
        return source_textarea

    except Exception as e:
        logging.error(f"Fehler beim Navigieren zum Editor: {e}")
        return None

# Generate text with GPT (max. 3 retries)
def generate_new_text(region_name, retries=3):
    messages = [
        {"role": "system", "content": "Du bist ein Assistent, der SEO-Texte für Immobilien erstellt."},
        {"role": "user", "content": f"Schreibe ca. 400 Wörter über Immobilienmarkt und Baufinanzierung in {region_name}, formatiert mit <hX>, <b>, <br> usw."}
    ]
    
    for attempt in range(retries):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            logging.info(f"OpenAI Text erfolgreich bei Versuch {attempt + 1} erhalten.")
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"OpenAI Fehler Versuch {attempt + 1}/{retries}: {e}")
            time.sleep(2)  # Kurze Pause zwischen den Versuchen
    return ""
    
# Insert new content
def insert_text(source_textarea, driver, region_name):
    html_content = generate_new_text(region_name)
    if html_content:
        logging.info(f"Inhalt für {region_name} erfolgreich generiert.")
    else:
        logging.error("Inhalt leer – möglicherweise Fehler bei OpenAI.")
    
    try:
        source_textarea.clear()
        source_textarea.send_keys(html_content)
        logging.info("HTML-Inhalt eingefügt.")
    except Exception as e:
        logging.error(f"Fehler beim Einfügen des Inhalts: {e}")

# Save content and continue on next entry then logout
def save_content(driver):
    try:
        save_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".display"))
        )
        save_button.click()
        logging.info("Neuer Inhalt erfolgreich gespeichert.")
    except Exception as e:
        logging.error(f"Fehler beim Speichern: {e}")

    # Jetzt nach dem Klick wirklich warten, bis Übersichtsseite wieder bereit ist!
    try:
        # Warten auf etwas, das NUR auf der Übersichtsseite sicher erscheint:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "alle Regionen"))
        )

        # Jetzt erst neu suchen und klicken
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "alle Regionen"))
        ).click()

        logging.info("Zurück zur Übersicht gewechselt.")
    except Exception as e:
        logging.error(f"Fehler beim Zurückkehren zur Übersicht: {e}")

def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    if not login_to_adm(driver):
        logging.error("Login fehlgeschlagen. Skript wird beendet.")
        driver.quit()
        return
    
    for region_code, region_display in region_mapping.items():
        logging.info(f"Bearbeite Region: {region_display} ({region_code})")
        
        source_textarea = navigate_to_editor(driver, region_code)
        if source_textarea:
            insert_text(source_textarea, driver, region_display)
            save_content(driver)
        else:
            logging.warning(f"Region übersprungen: {region_display}")
    
    driver.quit()
