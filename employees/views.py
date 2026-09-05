from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import AttendanceFilter, EmployeeFilter, LeaveRequestFilter
from .models import Attendance, Department, Employee, LeaveRequest
from .pagination import StandardResultsPagination
from .serializers import (
    AttendanceSerializer,
    DepartmentSerializer,
    EmployeeSerializer,
    LeaveRequestSerializer,
    LeaveReviewSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    CRUD API for employees.

    Supports:
      - search: ?search=john
      - filtering: ?status=ACTIVE&department=Engineering&min_salary=30000
      - ordering: ?ordering=-salary
      - pagination: ?page=2&page_size=20
    """

    queryset = Employee.objects.select_related("department").all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = EmployeeFilter
    search_fields = [
        "first_name",
        "last_name",
        "email",
        "employee_code",
        "designation",
        "department__name",
    ]
    ordering_fields = ["first_name", "last_name", "salary", "date_of_joining", "created_at"]
    ordering = ["-created_at"]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    CRUD + approval workflow for employee leave requests.

    Supports:
      - filtering: ?status=PENDING&leave_type=SICK&employee=<uuid>
      - date range: ?starts_after=2024-01-01&ends_before=2024-12-31
      - ordering: ?ordering=-applied_at
      - custom actions: POST /api/leave-requests/{id}/approve/ and /reject/
    """

    queryset = LeaveRequest.objects.select_related("employee").all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = LeaveRequestFilter
    ordering_fields = ["applied_at", "start_date", "end_date"]
    ordering = ["-applied_at"]

    def _review(self, request, new_status):
        leave = self.get_object()
        if leave.status != LeaveRequest.Status.PENDING:
            return Response(
                {"detail": f"This leave request is already {leave.status.lower()}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        review_serializer = LeaveReviewSerializer(data=request.data)
        review_serializer.is_valid(raise_exception=True)

        leave.status = new_status
        leave.reviewed_at = timezone.now()
        leave.review_comment = review_serializer.validated_data.get("comment", "")
        leave.save(update_fields=["status", "reviewed_at", "review_comment"])
        return Response(LeaveRequestSerializer(leave).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """POST /api/leave-requests/{id}/approve/  body (optional): {"comment": "..."}"""
        return self._review(request, LeaveRequest.Status.APPROVED)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """POST /api/leave-requests/{id}/reject/  body (optional): {"comment": "..."}"""
        return self._review(request, LeaveRequest.Status.REJECTED)


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    CRUD API for daily attendance records.

    Supports:
      - filtering: ?status=PRESENT&employee=<uuid>&date_after=2024-01-01&date_before=2024-01-31
      - ordering: ?ordering=-date
    One record per employee per day (enforced at the database level).
    """

    queryset = Attendance.objects.select_related("employee").all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AttendanceFilter
    ordering_fields = ["date", "created_at"]
    ordering = ["-date"]
