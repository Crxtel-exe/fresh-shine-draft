# 🧽 SparkleClean PH — Cleaning Services Booking App (Demo Build)

A full-stack cleaning services booking web application built with **React (Vite)** and **Python + Flask**.

> ⚠️ **This is the DEMO build — there is NO database.**
> There is no SQLite file, no SQLAlchemy, no migrations and no seed script to run.
> Everything (users, services, bookings, reviews, site content) is held **in memory**
> in `backend/store.py` and **resets when the server restarts**. That is intentional:
> you can start the app and use it straight away with no setup step at all.

- **Frontend:** React 18, Vite, React Router, Context API (auth + theme), Axios
- **Backend:** Python + Flask, bcrypt password hashing, JWT auth, **in-memory data store**
- **Location:** Restricted to **Pampanga** (municipality + barangay picker)
- **Booking rule:** Only **1 booking per day** — unless a customer pays a **downpayment** to secure the date (first downpayment, first served)

---

## 🚀 Quick Start

**No database step. Nothing to create, migrate or seed.**

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm

### 1. Backend (Flask)

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server (port 5000)
python app.py
```

That is the whole backend setup. The sample data is seeded automatically on startup.

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser. The Vite dev server proxies `/api` requests to the Flask backend on port 5000.

---

## 🔑 Sample Accounts (ready to use)

Two accounts are created automatically on startup, so you can sign in **without signing up first**.
The credentials are also shown on the **Login page** (click a row to fill the form in).

| Role         | Email                        | Password      | Notes                                                        |
|--------------|------------------------------|---------------|--------------------------------------------------------------|
| **Customer** | `customer@sparkleclean.ph`   | `customer123` | Already has sample bookings — one completed and one pending — plus a review. |
| **Admin**    | `admin@sparkleclean.ph`      | `admin123`    | Company owner. Can manage bookings, services, reviews and site content. |

You can also log in with a **cellphone number** instead of an email:

| Role         | Cellphone number |
|--------------|------------------|
| Customer     | `09171234567`    |
| Admin        | `09170000000`    |

> These are demo credentials and are shown openly on purpose. They are defined at the top of `backend/store.py`.

### What the sample customer can do right away
- **My Bookings** — two sample bookings are already there (one **completed** and paid, one **pending**).
- **Reviews** — the completed booking can be rated, and there is already a seeded review with an admin reply.
- **Booking** — tick several services, see the live price, and book a new date.

---

## ✨ Features

### Authentication
- Login with **email OR cellphone number** + password
- Signup: first name, last name, phone, email, password, confirm password, **Pampanga location picker** (municipality + barangay), terms & conditions checkbox
- **Forgot password** flow (token-based reset)
- **Logout** invalidates the token server-side (kept in an in-memory blocklist)

### Roles
- **User** (regular customer)
- **Admin** (company owner) — admin cannot see Book / My Bookings as a user

### User Pages
1. **Home** — company name, description, past projects, services (placeholder content editable by admin).
2. **Booking** — calendar date picker (1 booking/day, downpayment secures), **checkboxes so the customer can pick several services at once**, location (auto-filled, editable), optional notes. A note tells the customer an admin will call to confirm the booking by paying a downpayment.
3. **My Bookings** — view past/ongoing bookings, all the services availed, statuses, **pay downpayment / pay in full**, **Contact Admin** button.
4. **Reviews** — rate a booking **once**, only if **completed**.
5. **Profile** — edit name, phone, email, password, profile picture.
6. **About Us** — company location, description, services, contacts (email, phone, Facebook, TikTok).

### Admin Pages
1. **Home** — same as user home but editable (company info, services, projects, images).
2. **Bookings** — all bookings, edit status & payment status, schedule date, the service(s) availed, **clickable location → Google Maps**, **Contact Customer** button.
3. **Services** — full CRUD for services: add/edit/delete a service (name, description, image, **price range**, **whether it is a house cleaning service**, and **pricing options**).
4. **Reviews** — reply to reviews.
5. **About Us** — edit all info.

### Admin Logout
- A **Logout** button appears in the navbar for admins (desktop and mobile menu).
- Clicking it calls `POST /api/admin/logout`, which **invalidates the admin's JWT server-side**, clears the local session, and redirects to the **login page**.
- After logout, the admin **cannot access any protected admin route** — the backend returns `401` and the frontend redirects to login.

### User (Customer) Logout
- A **Logout** button also appears in the navbar for **regular logged-in users** (desktop and mobile menu).
- Clicking it calls `POST /api/auth/logout`, which invalidates the user's JWT server-side, clears the local session, and redirects to the **login page**.

### Services & Configurable Pricing
- Each service has a **price range** (`min_price` – `max_price`), shown on the Home and Booking pages (e.g. "₱1,500 – ₱5,000").
- The admin can toggle which **pricing options** apply to a service and set their rates:
  - **Base price** (₱)
  - **Price per square meter** (₱/sqm)
  - **Price per room** (₱/room)
  - **Price per story/floor** (₱/floor)
  - **Price per hour** (₱/hr)
- Each service is also flagged as either a **house cleaning service** or a **non-house service** (`is_house_service`). This flag decides whether the Booking page asks for house details.
- On the **Booking** page the app computes a **live estimated price**. Each selected service is priced on its own (base price + its enabled options, clamped to its own min–max range) and the results are **added together**, so the total updates as services are ticked and options change. The estimate is stored on the booking and shown in **My Bookings**.

### Booking: Multiple Services + Conditional House Details
- On the **Booking** page the customer ticks a **checkbox for every service they want** — several can be selected for a single booking. The ticked services are listed in a **Selected Services** panel (each with a **Remove** link), and all of them are saved on the booking.
- The **house details fields — area (sqm), number of rooms, and number of stories/floors — are only shown and only required when at least one house cleaning service is ticked.**
  - If the customer ticks only non-house services (for example **Couch Cleaning**), those fields are **hidden, not required, and not stored** on the booking. A short note explains why.
  - Services priced per hour (couch, mattress, carpet, window cleaning) instead offer an optional **Estimated Duration (hours)** field.
  - The form reacts live: ticking the first house service reveals the details, and unticking the last one hides them again.
- Each service card carries a small tag — **🏠 House details required** or **🚫 No house details needed** — so the customer can tell at a glance.
- The backend enforces the same rule: a booking containing a house service returns **400** if the house details are missing, while a booking made up only of non-house services succeeds with those values left empty.
- Seeded services: four house cleaning services (Home Deep Cleaning, Office Cleaning, Move-in / Move-out, Post-Construction) and four non-house ones (Couch Cleaning, Mattress Cleaning, Carpet Cleaning, Window & Glass Cleaning). The admin can change any service's flag on the **Services** page.

### Company Contact Details (the "Contact Admin" button)
- The **Contact Admin** button on **My Bookings** opens a small pop-up showing **only the company's phone number, email address, and Facebook account** — nothing else.
- These details live in **one obvious place**: **`frontend/src/config/companyContact.js`**.
- **To change them, edit the three values in that file:**
  ```js
  export const COMPANY_CONTACT = {
    phone: '0917 123 4567',            // <-- EDIT THIS LINE: company phone number
    email: 'hello@sparkleclean.ph',    // <-- EDIT THIS LINE: company email address
    facebook: 'facebook.com/sparklecleanph',  // <-- EDIT THIS LINE: company Facebook page
  }
  ```
  The comment block at the top of the file says exactly which lines to edit. Change only the text inside the quotes — do not rename the keys. The pop-up builds its rows from this object, so the change appears everywhere the button is used. A value left empty is simply skipped.

### Contact Customer (the admin's button)
- On **Admin → Bookings**, the **Contact Customer** button on each row opens a pop-up showing **the customer's email address and contact number only**.
- This reads straight from the booking record, so there is nothing to configure. If a customer has no email or phone on file, that row is skipped.

### Theme
- Light mode: `#F2FFF6` / `#CAFFDE` / `#25C5E9` / `#238689`
- Dark mode: `#021225`
- Toggle in the navbar (persisted in localStorage).

