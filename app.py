from __future__ import annotations

import csv
import io
from pathlib import Path

import streamlit as st


PROJECT_DIR = Path(__file__).parent
PRICES_FILE = PROJECT_DIR / "prices.txt"
SEAT_COUNT = 20


def load_prices() -> dict[str, float]:
    prices: dict[str, float] = {}
    with PRICES_FILE.open(encoding="utf-8", newline="") as price_file:
        for row in csv.reader(price_file):
            if len(row) == 2:
                prices[row[0].strip()] = float(row[1])
    return prices


def make_csv(bookings: list[dict[str, str | int | float]]) -> str:
    output = io.StringIO()
    fields = ["seat", "customer", "ticket_type", "price"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(bookings)
    return output.getvalue()


def select_seat(seat_number: int) -> None:
    st.session_state.selected_seat = seat_number


def confirm_booking(prices: dict[str, float]) -> None:
    selected_seat = st.session_state.get("selected_seat")
    customer_name = st.session_state.get("customer_name", "").strip()
    ticket_type = st.session_state.get("ticket_type", next(iter(prices)))
    bookings = st.session_state.bookings

    if selected_seat is None:
        st.session_state.booking_notice = ("warning", "Choose an available seat first.")
    elif not customer_name:
        st.session_state.booking_notice = ("warning", "Enter a customer name to finish the booking.")
    elif any(int(booking["seat"]) == selected_seat for booking in bookings):
        st.session_state.booking_notice = ("warning", "That seat is no longer available. Choose another seat.")
    else:
        bookings.append(
            {
                "seat": selected_seat,
                "customer": customer_name,
                "ticket_type": ticket_type,
                "price": prices[ticket_type],
            }
        )
        st.session_state.selected_seat = None
        st.session_state.booking_notice = ("success", f"Seat {selected_seat:02d} booked for {customer_name}.")


def reset_session() -> None:
    st.session_state.bookings = []
    st.session_state.selected_seat = None


st.set_page_config(page_title="Ticket Desk", page_icon="🎟️", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --ink: #171a18;
        --paper: #f4f3ed;
        --lime: #d7f36a;
        --coral: #e66c4e;
        --muted: #767a72;
    }
    [data-testid="stAppViewContainer"] { background: var(--paper); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
    .eyebrow { color: var(--coral); font-size: .75rem; font-weight: 800; letter-spacing: .12em; }
    .hero-title { font-size: 2.8rem; line-height: 1.02; font-weight: 850; margin: .35rem 0 .45rem; }
    .hero-copy { color: var(--muted); font-size: 1rem; margin-bottom: 1.4rem; }
    .screen-label {
        background: var(--ink); color: var(--lime); border-radius: 3px;
        padding: .5rem; text-align: center; font-size: .72rem; font-weight: 800;
        letter-spacing: .15em; margin: .4rem 0 1.2rem;
    }
    div.stButton > button { border-radius: 4px; min-height: 2.8rem; font-weight: 750; }
    div.stButton > button[kind="primary"] { background: var(--coral); border-color: var(--coral); }
    div[data-testid="stMetric"] { background: #fff; padding: .85rem 1rem; border-left: 3px solid var(--lime); }
    @media (max-width: 700px) {
        .hero-title { font-size: 2.25rem; }
        .block-container { padding: 1.2rem 1rem 2rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    prices = load_prices()
except (OSError, ValueError, csv.Error) as error:
    st.error(f"Could not read ticket prices from {PRICES_FILE.name}: {error}")
    st.stop()

if not prices:
    st.error("No ticket prices were found in prices.txt.")
    st.stop()

st.session_state.setdefault("bookings", [])
st.session_state.setdefault("selected_seat", None)
bookings: list[dict[str, str | int | float]] = st.session_state.bookings
booked_seats = {int(booking["seat"]) for booking in bookings}
available_seats = [seat for seat in range(1, SEAT_COUNT + 1) if seat not in booked_seats]
revenue = sum(float(booking["price"]) for booking in bookings)
booking_notice = st.session_state.pop("booking_notice", None)

st.markdown('<div class="eyebrow">BOX OFFICE / LIVE SESSION</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Ticket Desk</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-copy">A simple seat map and box-office ledger, powered by your project ticket prices.</div>',
    unsafe_allow_html=True,
)

metric_columns = st.columns(3)
metric_columns[0].metric("Available", len(available_seats), f"of {SEAT_COUNT} seats")
metric_columns[1].metric("Booked", len(bookings), "this session")
metric_columns[2].metric("Ticket revenue", f"${revenue:,.2f}", "this session")
if booking_notice:
    notice_type, notice_message = booking_notice
    getattr(st, notice_type)(notice_message)

st.divider()
map_column, booking_column = st.columns([1.2, 0.8], gap="large")

with map_column:
    st.subheader("Choose a seat")
    st.markdown('<div class="screen-label">SCREEN</div>', unsafe_allow_html=True)
    for row in range(4):
        seat_columns = st.columns(5, gap="small")
        for column_index, seat_column in enumerate(seat_columns):
            seat_number = row * 5 + column_index + 1
            is_booked = seat_number in booked_seats
            label = f"{seat_number:02d}  ✓" if is_booked else f"{seat_number:02d}"
            seat_column.button(
                label,
                key=f"seat-{seat_number}",
                disabled=is_booked,
                type="primary" if st.session_state.selected_seat == seat_number else "secondary",
                width="stretch",
                on_click=select_seat,
                args=(seat_number,),
            )
    st.caption("Select an open seat. Checked seats are already booked.")

with booking_column:
    st.subheader("New booking")
    selected_seat = st.session_state.selected_seat
    st.text_input(
        "Selected seat",
        value=f"Seat {selected_seat:02d}" if selected_seat else "Choose a seat from the map",
        disabled=True,
    )
    st.text_input("Customer name", placeholder="Name for the booking", key="customer_name")
    ticket_type = st.selectbox("Ticket type", options=list(prices), key="ticket_type")
    ticket_price = prices[ticket_type]
    st.markdown(f"**Price**  ·  ${ticket_price:,.2f}")

    st.button(
        "Confirm booking",
        type="primary",
        width="stretch",
        on_click=confirm_booking,
        args=(prices,),
    )

st.divider()
history_column, export_column = st.columns([0.75, 0.25], vertical_alignment="bottom")
with history_column:
    st.subheader("Session bookings")
with export_column:
    if bookings:
        st.download_button(
            "Download CSV",
            data=make_csv(bookings),
            file_name="ticket_bookings.csv",
            mime="text/csv",
            width="stretch",
        )

if bookings:
    st.dataframe(
        [
            {
                "Seat": f"{booking['seat']:02d}",
                "Customer": booking["customer"],
                "Ticket": booking["ticket_type"],
                "Price": f"${float(booking['price']):,.2f}",
            }
            for booking in bookings
        ],
        hide_index=True,
        width="stretch",
    )
else:
    st.caption("Bookings will appear here after you reserve a seat.")

with st.sidebar:
    st.subheader("Ticket prices")
    for label, amount in prices.items():
        st.write(f"{label}  ·  ${amount:,.2f}")
    st.divider()
    st.button("Reset this session", width="stretch", on_click=reset_session)