from django.contrib import admin

from vacantpie.models import Leave_Category, Department, Employee, Day_Type, DepartmentEmployee, \
    Leave_Category_Max_Day_Type


class Leave_Category_Max_Day_Type_Inline(admin.TabularInline):
    model=Leave_Category_Max_Day_Type
    extra=1

class Leave_Category_Admin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name','description']}),
    ]
    inlines=[Leave_Category_Max_Day_Type_Inline]
    list_display = ['name']


class Department_Inline(admin.TabularInline):
    model=Department
    extra=1

class DepartmentEmployee_Inline(admin.TabularInline):
    model=DepartmentEmployee
    extra =1

class Day_Type_Inline(admin.TabularInline):
    model=Day_Type
    extra =1

class EmployeeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['leave_category','user']}),
    ]
    inlines=[DepartmentEmployee_Inline]
    list_display = ['user']

admin.site.register(Leave_Category, Leave_Category_Admin)
admin.site.register(Department)
admin.site.register(Employee,EmployeeAdmin)
admin.site.register(Day_Type)