### Photo Upload (real file upload)
- Photos are uploaded as **actual files** from the user's device (file picker), not by pasting a URL.
- A reusable **ImageUpload** component is used on the **Profile** page (profile picture), the **Admin → Services** page (service image), and the **Admin → Home** page (service + project images).
- Selecting a file uploads it to `POST /api/upload` (multipart), which saves it to `backend/uploads/` and returns a URL like `/uploads/<filename>`.
- Uploaded files are served statically at `/uploads/<filename>` (the Vite dev server proxies `/uploads` to the backend).
- **Validation:** only image files are accepted (JPG, PNG, GIF, WEBP, SVG, BMP) and the maximum size is **5 MB**.

> Note: the image **files** are still written to disk in `backend/uploads/`. That is the only thing this demo build writes — there is still no database.

### Mobile Responsiveness
- Fully responsive on mobile and tablet (all pages).
- **Hamburger menu** on small screens — nav links collapse into a slide-down drawer; desktop keeps the horizontal nav.
- Forms, cards, grids, and the calendar scale down for small screens (verified at 375px).

---

## 🗃 How the data works (no database)

All state lives in **`backend/store.py`**, an in-memory store seeded on startup:

| In-memory "table" | Seeded with |
|-------------------|-------------|
| `users` | The **sample admin** and **sample customer** accounts |
| `services` | 8 cleaning services (4 house + 4 non-house) |
| `bookings` | 2 sample bookings for the customer (one completed, one pending) |
| `reviews` | 1 sample review with an admin reply |
| `site_content` | Company name, tagline, description, about, contacts |
| `projects` | 3 sample past projects |
| `password_resets` / `token_blocklist` | Used by forgot-password and logout |

