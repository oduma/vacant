from django.db.models import Q

from vacantpie.models import Day, Employee_Event, Employee, DepartmentEmployee


def get_free_days(from_date, to_date, color):
    return list(map(lambda x: x.get_event(color).__dict__,
                    Day.objects.filter(day_date__range=[from_date, to_date], is_workday=False)))


def get_own_days(from_date, to_date, user_id, color, status_color_range):
    return list(map(
        lambda x: x.get_event_as_own(color, status_color_range).__dict__,
        Employee_Event.objects.filter(
            Q(start_day__range=[from_date, to_date]) | Q(end_day__range=[from_date, to_date]),
            employee__user__id=user_id)))


def get_reports_days(from_date, to_date, user_id, status_color_range, reports_color_range):
    reports_days = []
    try:
        queryset = Employee_Event.objects.get_reporting_employees_days(from_date, to_date, user_id)
    except:
        return reports_days
    color_index = 0
    current_employee_id = 0
    for item in queryset:
        if not current_employee_id == item.employee.pk:
            color_index += 1
            if color_index >= 2:
                color_index = 0
            current_employee_id = item.employee.pk
        reports_days.append(item.get_event(reports_color_range[color_index], status_color_range).__dict__)

    return reports_days


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
