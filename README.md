
# QuickDrop

**QuickDrop** is a real-time, crowdsourced delivery platform that enables users to request and track deliveries on-demand or schedule them ahead of time. Built with Django and React, QuickDrop simplifies last-mile logistics with automation, real-time updates, and detailed earnings insights for delivery agents.

---

## Features

###  User Side
- Request on-demand or scheduled deliveries
- Live tracking of orders
- Real-time notifications and status updates
- Secure payment integration (e.g., Safaricom STK Push via Daraja API)
- Voucher system for accessing delivery services

### Courier Side
- Accept/reject delivery requests
- Navigate with real-time location updates
- View earnings summary (daily, weekly, monthly)
- Live status updates to customers
- Delivery performance dashboard

###  Admin Dashboard
- Overview cards for deliveries, earnings, and pending orders
- Interactive charts/graphs for insights
- Quick actions: Assign orders, update statuses
- Dark mode toggle
- Manage users, couriers, and delivery history

---

##  Technologies Used

- **Backend:** Django, Django REST Framework, Celery, Redis
- **Frontend:** React, TailwindCSS, Chart.js / Recharts
- **Database:** PostgreSQL
- **Authentication:** JWT / Django Auth
- **Payments:** Safaricom Daraja API
- **Others:** WebSockets (for live updates), Docker (optional)

---

##  Installation

### Backend (Django)

```bash
git clone https://github.com/occupyashanti/quickdrop.git
cd quickdrop/backend
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver