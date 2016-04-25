from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
import datetime

from django.db.models import Sum, Count

from vacantpie.utils import format_date
from . import myworkday


class Event:
    def __init__(self, id=None, color="", borderColor="", textColor="", title="", start="", end="", editable=True,
                 startEditable=True):
        self.id = id
        self.color = color
        self.borderColor = borderColor
        self.textColor = textColor
        self.allDay = True
        self.title = title
        self.start = start
        self.end = end
        self.editable = editable
        self.startEditable = startEditable


class User_Events_Summary:
    def __init__(self):
        self.asked_vacation_days = []
        self.approved_vacation_days = []
        self.declined_vacation_days = []


class UserEventDetails:
    def __init__(self):
        self.eventStartDate = ""
        self.eventEndDate = ""
        self.eventLapseDays = 0
        self.eventTypeName = ""
        self.eventTypeDescription = ""
        self.eventTypeMarker = ""
        self.eventStatus = "N/A"
        self.eventStatusBy = ""
        self.eventStatusDate = ""
        self.eventUserName = ""
        self.useLeaveCategory = ""
        self.userLeaveCategoryDescription = ""
        self.userLeaveLimits=None
        self.userVacationsSummary = None


class Leave_Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name + " " + self.description

    class Meta:
        verbose_name = "Leave Category"
        verbose_name_plural = "Leave Categories"


class DayManager(models.Manager):
    def get_free_days(self, from_date, to_date, color):
        return list(map(lambda x: x.get_event(color).__dict__,
                        self.filter(day_date__range=[from_date, to_date], is_workday=False)))


class Day(models.Model):
    is_workday = models.BooleanField()
    day_date = models.DateField()

    def get_event(self, color):
        return Event(color=color,
                     title="non working day", start=format_date(self.day_date),
                     end=format_date(self.day_date), editable=False, startEditable=False)

    objects=DayManager()


