import os
from django.conf import settings

DEFAULT_SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

DEFAULT_HEADER = [
    "ID",
    "Дата",
    "Время",
    "Имя",
    "Телефон",
    "Email",
    "Уровень",
    "Площадь (м²)",
    "Комнаты",
    "Санузлы",
    "Цена",
    "Адрес",
    "Комментарий",
    "Желаемая дата",
    "Желаемое время",
    "Скидка (%)",
    "Статус",
]

SHEET_NAME = getattr(settings, "GOOGLE_SHEETS_NAME", "Заявки YourClean")
CREDENTIALS_PATH = getattr(
    settings,
    "GOOGLE_SHEETS_CREDENTIALS_PATH",
    os.path.join(settings.BASE_DIR, "credentials.json"),
)


def append_to_google_sheet(order):
    """Append order data into a Google Sheet using a service account."""

    try:
        import gspread
        from gspread.exceptions import APIError, SpreadsheetNotFound
        from oauth2client.service_account import ServiceAccountCredentials
    except ImportError:
        print("Google Sheets libraries not installed (gspread, oauth2client). Skipping.")
        return

    if not os.path.exists(CREDENTIALS_PATH):
        print(f"Credentials file not found at {CREDENTIALS_PATH}. Skipping Google Sheets.")
        return

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, DEFAULT_SCOPE)
        client = gspread.authorize(creds)

        try:
            sheet = client.open(SHEET_NAME).sheet1
        except SpreadsheetNotFound:
            print(f"Spreadsheet '{SHEET_NAME}' not found. Creating one...")
            sheet = _create_sheet(client, creds)

        _ensure_header(sheet)
        sheet.append_row(_build_row(order), value_input_option="USER_ENTERED")
        print(f"Order #{order.id} appended to Google Sheet '{SHEET_NAME}'.")

    except Exception as exc:
        print(f"Error in append_to_google_sheet: {exc}")


def _create_sheet(client, creds):
    """Create the spreadsheet if it doesn't exist and return the first worksheet."""
    sh = client.create(SHEET_NAME)
    sh.share(creds.service_account_email, perm_type="user", role="owner")
    sheet = sh.sheet1
    sheet.append_row(DEFAULT_HEADER)
    return sheet


def _ensure_header(sheet):
    """Make sure the first row contains the header before appending data."""
    try:
        header = sheet.row_values(1)
    except Exception as exc:  # pragma: no cover - defensive logging only
        print(f"Failed to read header row: {exc}")
        header = []

    if not header:
        sheet.append_row(DEFAULT_HEADER)


def _build_row(order):
    """Convert an Order instance to a list matching DEFAULT_HEADER order."""
    def _format_date(value, fmt):
        return value.strftime(fmt) if value else ""

    return [
        order.id,
        _format_date(order.created_at, "%Y-%m-%d"),
        _format_date(order.created_at, "%H:%M"),
        order.name,
        order.phone,
        order.email or "",
        order.get_cleaning_level_display(),
        float(order.area) if order.area is not None else "",
        order.rooms,
        order.bathrooms,
        float(order.total_price) if order.total_price is not None else "",
        order.address or "",
        order.comment or "",
        _format_date(order.desired_date, "%Y-%m-%d"),
        _format_date(order.desired_time, "%H:%M"),
        order.applied_discount_percent,
        order.get_status_display(),
    ]
