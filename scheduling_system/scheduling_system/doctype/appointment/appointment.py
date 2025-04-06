import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, add_to_date


class Appointment(Document):
    def validate(self):
        self.validate_required_fields()
        self.set_end_date()
        self.validate_time_order()
        self.check_seller_conflict()

    def validate_required_fields(self):
        missing = []

        # Verifica campos obrigatórios
        if not self.seller:
            missing.append("Seller")
        if not self.start_date:
            missing.append("Satart date")
        if not self.duration:
            missing.append("Duration")

        if missing:
            frappe.throw("Required fields not filled in: " + ", ".join(missing))

        try:
            hours, minutes, seconds = map(int, str(self.duration).split(":"))
            if hours == 0 and minutes == 0 and seconds == 0:
                frappe.throw("The duration cannot be zero.")
        except Exception:
            frappe.throw("Duration format invalid. Use HH:MM:SS.")

    def set_end_date(self):
        self.start_date = get_datetime(self.start_date)
        hours, minutes, seconds = map(int, str(self.duration).split(":"))
        self.end_date = add_to_date(self.start_date, hours=hours, minutes=minutes, seconds=seconds)

    def validate_time_order(self):
        if self.start_date >= self.end_date:
            frappe.throw("The start date must be earlier than the end date.")

    def check_seller_conflict(self):
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
            self.end_date,
            self.start_date
        ), as_dict=True)


        if conflicts:
            conflict_list = [
                f"{c.client_name}: {get_datetime(c.start_date).strftime('%d/%m/%Y %H:%M')} until {get_datetime(c.end_date).strftime('%H:%M')}"
                for c in conflicts
            ]
            frappe.throw(
                "Time conflict! The seller already has commitment(s): \n\n" + "\n".join(conflict_list)
            )

