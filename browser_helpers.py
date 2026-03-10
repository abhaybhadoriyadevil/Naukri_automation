"""
Browser Helpers — shared utilities for Selenium automation.
Provides anti-detection Chrome setup and human-like interaction helpers.
"""

import time
import random
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)
from webdriver_manager.chrome import ChromeDriverManager

import config

logger = logging.getLogger(__name__)


def create_driver() -> webdriver.Chrome:
    """
    Create a Chrome WebDriver with anti-detection options.
    """
    options = Options()

    for arg in config.CHROME_ARGUMENTS:
        options.add_argument(arg)

    options.add_experimental_option("excludeSwitches", config.CHROME_EXCLUDE_SWITCHES)
    options.add_experimental_option("prefs", config.CHROME_PREFS)
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Remove webdriver property to avoid detection
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                // Override plugins length
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                // Override languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """
        },
    )

    logger.info("Chrome driver created with anti-detection options")
    return driver


def random_delay(min_sec: float = None, max_sec: float = None) -> None:
    """Sleep for a random duration to mimic human behavior."""
    mn = min_sec or config.MIN_DELAY
    mx = max_sec or config.MAX_DELAY
    delay = random.uniform(mn, mx)
    logger.debug(f"Waiting {delay:.1f}s ...")
    time.sleep(delay)


def human_type(element, text: str) -> None:
    """
    Type text character-by-character with random delays to mimic human typing.
    """
    element.clear()
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(config.KEYSTROKE_MIN, config.KEYSTROKE_MAX))


def wait_and_find(driver, by: By, value: str, timeout: int = 15):
    """Wait for an element to be present and return it."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def wait_and_click(driver, by: By, value: str, timeout: int = 15):
    """Wait for an element to be clickable and click it."""
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    element.click()
    return element


def safe_find(driver, by: By, value: str, timeout: int = 5):
    """
    Try to find an element, return None if not found (no exception).
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except (TimeoutException, NoSuchElementException):
        return None


def dismiss_popups(driver) -> None:
    """
    Try to close common popups/overlays that may block interaction.
    """
    popup_selectors = [
        (By.CSS_SELECTOR, "button.crossIcon"),              # Naukri popup close
        (By.CSS_SELECTOR, "[class*='close']"),               # generic close buttons
        (By.CSS_SELECTOR, "[aria-label='Close']"),           # aria close
        (By.XPATH, "//button[contains(text(),'Not now')]"),  # "Not now" buttons
        (By.XPATH, "//button[contains(text(),'Later')]"),    # "Later" buttons
    ]

    for by, selector in popup_selectors:
        try:
            btn = driver.find_element(by, selector)
            if btn.is_displayed():
                btn.click()
                logger.info(f"Dismissed popup: {selector}")
                time.sleep(1)
        except (NoSuchElementException, ElementNotInteractableException):
            continue
