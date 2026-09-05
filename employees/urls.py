from rest_framework.routers import DefaultRouter

from .views import AttendanceViewSet, DepartmentViewSet, EmployeeViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"leave-requests", LeaveRequestViewSet, basename="leave-request")
router.register(r"attendance", AttendanceViewSet, basename="attendance")

urlpatterns = router.urls
