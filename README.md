# Python-2026

Python samples and a Streamlit ticket-booking app built from the seat-selection exercise.

## Ticket Desk

The app reads ticket types and prices from `prices.txt`, provides 20 interactive seats, tracks bookings and session revenue, and lets you download the booking list as a CSV.

Bookings are kept in Streamlit session state, so they reset when the app session restarts. The app does not change the original exercise files.

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

### Deploy to Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) with the GitHub account that owns this repository.
2. Select **Create app** and choose `AidanHerrera1/my_python_final_fa26` on the `main` branch.
3. Set the app file path to `app.py`, then deploy.

The app uses only `requirements.txt` and the checked-in `prices.txt`; no secrets or additional configuration are required.
