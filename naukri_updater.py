"""
Naukri Updater — automates login and resume upload on Naukri.com.
"""

import logging
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import config
from browser_helpers import (
    create_driver,
    random_delay,
    human_type,
    wait_and_find,
    wait_and_click,
    safe_find,
    dismiss_popups,
)

logger = logging.getLogger(__name__)


def login_naukri(driver) -> bool:
    """
    Log in to Naukri.com with credentials from config.
    Returns True on success, False on failure.
    """
    logger.info("Navigating to Naukri login page ...")
    driver.get(config.NAUKRI_LOGIN_URL)
    random_delay(3, 6)

    # Dismiss any initial popups
    dismiss_popups(driver)

    try:
        # Enter email
        email_field = wait_and_find(driver, By.XPATH,
            "//input[@type='text' and (@placeholder='Enter your active Email ID / Username' "
            "or @id='usernameField' or contains(@name,'email') or contains(@name,'username'))]"
        )
        human_type(email_field, config.NAUKRI_EMAIL)
        logger.info("Entered email")
        random_delay(1, 2)

        # Enter password
        pass_field = wait_and_find(driver, By.XPATH,
            "//input[@type='password' and (@placeholder='Enter your password' "
            "or @id='passwordField' or contains(@name,'password'))]"
        )
        human_type(pass_field, config.NAUKRI_PASSWORD)
        logger.info("Entered password")
        random_delay(1, 2)

        # Click login button
        login_btn = wait_and_click(driver, By.XPATH,
            "//button[@type='submit' and (contains(text(),'Login') or "
            "contains(text(),'login') or contains(@class,'loginButton'))]"
        )
        logger.info("Clicked login button")
        random_delay(4, 7)

        # Dismiss any post-login popups
        dismiss_popups(driver)

        # Verify login success — look for profile icon or name
        profile_indicator = safe_find(driver, By.XPATH,
            "//*[contains(@class,'nI-gNb-drawer__icon') or "
            "contains(@class,'user-name') or "
            "contains(@class,'nI-gNb-sb__header')]",
            timeout=10
        )

        if profile_indicator:
            logger.info("✅ Naukri login successful!")
            return True
        else:
            # Check if still on login page (could mean wrong credentials)
            if "login" in driver.current_url.lower():
                driver.save_screenshot("naukri_login_failed.png")
                logger.error("❌ Login failed — possibly wrong credentials (saved naukri_login_failed.png)")
                return False
            # Might have logged in but indicator not found
            logger.warning("⚠️ Login status uncertain, proceeding anyway ...")
            return True

    except TimeoutException as e:
        driver.save_screenshot("naukri_login_timeout.png")
        logger.error(f"❌ Naukri login timed out: {e} (saved naukri_login_timeout.png)")
        return False
    except Exception as e:
        driver.save_screenshot("naukri_login_error.png")
        logger.error(f"❌ Naukri login error: {e} (saved naukri_login_error.png)")
        return False


def upload_resume_naukri(driver, resume_path: Path) -> bool:
    """
    Navigate to Naukri profile and upload the resume.
    Returns True on success, False on failure.
    """
    logger.info("Navigating to Naukri profile page ...")
    driver.get(config.NAUKRI_PROFILE_URL)
    random_delay(4, 7)

    # Dismiss popups
    dismiss_popups(driver)

    try:
        # ── Method 1: Direct file input upload ──────────────────
        # Naukri has a hidden file input for resume upload
        file_input = safe_find(driver, By.XPATH,
            "//input[@type='file' and (contains(@id,'attachCV') or "
            "contains(@name,'file') or contains(@id,'fileUpload') or "
            "contains(@class,'fileUpload'))]",
            timeout=10
        )

        if file_input:
            abs_path = str(resume_path.resolve())
            file_input.send_keys(abs_path)
            logger.info(f"Uploaded resume via file input: {resume_path.name}")
            random_delay(5, 8)

            # Check for success message
            success = safe_find(driver, By.XPATH,
                "//*[contains(text(),'successfully') or "
                "contains(text(),'uploaded') or "
                "contains(text(),'updated')]",
                timeout=10
            )
            if success:
                logger.info("✅ Resume upload confirmed on Naukri!")
                return True
            else:
                logger.warning("⚠️ Upload may have succeeded (no confirmation message found)")
                return True

        # ── Method 2: Click update resume button first ──────────
        update_btn = safe_find(driver, By.XPATH,
            "//*[contains(text(),'Update resume') or "
            "contains(text(),'update resume') or "
            "contains(text(),'Upload Resume') or "
            "contains(@class,'widgetHead') and contains(text(),'Resume')]",
            timeout=10
        )

        if update_btn:
            logger.info("Found 'Update Resume' button, clicking ...")
            update_btn.click()
            random_delay(2, 4)

            # Now look for file input again
            file_input = safe_find(driver, By.XPATH, "//input[@type='file']", timeout=10)
            if file_input:
                abs_path = str(resume_path.resolve())
                file_input.send_keys(abs_path)
                logger.info(f"Uploaded resume: {resume_path.name}")
                random_delay(5, 8)
                return True

        logger.error("❌ Could not find resume upload element on Naukri")
        return False

    except Exception as e:
        logger.error(f"❌ Resume upload failed on Naukri: {e}")
        return False


def run_naukri(resume_path: Path, dry_run: bool = False) -> bool:
    """
    Full Naukri flow: login → upload resume.
    Returns True if everything succeeds.
    """
    if not config.NAUKRI_EMAIL or not config.NAUKRI_PASSWORD:
        logger.error("❌ Naukri credentials not set in .env file!")
        return False

    if dry_run:
        logger.info("🏃 DRY RUN — Naukri: would login and upload resume")
        return True

    driver = None
    try:
        driver = create_driver()

        # Step 1: Login
        if not login_naukri(driver):
            return False

        random_delay(2, 4)

        # Step 2: Upload resume
        if not upload_resume_naukri(driver, resume_path):
            return False

        logger.info("🎉 Naukri profile updated successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Naukri automation failed: {e}")
        return False
    finally:
        if driver:
            random_delay(2, 3)
            driver.quit()
            logger.info("Chrome closed (Naukri)")
