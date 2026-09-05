from datetime import date

from rest_framework import serializers

from .models import Attendance, Department, Employee, LeaveRequest


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_code",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone_number",
            "department",
            "department_name",
            "designation",
            "salary",
            "date_of_joining",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "employee_code", "created_at", "updated_at"]

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("First name cannot be blank.")
        return value.strip().title()

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Last name cannot be blank.")
        return value.strip().title()

    def validate_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Salary must be greater than zero.")
        return value

    def validate_date_of_joining(self, value):
        if value > date.today():
            raise serializers.ValidationError("Date of joining cannot be in the future.")
        return value

    def validate_email(self, value):
        qs = Employee.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("An employee with this email already exists.")
        return value.lower()


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    days_requested = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
            "status",
            "days_requested",
            "applied_at",
            "reviewed_at",
            "review_comment",
        ]
        read_only_fields = [
            "id",
            "status",
            "applied_at",
            "reviewed_at",
            "review_comment",
        ]

    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_date": "End date cannot be before start date."}
            )
        if start and start < date.today() and not self.instance:
            raise serializers.ValidationError(
                {"start_date": "Cannot apply for leave starting in the past."}
            )
        return attrs


class LeaveReviewSerializer(serializers.Serializer):
    """Used only by the approve/reject actions — not a full leave representation."""

    comment = serializers.CharField(required=False, allow_blank=True, max_length=255)


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",
            "employee",
            "employee_name",
            "date",
            "check_in",
            "check_out",
            "status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        check_in = attrs.get("check_in", getattr(self.instance, "check_in", None))
        check_out = attrs.get("check_out", getattr(self.instance, "check_out", None))
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError(
                {"check_out": "Check-out time must be after check-in time."}
            )
        return attrs

    def validate_date(self, value):
        if value > date.today():
            raise serializers.ValidationError("Attendance date cannot be in the future.")
        return value
