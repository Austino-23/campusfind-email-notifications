# CampusFind — Django-connected version

This project uses **HTML, CSS, JavaScript, Python, Django, and SQLite**. It has five website pages: Home, Accounts, Report an Item, Browse Items, and Dashboard. The Django admin interface is an extra built-in management tool, not a sixth public website page.

## Features connected to Django
- Registration and login using Django authentication; passwords are hashed by Django.
- Logout via a CSRF-protected POST form.
- Lost/found reports saved to the SQLite database.
- Search and filters for item name, description, location, report type, and category.
- Optional item photo upload (JPG/PNG/WEBP, up to 5 MB).
- Ownership claims saved in the database, with duplicate claims prevented.
- Automatic lost/found matching by category, item name, description, and location.
- Email notification records saved in SQL to prevent duplicate emails for the same lost/found pair.
- Email backend supports safe local console testing and SMTP delivery for deployment.
- Users can manage their own reports and review claims relating to their reports.
- Staff users can manage reports and claims across the system.
- Django admin for staff at `/django-admin/`.
- CSRF protection on all state-changing forms.

## Requirements
- Python 3.10 or newer (Python 3.11+ recommended)
- Internet only for the initial Django installation

## Run on Windows (VS Code)
1. Extract this ZIP file.
2. Open the extracted `CampusFind_Django` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
5. Activate it:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat` instead.
6. Install Django:
   ```powershell
   python -m pip install -r requirements.txt
   ```
7. Apply the database migrations:
   ```powershell
   python manage.py migrate
   ```
8. Create an administrator account:
   ```powershell
   python manage.py createsuperuser
   ```
   Follow the prompts to enter a username, email (if requested), and password.
9. Start the website:
   ```powershell
   python manage.py runserver
   ```
10. Open `http://127.0.0.1:8000/` in your browser.

## How to test
1. Open `/accounts/` and create a student account using an email address and password of at least 8 characters.
2. Go to **Report an item** and submit a lost or found report.
3. Open **Browse items** and search for the report. It is stored in SQLite, so it remains after restarting the server.
4. Create a second account in a private/incognito browser window and submit a claim on the first account's report.
5. Sign back in as the first user and open **Dashboard** to approve or reject the claim.
6. Sign in as the superuser to see the staff dashboard, and visit `/django-admin/` for the full Django admin.

## Important notes
- This is a local development project. `DEBUG=True` and the development secret key are not safe for public production deployment. Before deploying, set a private `SECRET_KEY`, set `DEBUG=False`, configure `ALLOWED_HOSTS`, use HTTPS, and configure persistent media storage.
- The optional image upload is saved under the local `media/` folder during development.
- The email field is used as the account username. Each email address can only register once.
- If the project already has migrations, run `python manage.py migrate` rather than deleting the database.
- This package includes the original CampusFind CSS and the new Django templates. The original static HTML preview files are not required to run the Django version.


## Automatic matching and email notifications
When a signed-in user submits a **found** report, CampusFind compares it with unresolved **lost** reports in the same category. The matcher scores name, description, and location similarity; a score of 0.58 or higher is treated as a possible match. CampusFind emails the lost-report owner using the contact email on that report, falling back to the owner's account email. The email describes it as a possible match, not proof of ownership. Notification records are visible in Django admin and prevent repeated messages for the same lost/found pair.

### Test email locally
By default, development email uses Django's console backend. Submit a found report that closely matches an unresolved lost report, then check the VS Code terminal where `runserver` is running; the email content should print there. The recipient must have an email address in the lost report or their account.

### Send real emails (Gmail SMTP example)
For actual delivery, use a Gmail **App Password** (not your normal Gmail password) and configure environment variables. In PowerShell, before starting the server, run:

```powershell
$env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST="smtp.gmail.com"
$env:EMAIL_PORT="587"
$env:EMAIL_USE_TLS="True"
$env:EMAIL_HOST_USER="your-sending-address@gmail.com"
$env:EMAIL_HOST_PASSWORD="your-16-character-app-password"
$env:DEFAULT_FROM_EMAIL="CampusFind <your-sending-address@gmail.com>"
python manage.py runserver
```

Replace the example values with your own. Do not commit credentials to GitHub. For Render, add the same values under **Environment** in your web service settings; set `EMAIL_BACKEND` to `django.core.mail.backends.smtp.EmailBackend`. If SMTP is not configured, the report will still save, but real emails will not be delivered.

### Matching limitations
This is text-based matching, not image recognition. Similar item names and descriptions help; very different descriptions or incorrect categories may prevent a match. Tune `MATCH_THRESHOLD` in `core/services.py` if testing shows it is too strict or too permissive.