**Every value resets to these defaults when the backend restarts.** There is nothing to clean up and no data to lose — just restart to get a fresh demo. If you need to reset mid-session, delete a booking or edit freely: a restart always brings it back to the state above.

---

## 📁 Project Structure

```
cleaning-booking/
├── backend/
│   ├── app.py            # Flask app entry point (registers blueprints, seeds the store)
│   ├── store.py          # THE IN-MEMORY DATA STORE + sample accounts + seed content
│   ├── helpers.py        # Serializers, validation, auth decorators
│   ├── notifications.py  # Email (SMTP) + SMS notification helpers
│   ├── pampanga.py       # Pampanga municipalities & barangays
│   ├── .env.example      # Notification config template (SMTP + SMS)
│   ├── requirements.txt  # No database driver needed
│   ├── test_demo_store.py       # Tests: sample accounts + no-database checks
│   ├── test_booking_services.py # Tests: multi-service booking + house details
│   ├── test_notifications.py    # Tests: email/SMS helpers
│   ├── uploads/          # Uploaded images (the only thing written to disk)
│   └── routes/           # Route blueprints (one file per domain)
│       ├── auth.py       # signup, login, me, forgot/reset password
│       ├── profile.py    # update profile, change password
│       ├── bookings.py   # my bookings, availability, create, payments
│       ├── reviews.py    # public reviews, create review
│       ├── admin.py      # admin bookings, reviews, site, services, projects
│       ├── upload.py     # multipart image upload (POST /api/upload)
│       └── site.py       # public site content + demo accounts + pampanga data
└── frontend/
    ├── index.html
    ├── vite.config.js    # /api proxy → localhost:5000
    ├── public/
    │   └── sparkle.svg
    └── src/
        ├── main.jsx
        ├── App.jsx       # Routes + role protection
        ├── api.js        # Axios instance (JWT interceptor)
        ├── index.css     # Theme (light/dark) + all styles
        ├── config/
        │   └── companyContact.js  # COMPANY PHONE / EMAIL / FACEBOOK  <-- EDIT HERE
        ├── context/
        │   ├── AuthContext.jsx
        │   └── ThemeContext.jsx
        ├── hooks/
        │   └── useApi.js # Shared data-fetching hook (loading/error/reload)
        ├── components/
        │   ├── Navbar.jsx
        │   ├── Footer.jsx
        │   ├── ContactModal.jsx     # reusable contact pop-up (customer + admin)
        │   ├── DemoAccounts.jsx     # sample-account hint on the Login page
        │   ├── ProtectedRoute.jsx   # auth guard
        │   ├── AdminRoute.jsx       # admin guard
        │   ├── PampangaPicker.jsx   # reusable location picker
        │   ├── StarRating.jsx       # reusable star rating (input + display)
        │   └── Badge.jsx            # reusable status badge
        └── pages/
            ├── Home.jsx, Booking.jsx, MyBookings.jsx,
            ├── Reviews.jsx, Profile.jsx, About.jsx,
            ├── Login.jsx, Signup.jsx, ForgotPassword.jsx
            └── admin/
                ├── AdminHome.jsx, AdminBookings.jsx,
                ├── AdminReviews.jsx, AdminServices.jsx, AdminAbout.jsx
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register a user |
| POST | `/api/auth/login` | Login (email or phone) |
| GET | `/api/auth/me` | Current user |
| POST | `/api/auth/logout` | Log out the current user (invalidates JWT) |
| POST | `/api/auth/forgot` | Request password reset |
| POST | `/api/auth/reset-password` | Reset password with token |
| GET | `/api/site` | Public site content, services, projects |
| GET | `/api/demo-accounts` | The sample account credentials shown on the Login page |
| GET | `/api/pampanga` | Pampanga municipalities & barangays |
| GET | `/api/bookings` | My bookings (each includes `service_ids` / `service_names`) |
| GET | `/api/bookings/availability` | Date availability |
| POST | `/api/bookings` | Create booking — takes `service_ids` (an array, one or many) and `service_id` for older clients; house details required only when a house service is included |
| POST | `/api/bookings/:id/downpayment` | Pay downpayment |
| POST | `/api/bookings/:id/payfull` | Pay in full |
| GET | `/api/reviews` | Public reviews |
| POST | `/api/reviews` | Create review (completed booking, once) |
| POST | `/api/upload` | Upload an image file (multipart, auth required) |
| PUT | `/api/profile` | Update profile |
| PUT | `/api/profile/password` | Change password |
| GET | `/api/admin/bookings` | All bookings (admin) |
| PUT | `/api/admin/bookings/:id` | Update booking (admin) |
| GET | `/api/admin/reviews` | All reviews (admin) |
| PUT | `/api/admin/reviews/:id` | Reply to review (admin) |
| PUT | `/api/admin/site` | Update site content (admin) |
| POST | `/api/admin/services` | Add a service (admin) |
| PUT | `/api/admin/services/:id` | Update a service (admin) |
| DELETE | `/api/admin/services/:id` | Delete a service (admin) |
| POST/PUT/DELETE | `/api/admin/projects` | Manage projects (admin) |

---

## 🧪 Tests

The test scripts talk to a **running backend** (start it first, as above):

```bash
cd backend
source venv/bin/activate     # if not already active

