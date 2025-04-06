frappe.views.calendar["Appointment"] = {
    field_map: {
        start: "start_date",
        end: "end_date",
        id: "name",
        title: "client_name",
        allDay: false,
    },
    gantt: false,
    get_events_method: "frappe.desk.calendar.get_events"
};
