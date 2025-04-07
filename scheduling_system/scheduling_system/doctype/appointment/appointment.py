import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, add_to_date

class Appointment(Document):
    def validate(self):
        self.set_end_date()
        self.check_seller_conflict()


    def set_end_date(self):
        self.start_date = get_datetime(self.start_date)
        try:
            parts = list(map(int, self.duration.split(":")))
            hours = parts[0]
            minutes = parts[1] if len(parts) > 1 else 0
            seconds = parts[2] if len(parts) > 2 else 0
            self.end_date = add_to_date(self.start_date, hours=hours, minutes=minutes, seconds=seconds)
        except Exception as e:
            frappe.throw(f"Error interpreting duration (expected format HH:MM:SS): {e}")


    def check_seller_conflict(self):
        if not self.seller or not self.start_date or not self.end_date:
            frappe.throw("Missing required information to check for scheduling conflicts.")
        try:
            start = get_datetime(self.start_date)
            end = get_datetime(self.end_date)
        except Exception as e:
            frappe.throw(f"Error converting dates: {e}")
        conflicts = frappe.db.sql("""
            SELECT name, client_name, start_date, end_date
            FROM `tabAppointment`
            WHERE 
                seller = %s
                AND name != %s
                AND status != 'Canceled'
                AND (
                    start_date < %s AND end_date > %s
                )
        """, (
            self.seller,
            self.name or "New Appointment",
            end,
            start
        ), as_dict=True)
        if conflicts:
            conflict_list = [
                f"{c.client_name}: {get_datetime(c.start_date).strftime('%d/%m/%Y %H:%M')} to {get_datetime(c.end_date).strftime('%H:%M')}"
                for c in conflicts
            ]
            frappe.throw(
                f"Schedule conflict! The seller already has the following appointment(s):\n\n" + "\n".join(conflict_list)
            )

