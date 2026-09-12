import time
import os
import smtplib
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ==== НАСТРОЙКИ EMAIL ====
EMAIL_FROM = "kersrus@yandex.ru"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_TO = "kersrus@yandex.ru"

TARGET_URL = "https://parking.mos.ru/parking/barrier/subscribe/"
ADDRESS_TEXT = "Новотушинский"


def send_email(text):
    try:
        msg = MIMEText(text, "plain", "utf-8")
        msg["Subject"] = "Свободное место на парковке!"
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        server = smtplib.SMTP_SSL("smtp.yandex.ru", 465)
        server.login("kersrus", EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        server.quit()
        print("✅ Email отправлен!")
    except Exception as e:
        print("Ошибка email:", e)


def check():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("Открываю сайт...")
        driver.get(TARGET_URL)
        time.sleep(6)

        print("Кликаю по СЗАО...")
        region = driver.find_element(By.CSS_SELECTOR, '[data-value="0900"]')
        driver.execute_script("arguments[0].click();", region)
        time.sleep(6)

        # Ищем элемент с нужным адресом
        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{ADDRESS_TEXT}')]")

        if not elements:
            print("Элемент с адресом не найден на странице.")
            return False

        element = elements[0]
        class_attr = element.get_attribute("class") or ""
        print(f"Класс элемента: '{class_attr}'")

        if "disabledVar" in class_attr:
            print("😔 Мест нет (элемент заблокирован).")
            return False
        else:
            print("🎉 МЕСТО ПОЯВИЛОСЬ! Отправляю письмо...")
            send_email(f"Появилось свободное место!\nАдрес: Новотушинский проезд, вл. 8, к. 1\nСсылка: {TARGET_URL}")
            return True

    except Exception as e:
        print("Ошибка:", e)
        return False
    finally:
        driver.quit()


if __name__ == "__main__":
    print("Проверяю парковку...")
    check()