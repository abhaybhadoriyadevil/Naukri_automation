# 🚀 Resume Upload Automation

Automatically upload your resume to **Naukri.com** and **Indeed.com** twice daily to keep your profile fresh and boost recruiter visibility.

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

INDEED_EMAIL=your_real_email@gmail.com
INDEED_PASSWORD=your_real_password
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
| `python main.py` | Run both Naukri + Indeed |
| `python main.py --naukri` | Run Naukri only |
| `python main.py --indeed` | Run Indeed only |
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
├── indeed_updater.py    # Indeed login + upload
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

## 🔧 Troubleshooting

| Issue | Solution |
|---|---|
| Chrome doesn't open | Install Google Chrome, run `pip install webdriver-manager` |
| Login fails | Verify credentials in `.env`, check for CAPTCHA |
| Upload not found | Website layout may have changed — check logs |
| Task Scheduler fails | Run `setup_scheduler.bat` as **Administrator** |
| Indeed verification | First login manually and complete any verification, then re-run |
