import uuid

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Department(models.Model):
    """Department an employee belongs to."""

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    """Core employee record."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        ON_LEAVE = "ON_LEAVE", "On Leave"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_code = models.CharField(max_length=20, unique=True, editable=False)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="employees"
    )
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(0)]
    )
    date_of_joining = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["employee_code"]),
            models.Index(fields=["status"]),
        ]

    def save(self, *args, **kwargs):
        if not self.employee_code:
            self.employee_code = f"EMP{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_code} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class LeaveRequest(models.Model):
    """A leave application submitted by an employee, subject to approval."""

    class LeaveType(models.TextChoices):
        SICK = "SICK", "Sick Leave"
        CASUAL = "CASUAL", "Casual Leave"
        EARNED = "EARNED", "Earned Leave"
        UNPAID = "UNPAID", "Unpaid Leave"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="leave_requests"
    )
    leave_type = models.CharField(max_length=10, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_comment = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-applied_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["employee", "status"]),
        ]

    def __str__(self):
        return f"{self.employee.employee_code} — {self.leave_type} ({self.status})"

    @property
    def days_requested(self):
        return (self.end_date - self.start_date).days + 1


class Attendance(models.Model):
    """A single day's attendance record for an employee."""

    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        HALF_DAY = "HALF_DAY", "Half Day"
        ON_LEAVE = "ON_LEAVE", "On Leave"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name="attendance_records"
    )
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    notes = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ("employee", "date")
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["employee", "date"]),
        ]

    def __str__(self):
        return f"{self.employee.employee_code} — {self.date} ({self.status})"