class Day_Type(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    marker = models.CharField(max_length=8)
    is_default=models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Day Type"
        verbose_name_plural = "Day Types"


class Leave_Category_Max_Day_Type(models.Model):
    leave_category = models.ForeignKey(Leave_Category, on_delete=models.CASCADE)
    day_type = models.ForeignKey(Day_Type, on_delete=models.CASCADE)
    max_days = models.IntegerField(default=365)


class Employee(models.Model):
    user = models.OneToOneField(User)
    leave_category = models.ForeignKey(Leave_Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.employee_name

    @property
    def employee_name(self):
        full_name = self.user.first_name + " " + self.user.last_name
        if full_name == " ":
            return self.user.username
        return self.user.first_name + " " + self.user.last_name

    def get_max_days_for_day_type(self,day_type_id):
        return Leave_Category_Max_Day_Type.objects.get(leave_category__id=self.leave_category.pk,day_type__id=day_type_id).max_days


class Department(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class DepartmentEmployeeManager(models.Manager):
    def check_user_approver(self, user_id, approver_user_id):
        return (self.filter(employee__user_id=user_id,
                            department__id__in=self.filter(
                                employee__user_id=approver_user_id,
                                is_approver=True).values_list("department_id",
                                                              flat=True)).aggregate(
            deps=Count('id'))[
                    'deps'] > 0)

    def get_all_colleagues(self, user_id):
        reps_departments = self.filter(employee__user__id=user_id, is_approver=True).values_list(
            "department_id", flat=True)
        return self.filter(~Q(employee__user_id=user_id),
                           department__id__in=reps_departments).values_list(
            "employee_id", flat=True)


class DepartmentEmployee(models.Model):
    is_approver = models.BooleanField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    objects = DepartmentEmployeeManager()


class Employee_Event_Manager(models.Manager):
    def get_summary_by_employee(self, user_id):
        summary = User_Events_Summary()
        summary.asked_vacation_days = list(
            self.filter(employee__user_id=user_id, approved=False, declined=False).values(
                'event_Type__id', 'event_Type__name').annotate(days=Sum('lapse_days')))
        summary.approved_vacation_days = list(
            self.filter(employee__user_id=user_id, approved=True, declined=False).values(
                'event_Type__id',
                'event_Type__name').annotate(
                days=Sum('lapse_days')))
        summary.declined_vacation_days = list(
            self.filter(employee__user_id=user_id, approved=False, declined=True).values(
                'event_Type__id',
                'event_Type__name').annotate(
                days=Sum('lapse_days')))
        return summary

    def get_used_days_for_day_type(self, day_type_id, user_id):
        used_days=self.filter(employee__user_id=user_id, event_Type__id=day_type_id).aggregate(days=Sum('lapse_days'))['days']
        if used_days is None:
            return 0
        return used_days

    def create_employee_event(self, start_day, end_day, user_id):
        if self.check_overlapped_events_for_user(start_day, end_day, user_id):
            return None

        dstart_day = datetime.datetime.strptime(start_day, '%Y-%m-%d').date()
        dend_day = datetime.datetime.strptime(end_day, '%Y-%m-%d').date()
        emp = Employee.objects.get(user__id=user_id)
        daytype = Day_Type.objects.get(is_default=True)
        queryset = Day.objects.filter(day_date__range=[start_day, end_day], is_workday=False).dates("day_date", "day")
        lapse_days = myworkday.networkdays(dstart_day, dend_day, queryset, weekends=(6, 7))
        if lapse_days == 0 or lapse_days>emp.get_max_days_for_day_type(daytype.pk)-self.get_used_days_for_day_type(daytype.pk,user_id):
            return None
        employee_event = Employee_Event()
        employee_event.event_Type = daytype
        employee_event.start_day = dstart_day
        employee_event.employee = emp
        employee_event.lapse_days = lapse_days
        employee_event.end_day = dend_day
        employee_event.save()
        return employee_event

    def check_overlapped_events_for_user(self, start_day, end_day, user_id, event_id=0):
        if start_day == "" or end_day == "":
            return False
        if event_id == 0:
            return (self.filter(((Q(start_day__lte=start_day) & Q(end_day__gte=start_day)) | (
                Q(start_day__lte=end_day) & (Q(end_day__gte=end_day)))) | (Q(start_day__range=[start_day, end_day]) | Q(
                end_day__range=[start_day, end_day])), employee__user__id=user_id).aggregate(overlapped=Count('id'))[
                        'overlapped'] > 0)
        return (self.filter((((Q(start_day__lte=start_day) & Q(end_day__gte=start_day)) | (
            Q(start_day__lte=end_day) & (Q(end_day__gte=end_day)))) | (Q(start_day__range=[start_day, end_day]) | Q(
            end_day__range=[start_day, end_day]))) & ~Q(id=event_id), employee__user__id=user_id).aggregate(
            overlapped=Count('id'))[
                    'overlapped'] > 0)

    def get_reporting_employees_days(self, from_date, to_date, user_id):
        return self.filter(
            Q(start_day__range=[from_date, to_date]) | Q(end_day__range=[from_date, to_date]),
            employee__id__in=DepartmentEmployee.objects.get_all_colleagues(user_id)).order_by("employee_id")

    def check_event_for_user(self, event_id, user_id):
        return (self.filter(id=event_id, employee__user_id=user_id).aggregate(
            evs=Count('id'))['evs'] == 0)

    def get_own_days(self, from_date, to_date, user_id, color, status_color_range):
        return list(map(
            lambda x: x.get_event_as_own(color, status_color_range).__dict__,
            self.filter(
                Q(start_day__range=[from_date, to_date]) | Q(end_day__range=[from_date, to_date]),
                employee__user__id=user_id)))

    def get_reports_days(self, from_date, to_date, user_id, status_color_range, reports_color_range):
        reports_days = []
        try:
            queryset = self.get_reporting_employees_days(from_date, to_date, user_id)
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


class Employee_Event(models.Model):
    start_day = models.DateField()
    end_day = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee')
    event_Type = models.ForeignKey(Day_Type, on_delete=models.CASCADE)
    lapse_days = models.IntegerField()
    approved = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Employee, blank=True, related_name='approver', null=True)
    declined_by = models.ForeignKey(Employee, blank=True, related_name='decliner', null=True)
    approved_date = models.DateField(blank=True, null=True)
    declined_date = models.DateField(blank=True, null=True)

    def update(self, to_type_id=0, start="", end=""):
        if Employee_Event.objects.check_overlapped_events_for_user(start, end, self.employee.user.id, self.pk):
            return
        if int(to_type_id) > 0:
            new_event_Type = Day_Type.objects.get(id=to_type_id)
        else:
            new_event_Type=self.event_Type
        if not start == "":
            d_start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
        else:
            d_start = self.start_day
        if not end == "":
            d_end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
        else:
            d_end = self.end_day
        queryset = Day.objects.filter(day_date__range=[format_date(d_start), format_date(d_end)],
                                      is_workday=False).dates("day_date", "day")
        lapse_days = myworkday.networkdays(d_start, d_end, queryset, weekends=(6, 7))
        if lapse_days is not None:
            if lapse_days-self.lapse_days<=self.employee.get_max_days_for_day_type(new_event_Type.pk)-Employee_Event.objects.get_used_days_for_day_type(new_event_Type.pk,self.employee.user.id):
                self.start_day=d_start
                self.end_day=d_end
                self.event_Type=new_event_Type
                self.lapse_days=lapse_days
        else:
            self.event_Type=new_event_Type
        self.save()

    def change_status(self, status_changer_employee, option):
        if option == 'approve':
            self.approved = True
            self.declined = False
            self.approved_by = status_changer_employee
            self.approved_date = datetime.date.today()
            self.declined_by = None
            self.declined_date = None
        elif option == 'decline':
            self.declined = True
            self.approved = False
            self.approved_by = None
            self.approved_date = None
            self.declined_by = status_changer_employee
            self.declined_date = datetime.date.today()
        self.save()

    def get_user_event_details(self):
        user_event_details = UserEventDetails()
        user_event_details.eventStartDate = format_date(self.start_day)
        user_event_details.eventEndDate = format_date(self.end_day)
        user_event_details.eventLapseDays = self.lapse_days
        user_event_details.eventTypeName = self.event_Type.name
        user_event_details.eventTypeDescription = self.event_Type.description
        user_event_details.eventTypeMarker = self.event_Type.marker
        user_event_details.eventStatus = self.approval_status_name
        user_event_details.eventStatusBy = self.approval_status_by
        status_date = self.approval_status_date
        if status_date is None:
            user_event_details.eventStatusDate = ""
        else:
            user_event_details.eventStatusDate = format_date(status_date)
        user_event_details.eventUserName = self.employee.employee_name
        user_event_details.useLeaveCategory = self.employee.leave_category.name
        user_event_details.userLeaveCategoryDescription = self.employee.leave_category.description
        user_event_details.userLeaveLimits=list(Leave_Category_Max_Day_Type.objects.filter(leave_category__id=self.employee.leave_category.id).values("day_type__name","max_days"))
        user_event_details.userVacationsSummary = Employee_Event.objects.get_summary_by_employee(
            self.employee.user.id).__dict__
        return user_event_details

    def get_event_as_own(self, color, status_color_range):
        return Event(id=self.id, color=color,
                     textColor=status_color_range[self.approval_status],
                     borderColor=self.event_Type.marker,
                     title=self.own_event_title,
                     start=format_date(self.start_day),
                     end=format_date(self.end_day))

    def get_event(self, color, status_color_range):
        return Event(id=self.id, color=color, borderColor=self.event_Type.marker,
                     textColor=status_color_range[self.approval_status],
                     title=self.event_title, start=format_date(self.start_day), end=format_date(self.end_day),
                     editable=False,
                     startEditable=False)

    @property
    def approval_status(self):
        if self.approved:
            return 1
        if self.declined:
            return 2
        return 0

    @property
    def event_title(self):
        if self.approval_status == 0:
            return self.employee.user.username + " asked for " + str(
                self.lapse_days) + " days as " + self.event_Type.name
        if self.approval_status == 1:
            return self.employee.user.username + " has " + str(self.lapse_days) + " days as " + self.event_Type.name
        if self.approval_status == 2:
            return self.employee.user.username + " has unapproved " + str(
                self.lapse_days) + " days as " + self.event_Type.name

    @property
    def own_event_title(self):
        if self.approval_status == 0:
            return "Asked for " + str(
                self.lapse_days) + " days as " + self.event_Type.name
        if self.approval_status == 1:
            return "Have " + str(self.lapse_days) + " days as " + self.event_Type.name
        if self.approval_status == 2:
            return "Got unapproved " + str(
                self.lapse_days) + " days as " + self.event_Type.name

    approval_status_titles = ['N/A', 'approved', 'declined']

    @property
    def approval_status_name(self):
        return self.approval_status_titles[self.approval_status]

    @property
    def approval_status_by(self):
        if self.approval_status == 1:
            return self.approved_by.employee_name
        if self.approval_status == 2:
            return self.declined_by.employee_name
        return "N/A"

    @property
    def approval_status_date(self):
        if self.approval_status == 1:
            return self.approved_date
        if self.approval_status == 2:
            return self.declined_date
        return None

    objects = Employee_Event_Manager()
