from django.contrib import admin

from .models import Attendance, Department, Employee, LeaveRequest

admin.site.site_header = "Employee Management"
admin.site.site_title = "Employee Management Admin"
admin.site.index_title = "HR Administration"


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "department",
        "designation",
        "status",
        "salary",
        "date_of_joining",
    ]
    list_filter = ["status", "department"]
    search_fields = ["first_name", "last_name", "email", "employee_code"]
    date_hierarchy = "date_of_joining"
    list_per_page = 25


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = [
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "applied_at",
    ]
    list_filter = ["status", "leave_type"]
    search_fields = ["employee__first_name", "employee__last_name", "employee__employee_code"]
    date_hierarchy = "applied_at"
    actions = ["approve_selected", "reject_selected"]

    @admin.action(description="Approve selected leave requests")
    def approve_selected(self, request, queryset):
        from django.utils import timezone

        updated = queryset.filter(status=LeaveRequest.Status.PENDING).update(
            status=LeaveRequest.Status.APPROVED, reviewed_at=timezone.now()
        )
        self.message_user(request, f"{updated} leave request(s) approved.")

    @admin.action(description="Reject selected leave requests")
    def reject_selected(self, request, queryset):
        from django.utils import timezone

        updated = queryset.filter(status=LeaveRequest.Status.PENDING).update(
            status=LeaveRequest.Status.REJECTED, reviewed_at=timezone.now()
        )
        self.message_user(request, f"{updated} leave request(s) rejected.")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["employee", "date", "check_in", "check_out", "status"]
    list_filter = ["status"]
    search_fields = ["employee__first_name", "employee__last_name", "employee__employee_code"]
    date_hierarchy = "date"
    list_per_page = 25
