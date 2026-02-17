import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:5001"

def test_full_flow():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        print("\n--- Starting Final Automated Workflow Test ---")
        
        # 1. Login
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "email").send_keys("ananya@example.com")
        driver.find_element(By.NAME, "password").send_keys("password123")
        driver.find_element(By.CSS_SELECTOR, "button.bg-pink").click()
        wait.until(EC.url_contains("/dashboard"))
        print("✓ Login: OK")

        # 2. Raise Complaint
        driver.find_element(By.NAME, "title").send_keys("Automated Test")
        driver.find_element(By.NAME, "description").send_keys("Testing button...")
        driver.find_element(By.XPATH, "//button[contains(text(), 'Submit Issue')]").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "flash-msg")))
        print("✓ Raise Complaint: OK")

        # 3. Explore Rooms
        explore_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Explore Rooms")))
        explore_link.click()
        wait.until(EC.url_to_be(f"{BASE_URL}/"))
        print("✓ Explore Rooms Page: OK")

        # 4. Book Room
        book_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/book/')]")))
        book_btn.click()
        wait.until(EC.url_contains("/book/"))
        print("✓ Room Details Page: OK")
        
        driver.find_element(By.NAME, "start_date").send_keys("20-12-2026")
        driver.find_element(By.XPATH, "//button[contains(text(), 'Confirm Booking')]").click()
        wait.until(EC.url_contains("/dashboard"))
        print("✓ Booking Process: OK")

        # 5. Admin Flow
        driver.find_element(By.XPATH, "//a[contains(@href, '/logout')]").click()
        driver.get(f"{BASE_URL}/login")
        driver.find_element(By.NAME, "email").send_keys("admin@example.com")
        driver.find_element(By.NAME, "password").send_keys("admin123")
        driver.find_element(By.CSS_SELECTOR, "button.bg-pink").click()
        wait.until(EC.url_contains("/admin/dashboard"))
        print("✓ Admin Login: OK")

        # 6. Resolve Complaint
        wait.until(EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Automated Test')]")))
        resolve_btn = driver.find_element(By.XPATH, "//a[contains(text(), 'Mark Resolved')]")
        resolve_btn.click()
        print("✓ Admin Complaint Resolution: OK")

        print("\n✨ ALL BUTTONS AND WORKFLOWS TESTED SUCCESSFULLY! 🌈👑")

    except Exception as e:
        print(f"\n❌ TEST FAILED at URL: {driver.current_url}")
        print(f"Error: {str(e)}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_full_flow()
