# 🚀 Resume Upload Automation

Automatically upload your resume to **Naukri.com** twice daily to keep your profile fresh and boost recruiter visibility.

## 📋 Features

- 📄 Auto-renames resume with today's date (e.g., `Abhay_Resume_10_Mar_2026.pdf`)
- 🔒 Credentials stored securely in local `.env` file
- 🕵️ Anti-bot detection (random delays, human-like typing, stealth Chrome flags)
- 🗑️ Auto-cleans old resume copies (keeps latest 3)
- 📝 Detailed logging to `logs/` folder
- ⏰ Windows Task Scheduler integration (9 AM + 2 PM daily)

---

## ⚡ Quick Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add Your Resume

Place your resume as **`resume.pdf`** in this folder.

### 3. Set Your Credentials

Edit the **`.env`** file with your actual credentials:

```env
NAUKRI_EMAIL=your_real_email@gmail.com
NAUKRI_PASSWORD=your_real_password
```

### 4. Test (Dry Run)

```bash
python main.py --dry-run
```

### 5. Full Test Run

```bash
python main.py
```

Watch the browser open, log in, and upload your resume automatically!

### 6. Schedule Automatic Runs

**Right-click** `setup_scheduler.bat` → **Run as Administrator**

This creates two Windows Task Scheduler tasks:
- `NaukriResumeUpload_9AM` — runs daily at 09:00
- `NaukriResumeUpload_2PM` — runs daily at 14:00

---

## 🎮 Usage Options

| Command | Description |
|---|---|
| `python main.py` | Run Naukri automation |
| `python main.py --dry-run` | Test without actual login |

---

## 📁 Project Structure

```
automation resume upload/
├── main.py              # Entry point
├── config.py            # Settings & credentials
├── resume_renamer.py    # Date-stamp resume copies
├── browser_helpers.py   # Anti-detection Chrome setup
├── naukri_updater.py    # Naukri login + upload
├── setup_scheduler.bat  # Windows Task Scheduler setup
├── requirements.txt     # Python dependencies
├── .env                 # Your credentials (never share!)
├── resume.pdf           # Your base resume (add this)
└── logs/                # Run logs
```

---

## ⚠️ Safety Tips

- ✅ Only updates resume **twice daily** — safe frequency
- ✅ Uses random delays between all actions
- ✅ Human-like keystroke timing
- ❌ Don't run more than 2-3 times per day
- ❌ Don't use for mass auto-applying to jobs
- 🔒 Never share your `.env` file

---

## 🤖 GitHub Actions Setup (Run Without PC)

You can run this automation entirely in the cloud using GitHub Actions at 9 AM and 2 PM IST automatically.

### 1. Push to GitHub
If you haven't already, push this code to your GitHub repository (`Naukri_automation`).

### 2. Add Secrets to GitHub
Since `.env` is ignored and *should never* be uploaded to GitHub, you need to provide your credentials via **GitHub Secrets**.

1. Go to your repository on GitHub.
2. Click **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret** and add the following two secrets exactly as named:
   - `NAUKRI_EMAIL` (your naukri email)
   - `NAUKRI_PASSWORD` (your naukri password)

### 3. How it Runs
The `.github/workflows/upload_resume.yml` file is already configured. 
- It will automatically trigger every day at **09:00 AM IST** and **02:00 PM IST**.
- It runs a "headless" version of Chrome on an Ubuntu server.
- You can also manually trigger it by going to the **Actions** tab on GitHub and clicking **Run workflow**.

> ⚠️ **IMPORTANT WARNING FOR CLOUD AUTOMATION:** 
> Job portals (especially Naukri and Indeed) have advanced bot-protection. They often block logins coming from data-center IP addresses like those used by GitHub Actions or AWS. 
> 
> *If the GitHub Action fails with a "Login failed" or "Timeout" error in the logs, Naukri has blocked the GitHub IP. In that case, you must fallback to using the Local Windows Task Scheduler method (which runs from your safe, home IP).*

| Issue | Solution |
|---|---|
| Chrome doesn't open | Install Google Chrome, run `pip install webdriver-manager` |
| Login fails | Verify credentials in `.env`, check for CAPTCHA |
| Upload not found | Website layout may have changed — check logs |
| Task Scheduler fails | Run `setup_scheduler.bat` as **Administrator** |
