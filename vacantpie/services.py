from vacantpie.models import Employee_Event, Employee, DepartmentEmployee

def create_new_employee_event(from_date, to_date, user_id, color, status_color_range):
    employee_event = Employee_Event.objects.create_employee_event(from_date, to_date, user_id)
    if employee_event is not None:
        return employee_event.get_event_as_own(color, status_color_range).__dict__
    return None


def cancel_employee_event(event_id, user_id):
    item = Employee_Event.objects.get(id=event_id)
    if item.employee.user.pk == user_id:
        item.delete()
        return True
    return False


def change_status_vacation_request(event_id, user_id, color, option, status_color_range):
    current_employee = Employee.objects.get(user_id=user_id)
    item = Employee_Event.objects.get(id=event_id)
    if not DepartmentEmployee.objects.check_user_approver(item.employee.user.id, user_id):
        return None
    item.change_status(current_employee, option)
    return item.get_event(color, status_color_range).__dict__


def change_disabled(event_id, change):
    if Employee_Event.objects.get(id=event_id).approval_status == change:
        return "disabled"
    return ""


def change_vacation_request(event_id, color, status_color_range, to_type_id=0, start="", end=""):
    item = Employee_Event.objects.get(id=event_id)
    item.update(to_type_id=to_type_id, start=start, end=end)
    return item.get_event_as_own(color, status_color_range).__dict__


def get_vacation_details_for_user(event_id):
    return Employee_Event.objects.get(id=event_id).get_user_event_details().__dict__