python test_demo_store.py        # sample accounts, and proof there is no database
python test_booking_services.py  # multi-service bookings + conditional house details
python test_notifications.py     # email/SMS helpers (no server needed)
```

`test_notifications.py` imports the helper functions directly, so it needs no server running.

---

## 📧 Optional: Configure Email & SMS Notifications

The app sends a **confirmation email + SMS** when a booking is created, and a
**status-update email + SMS** when an admin changes a booking's status.

**No configuration is required to run locally** — if SMTP/SMS are not set up,
the app simply logs the messages instead of sending them, so nothing breaks.

To enable real notifications, copy `backend/.env.example` to `backend/.env`
and fill in your credentials:

```bash
cd backend
cp .env.example .env
```

#### Email (SMTP)

| Variable     | Description                          | Example                    |
|--------------|--------------------------------------|----------------------------|
| `SMTP_HOST`  | SMTP server host                     | `smtp.gmail.com`           |
| `SMTP_PORT`  | SMTP port (587 = TLS, 465 = SSL)     | `587`                      |
| `SMTP_USER`  | SMTP username / email                | `you@gmail.com`            |
| `SMTP_PASS`  | SMTP password / app password         | `your-app-password`        |
| `MAIL_FROM`  | "From" address shown to recipients   | `SparkleClean PH <you@gmail.com>` |

> For Gmail, enable 2-Step Verification and create an **App Password** — your
> normal Gmail password will not work for SMTP.

#### SMS

| Variable            | Purpose                                        | Example |
|---------------------|------------------------------------------------|---------|
| `SMS_PROVIDER`      | `twilio` or `generic`                          | `twilio` |
| `SMS_API_KEY`       | API key for the provider                       | `your-api-key` |
| `SMS_SENDER`        | Sender name / ID                               | `SparkleClean` |
| `SMS_GATEWAY_URL`   | Endpoint for `generic` HTTP gateways           | `https://sms.example.com/send` |
| `TWILIO_ACCOUNT_SID`| Twilio account SID (only for `twilio`)         | `ACxxxxxxxx` |
| `TWILIO_AUTH_TOKEN` | Twilio auth token (only for `twilio`)          | `your-token` |
| `TWILIO_FROM`       | Twilio phone number (only for `twilio`)        | `+15017122661` |

