"""
Main Entry Point — Orchestrates resume rename + Naukri & Indeed upload.

Usage:
    python main.py              # Full run (both sites)
    python main.py --dry-run    # Test without actual login/upload
    python main.py --naukri     # Only Naukri
    python main.py --indeed     # Only Indeed
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

import config
from resume_renamer import rename_resume, cleanup_old_resumes
from naukri_updater import run_naukri
from indeed_updater import run_indeed


def setup_logging() -> None:
    """Configure logging to both console and file."""
    log_file = config.LOGS_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s │ %(levelname)-7s │ %(name)-18s │ %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )


def main() -> None:
    setup_logging()
    logger = logging.getLogger("main")

    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    run_naukri_flag = "--naukri" in args
    run_indeed_flag = "--indeed" in args
    run_all = not run_naukri_flag and not run_indeed_flag  # default: both

    logger.info("=" * 60)
    logger.info("🚀  RESUME UPLOAD AUTOMATION STARTED")
    logger.info(f"📅  Date: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    if dry_run:
        logger.info("🏃  Mode: DRY RUN (no actual login/upload)")
    logger.info("=" * 60)

    # ── Step 1: Rename resume ──────────────────────────────────
    try:
        resume_path = rename_resume()
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        logger.error("Please place your resume as 'resume.pdf' in the project folder.")
        sys.exit(1)

    # ── Step 2: Run Naukri ─────────────────────────────────────
    naukri_ok = True
    if run_all or run_naukri_flag:
        logger.info("")
        logger.info("─── NAUKRI.COM ──────────────────────────────")
        naukri_ok = run_naukri(resume_path, dry_run=dry_run)

    # ── Step 3: Run Indeed ─────────────────────────────────────
    indeed_ok = True
    if run_all or run_indeed_flag:
        logger.info("")
        logger.info("─── INDEED.COM ─────────────────────────────")
        indeed_ok = run_indeed(resume_path, dry_run=dry_run)

    # ── Step 4: Cleanup old resumes ────────────────────────────
    cleanup_old_resumes(keep_latest=3)

    # ── Summary ────────────────────────────────────────────────
    logger.info("")
    logger.info("=" * 60)
    logger.info("📊  RESULTS SUMMARY")
    logger.info("-" * 60)

    if run_all or run_naukri_flag:
        status = "✅ SUCCESS" if naukri_ok else "❌ FAILED"
        logger.info(f"   Naukri  : {status}")

    if run_all or run_indeed_flag:
        status = "✅ SUCCESS" if indeed_ok else "❌ FAILED"
        logger.info(f"   Indeed  : {status}")

    logger.info("=" * 60)

    if not naukri_ok or not indeed_ok:
        logger.warning("⚠️ Some tasks failed. Check logs for details.")
        sys.exit(1)

    logger.info("🎉 All tasks completed successfully!")


if __name__ == "__main__":
    main()
