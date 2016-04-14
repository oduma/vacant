import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from vacantpie.services import get_free_days, get_own_days, get_reports_days, create_new_employee_event, \
    cancel_employee_event, change_disabled, change_vacation_request, \
    get_vacation_details_for_user, change_status_vacation_request
from .models import Employee_Event, Employee, Day_Type


@method_decorator(login_required, name='dispatch')
class CalendarView(TemplateView):
    template_name = "vacantpie/index.html"
    model = Employee

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)
        context['username'] = Employee.objects.get(user__id=self.request.user.pk).user.username
        return context


@login_required
def days(request):
    events_list = get_free_days(request.GET['start'], request.GET['end'], '#ff0000')
    events_list.extend(get_own_days(request.GET['start'], request.GET['end'], request.user.pk, '#00ff00',
                                    ["#ffffff", "#00ff00", "#ff0000"]))
    events_list.extend(get_reports_days(request.GET['start'], request.GET['end'],
                                        request.user.pk,
                                        ["#ffffff", "#00ff00", "#ff0000"], ["#00ffcc", "#9966ff", "#ff99cc"]))
    return HttpResponse(json.dumps(events_list))


@login_required
def ask_for_vacation(request):
    return HttpResponse(json.dumps(create_new_employee_event(request.GET['start'], request.GET['end'], request.user.pk,
                                                             "#00ff00", ["#ffffff", "#00ff00", "#ff0000"])))


@login_required
def cancel_vacation(request):
    return HttpResponse(json.dumps(cancel_employee_event(request.GET['event_id'], request.user.pk)))


@login_required
def handle_vacation_request(request):
    return HttpResponse(json.dumps(
        change_status_vacation_request(request.GET['event_id'], request.user.pk, "#" + request.GET['color'],
                                request.GET['option'],
                                ["#ffffff", "#00ff00", "#ff0000"]
                                )))


@login_required
def get_options_for_event(request):
    if Employee_Event.objects.check_event_for_user(request.GET['event_id'], request.user.pk):
        return HttpResponse(json.dumps({"content": '<button ' + change_disabled(request.GET['event_id'],
                                                                                1) + ' onclick="handleVacationRequest(' +
                                                   request.GET[
                                                       'event_id'] + ",'" +
                                                   request.GET[
                                                       'color'] + "'" + ",'approve'" + ')">Approve</button>&nbsp;<button ' + change_disabled(
            request.GET['event_id'], 2) + 'onclick="handleVacationRequest(' +
                                                   request.GET['event_id'] + ",'" + request.GET[
                                                       'color'] + "'" + ",'decline'" + ')">Decline</button>'}))
    else:
        options = "<select onchange='changeType(" + request.GET['event_id'] + ", this)'>"
        evt = Employee_Event.objects.get(id=request.GET['event_id'])
        for day_Type in Day_Type.objects.all():
            if evt.event_Type.id == day_Type.id:
                options = options + '<option value="' + str(
                    day_Type.id) + '" selected="selected">' + day_Type.name + '</option>'
            else:
                options = options + '<option value="' + str(day_Type.id) + '">' + day_Type.name + '</option>'
        options += "</select>"
        return HttpResponse(json.dumps({"content": '<button onclick="cancelRequest(' + request.GET[
            'event_id'] + ',1)">Cancel Request</button>&nbsp;Change to:' + options}))


@login_required
def change_vacation_type(request):
    return HttpResponse(
        json.dumps(change_vacation_request(request.GET['event_id'], "#00ff00",
                                           ["#ffffff", "#00ff00", "#ff0000"], to_type_id=request.GET['to'])))


@login_required
def get_vacation_details(request):
    return HttpResponse(json.dumps(get_vacation_details_for_user(request.GET['event_id'])))


@login_required
def update_vacation_request(request):
    return HttpResponse(
        json.dumps(change_vacation_request(request.GET['event_id'], "#00ff00",
                                           ["#ffffff", "#00ff00", "#ff0000"]
                                           , start=request.GET['start'], end=request.GET['end'])))
