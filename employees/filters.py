import django_filters

from .models import Attendance, Employee, LeaveRequest


class EmployeeFilter(django_filters.FilterSet):
    min_salary = django_filters.NumberFilter(field_name="salary", lookup_expr="gte")
    max_salary = django_filters.NumberFilter(field_name="salary", lookup_expr="lte")
    joined_after = django_filters.DateFilter(field_name="date_of_joining", lookup_expr="gte")
    joined_before = django_filters.DateFilter(field_name="date_of_joining", lookup_expr="lte")
    department = django_filters.CharFilter(field_name="department__name", lookup_expr="iexact")

    class Meta:
        model = Employee
        fields = ["status", "department", "designation", "min_salary", "max_salary"]


class LeaveRequestFilter(django_filters.FilterSet):
    employee = django_filters.UUIDFilter(field_name="employee__id")
    starts_after = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    ends_before = django_filters.DateFilter(field_name="end_date", lookup_expr="lte")

    class Meta:
        model = LeaveRequest
        fields = ["status", "leave_type", "employee", "starts_after", "ends_before"]


class AttendanceFilter(django_filters.FilterSet):
    employee = django_filters.UUIDFilter(field_name="employee__id")
    date_after = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_before = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Attendance
        fields = ["status", "employee", "date_after", "date_before"]
