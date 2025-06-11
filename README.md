# HealthQ
# 🏥 HealthQ – Smart Doctor Appointment Booking System

**HealthQ** is a cloud-integrated, web-based application that allows users to seamlessly book and manage doctor appointments. Designed with accessibility and ease of use in mind, it minimizes wait times and eliminates the need for manual appointment scheduling.

> 📰 Published in: *Recent Trends in Androids and iOS Applications*, Vol 7 Issue 2 (2025)  
> 📄 DOI: [10.5281/zenodo.15550768](https://doi.org/10.5281/zenodo.15550768)

---

## 🧩 Features

- 🔐 Secure user & admin authentication
- 🗓️ Real-time appointment booking with available slot selection
- ❌ Appointment cancellation & rescheduling
- 🧾 Doctor profiles with department filter
- 💊 Integrated pharmacy & insurance modules
- 📬 Automated notifications for reminders
- 🗣️ Patient feedback system
- 📊 Admin dashboard for managing appointments
- 📱 Fully responsive web design

---

## 🛠 Tech Stack

| Layer       | Technology               |
|-------------|---------------------------|
| Frontend    | HTML5, CSS3, JavaScript, Bootstrap |
| Backend     | Python (Flask Framework)  |
| Database    | SQLite 3                  |
| Authentication | Flask-Login & Password Hashing |
| Development | Visual Studio Code        |

---

## 🚀 How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/your-username/HealthQ.git
cd HealthQ

# 2. Set up virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask app
python app.py

# 5. Open in browser
Visit http://127.0.0.1:5000/

HealthQ/
│
├── static/           # CSS, JS, and image assets
├── templates/        # HTML templates (Jinja2)
├── app.py            # Main Flask application
├── database.db       # SQLite database file
├── requirements.txt  # Python dependencies
└── README.md