- **`SMS_PROVIDER=twilio`** → uses the Twilio REST API.
- **`SMS_PROVIDER=generic`** → calls `SMS_GATEWAY_URL` with query params
  `to`, `message`, `sender`, and `api_key` (adapt to your gateway).

---

## 🧠 Booking Conflict Logic

- A date can have **only one booking** by default.
- If a date is already booked, a new user can still book it **only by paying a downpayment** — the first customer to pay the downpayment **secures** the date.
- The calendar shows: 🔴 already booked (needs downpayment to secure), 🟡 secured by another customer.

---

## 🛠 Troubleshooting

- **Port 5000 in use** → change the port in `app.py` and update the proxy in `frontend/vite.config.js`.
- **CORS errors** → Flask-CORS is already enabled; ensure the frontend runs on port 5173.
- **Data looks odd after testing** → just restart the backend. All data is in memory and re-seeds on startup, so a restart gives you a clean demo.
- **The sample-account hint is missing on the Login page** → the backend is not reachable. Start it and refresh.

---

## 📝 Changing Your Contact Information

Your company details (phone, email, Facebook) are in **one file**:

**`frontend/src/config/companyContact.js`**

```js
export const COMPANY_CONTACT = {
  phone: '0917 123 4567',            // <-- EDIT THIS LINE: company phone number
  email: 'hello@sparkleclean.ph',    // <-- EDIT THIS LINE: company email address
  facebook: 'facebook.com/sparklecleanph',  // <-- EDIT THIS LINE: company Facebook page
}
```

Edit the values inside the quotes on those three lines, save, and the **Contact Admin** button on My Bookings will show your new details. The comment block at the top of that file says exactly which lines to edit. To add or remove a detail, edit the `companyContactRows()` function just below the object.

> ⚠️ A backslash or missing quote will break the build — keep the quotes balanced.

---

*Demo build — no database, no persistence. Data is held in memory and resets on restart.*


## Code-managed website content

The admin panel is intentionally limited to customer operations. Services, prices,
descriptions, homepage project content, company information, homepage images, and
the logo are managed manually in the source code.

- Edit services and pricing in `backend/store.py` under `DEFAULT_SERVICES`.
- Edit homepage projects in `backend/store.py` under `DEFAULT_PROJECTS`.
- Edit company/site information in `backend/store.py` under `DEFAULT_SITE`.
- Put homepage images in `frontend/public/` and set the corresponding `image` path
  in `DEFAULT_SERVICES` or `DEFAULT_PROJECTS`.
- Replace `frontend/public/sparkle.png` to change the logo, or change its path in
  `frontend/src/components/Navbar.jsx`.

The admin panel no longer has service/site/project add, edit, delete, or image-upload
controls. Profile photo upload remains available to customers.

## Reviews

A customer can submit at most one review for each completed booking. After a review
is submitted, that completed booking is removed from the customer's review selector.
The backend also rejects another review for the same booking, so the rule is enforced
even if a client attempts to bypass the UI.
