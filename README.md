
# Spark_Sports
E-commerce store

# 🏏 Spark Sports - Premium Cricket Sports-Commerce Brand

Spark Sports is a professional, responsive, and modern e-commerce web application engineered for a Pakistani cricket sports brand. It features English Willow cricket gear, apparel, and training protection with a custom high-performance UI design system, built-in customer user profiles, a session-based shopping cart, checkout forms, and **Spark AI**—a draggable virtual assistant capable of recommending products, responding to page-specific contexts, and designing cricket training diet programs.

---

## 🚀 Key Features

* **⚡ Energetic Custom Theme:** Clean Outfit typography system featuring charcoal slate panels, crisp white grids, and neon-green accents. Fully responsive for desktop, tablet, and mobile browsers.
* **📦 Product Catalog:** Dynamic grid view with category filters, price range sliders, text search, and sorting (price low-to-high, high-to-low, newest).
* **🛒 Session Shopping Cart:** Works out of the box for guests and authenticated members. Handles real-time item increments, stock constraint checks, and automatic subtotal/shipping updates.
* **🧾 Cash on Delivery Checkout:** Secure billing address entry form with Pakistan province dropdown menus. Calculates order totals on the server to prevent browser tampering.
* **👤 User Account Dashboard:** Secure authentication system for customer registration, profile listings, and past order details logs.
* **🤖 Draggable Spark AI Chatbot:** A movable floating bubble in the bottom right that expands to a chat drawer.
  * **API Connected:** Connects directly to the Google Gemini API (gemini-1.5-flash) using standard libraries.
  * **Offline Fallback:** Runs a local rule-based expert system if no API key is set.
  * **Product Aware:** Understands the page context if clicked from a cricket product details screen.
  * **Diet Questionnaire:** Walks players through an interactive 4-step onboarding questionnaire to generate a 7-day cricket training meal plan.

---

## 🛠️ Technology Stack

* **Backend:** Python, Django 5.0+
* **Frontend:** Custom CSS3 (Flexbox & Grid systems), HTML5, JavaScript (Vanilla ES6), FontAwesome icons, Google Fonts
* **Database:** SQLite (structured to support PostgreSQL in production environments)
* **Images:** Pillow library (Django media configurations)
* **AI Engine:** Google Gemini API Integration (fallback offline engine built-in)

---

## 📁 Directory Structure

```
sports_store/
├── .env                  # Environment keys (ignored by git)
├── .env.example          # Template environment parameters
├── .gitignore            # Git exclusion targets
├── requirements.txt      # Python library dependencies
├── manage.py             # Django controller
│
├── config/               # Settings & URL configuration
│   ├── settings.py
│   └── urls.py
│
├── core/                 # Navigation system, home views & static files
├── products/             # Category & Product models, listing & details
├── accounts/             # Registration, login, logout, and dashboard views
├── cart/                 # Session-based shopping cart & context processors
├── orders/               # Checkout, order models, and details invoicing
├── chatbot/              # Spark AI endpoint and services layer
│
├── static/               # Compilation static assets
│   ├── css/style.css     # Spark Sports CSS Design Tokens
│   └── js/main.js        # Draggable bubble controls & AJAX chat client
│
└── templates/            # HTML pages split by features
    ├── base.html         # Navbar, alerts, layout wrapper & chatbot drawer
    ├── core/home.html    # Home page with USP banners & featured sliders
    ├── products/         # Product grids & detailed context panels
    ├── accounts/         # Login, register, and dashboard layout
    ├── cart/detail.html  # Shopping cart list & checkout summaries
    ├── orders/           # Checkout form, success logs & invoice lookup
    └── chatbot/widget.html # Floating chat UI drawer
```

---

## ⚙️ Installation & Local Setup

Get Spark Sports running on your local machine by executing the following commands:

### 1. Clone & Enter Directory
Clone this repository and navigate into the project root:
```bash
git clone https://github.com/muserah-hub/Spark_Sports.git
cd Spark_Sports/
```
*(If working inside the workspace root, proceed directly to Step 2).*

### 2. Configure Virtual Environment
Create and activate a Python virtual environment:
* **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
* **macOS/Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Requirements
Install requirements using pip:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` into a new file named `.env`:
```bash
cp .env.example .env
```
Inside `.env`, configure your parameters:
* `SECRET_KEY`: Set your secret key.
* `DEBUG`: Set to `True` for development.
* `GEMINI_API_KEY`: *(Optional)* Enter your Google Gemini API key to activate the live LLM chatbot. If left blank, Spark AI automatically switches to the offline rule-based expert fallback mode.

### 5. Run Database Migrations
Compile database schema tables for catalog products and order invoices:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin Account)
Create a superuser to access the Django admin panel:
```bash
python manage.py createsuperuser
```
Follow the interactive prompts to set a username, email, and password.

### 7. Run the Server
Start Django's built-in local development server:
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Unit Tests

To run automated checks verifying models, slugs, price reductions, and stock helper parameters:
```bash
python manage.py test
```

---

## 👤 Admin Dashboard

To add categories, upload images, update prices, or adjust order tracking states, log in to:
`http://127.0.0.1:8000/admin/`

---

## ⚕️ Sports Nutrition Disclaimer

Spark AI offers general coaching, conditioning, and sports nutrition meal recommendations. All meal plan templates and diet tips are for educational guidance only. Spark Sports is not a registered healthcare provider. Users with special dietary requirements, food allergies, or medical conditions should consult a qualified doctor or clinical dietitian.
