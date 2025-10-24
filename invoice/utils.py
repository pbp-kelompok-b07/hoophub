import datetime
def generate_invoice_no(user_id: int) -> str:
    now = datetime.datetime.now()
    return f"INV{now:%Y%m%d}-{user_id}-{now:%H%M%S%f}"[:32]