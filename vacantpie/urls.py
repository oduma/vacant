from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /vacantpie/
    url(r'^$', views.CalendarView.as_view(), name='index'),
    url(r'^getEvents/$',views.days,name='getEvents'),
    url(r'^AskForVacation/$',views.ask_for_vacation,name='AskForVacation'),
    url(r'^CancelVacation/$', views.cancel_vacation, name='CancelVacation'),
    url(r'^ApproveVacation/$', views.handle_vacation_request, name='ApproveVacation'),
    url(r'^OptionsForEvent/$', views.get_options_for_event, name='OptionsForEvent'),
    url(r'^ChangeVacationType/$', views.change_vacation_type, name='ChangeVacationType'),
    url(r'^VacationDetails/$', views.get_vacation_details, name='VacationDetails'),
    url(r'^UpdateVacation/$', views.update_vacation_request, name='UpdateVacation'),

]