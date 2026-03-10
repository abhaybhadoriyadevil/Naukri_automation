"""
Indeed Updater — automates login and resume upload on Indeed.com.
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


def login_indeed(driver) -> bool:
    """
    Log in to Indeed with credentials from config.
    Returns True on success, False on failure.
    """
    logger.info("Navigating to Indeed login page ...")
    driver.get(config.INDEED_LOGIN_URL)
    random_delay(3, 6)

    dismiss_popups(driver)

    try:
        # ── Step 1: Enter email ─────────────────────────────────
        email_field = wait_and_find(driver, By.XPATH,
            "//input[@type='email' or @id='ifl-InputFormField-3' or "
            "@name='__email' or contains(@id,'email') or "
            "contains(@aria-label,'Email')]",
            timeout=15
        )
        human_type(email_field, config.INDEED_EMAIL)
        logger.info("Entered Indeed email")
        random_delay(1, 2)

        # Click continue / submit email
        continue_btn = safe_find(driver, By.XPATH,
            "//button[@type='submit' or contains(text(),'Continue') or "
            "contains(text(),'continue') or contains(text(),'Next')]",
            timeout=10
        )
        if continue_btn:
            continue_btn.click()
            logger.info("Clicked continue after email")
            random_delay(3, 5)

        # ── Step 2: Enter password ──────────────────────────────
        pass_field = wait_and_find(driver, By.XPATH,
            "//input[@type='password' or @id='ifl-InputFormField-7' or "
            "contains(@name,'password') or contains(@id,'password')]",
            timeout=15
        )
        human_type(pass_field, config.INDEED_PASSWORD)
        logger.info("Entered Indeed password")
        random_delay(1, 2)

        # Click Sign In
        signin_btn = wait_and_click(driver, By.XPATH,
            "//button[@type='submit' or contains(text(),'Sign') or "
            "contains(text(),'sign') or contains(text(),'Log')]",
            timeout=10
        )
        logger.info("Clicked Sign In")
        random_delay(5, 8)

        # ── Handle potential verification ───────────────────────
        # Indeed sometimes asks for email/phone verification
        verify_page = safe_find(driver, By.XPATH,
            "//*[contains(text(),'verify') or contains(text(),'Verify') or "
            "contains(text(),'security check')]",
            timeout=5
        )
        if verify_page:
            logger.warning("⚠️ Indeed is requesting verification — "
                           "manual intervention may be needed")
            # Wait extra time for manual verification
            random_delay(30, 45)

        # Dismiss popups
        dismiss_popups(driver)

        # Check if logged in
        if "auth" not in driver.current_url.lower():
            logger.info("✅ Indeed login successful!")
            return True
        else:
            driver.save_screenshot("indeed_login_failed.png")
            logger.error("❌ Indeed login may have failed (saved indeed_login_failed.png)")
            return False

    except TimeoutException as e:
        driver.save_screenshot("indeed_login_timeout.png")
        logger.error(f"❌ Indeed login timed out: {e} (saved indeed_login_timeout.png)")
        return False
    except Exception as e:
        driver.save_screenshot("indeed_login_error.png")
        logger.error(f"❌ Indeed login error: {e} (saved indeed_login_error.png)")
        return False


def upload_resume_indeed(driver, resume_path: Path) -> bool:
    """
    Navigate to Indeed resume page and upload the resume.
    Returns True on success, False on failure.
    """
    logger.info("Navigating to Indeed resume page ...")
    driver.get(config.INDEED_RESUME_URL)
    random_delay(4, 7)

    dismiss_popups(driver)

    try:
        # ── Method 1: Look for file input directly ──────────────
        file_input = safe_find(driver, By.XPATH,
            "//input[@type='file' and (contains(@id,'upload') or "
            "contains(@name,'file') or contains(@accept,'.pdf'))]",
            timeout=10
        )

        if file_input:
            abs_path = str(resume_path.resolve())
            file_input.send_keys(abs_path)
            logger.info(f"Uploaded resume via file input: {resume_path.name}")
            random_delay(5, 8)

            # Look for save/confirm button
            save_btn = safe_find(driver, By.XPATH,
                "//button[contains(text(),'Save') or contains(text(),'save') or "
                "contains(text(),'Done') or contains(text(),'Upload') or "
                "contains(@type,'submit')]",
                timeout=10
            )
            if save_btn:
                save_btn.click()
                logger.info("Clicked save/upload button")
                random_delay(3, 5)

            logger.info("✅ Resume uploaded on Indeed!")
            return True

        # ── Method 2: Click 'Upload resume' link/button first ──
        upload_btn = safe_find(driver, By.XPATH,
            "//*[contains(text(),'Upload') or contains(text(),'upload') or "
            "contains(text(),'Replace') or contains(text(),'replace') or "
            "contains(text(),'Update resume')]",
            timeout=10
        )

        if upload_btn:
            logger.info("Found 'Upload/Replace' button, clicking ...")
            upload_btn.click()
            random_delay(2, 4)

            # Try file input again
            file_input = safe_find(driver, By.XPATH, "//input[@type='file']", timeout=10)
            if file_input:
                abs_path = str(resume_path.resolve())
                file_input.send_keys(abs_path)
                logger.info(f"Uploaded resume: {resume_path.name}")
                random_delay(5, 8)

                # Save
                save_btn = safe_find(driver, By.XPATH,
                    "//button[contains(text(),'Save') or contains(@type,'submit')]",
                    timeout=10
                )
                if save_btn:
                    save_btn.click()
                    random_delay(3, 5)

                return True

        logger.error("❌ Could not find resume upload element on Indeed")
        return False

    except Exception as e:
        logger.error(f"❌ Resume upload failed on Indeed: {e}")
        return False


def run_indeed(resume_path: Path, dry_run: bool = False) -> bool:
    """
    Full Indeed flow: login → upload resume.
    Returns True if everything succeeds.
    """
    if not config.INDEED_EMAIL or not config.INDEED_PASSWORD:
        logger.error("❌ Indeed credentials not set in .env file!")
        return False

    if dry_run:
        logger.info("🏃 DRY RUN — Indeed: would login and upload resume")
        return True

    driver = None
    try:
        driver = create_driver()

        # Step 1: Login
        if not login_indeed(driver):
            return False

        random_delay(2, 4)

        # Step 2: Upload resume
        if not upload_resume_indeed(driver, resume_path):
            return False

        logger.info("🎉 Indeed profile updated successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Indeed automation failed: {e}")
        return False
    finally:
        if driver:
            random_delay(2, 3)
            driver.quit()
            logger.info("Chrome closed (Indeed)")
