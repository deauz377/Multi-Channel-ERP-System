from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # Dashboard
    path('', views.hr_dashboard, name='dashboard'),
    
    # Employees
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_edit'),
    
    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_edit'),
    
    # Leave Management
    path('leave-requests/', views.LeaveRequestListView.as_view(), name='leave_request_list'),
    path('leave-requests/create/', views.LeaveRequestCreateView.as_view(), name='leave_request_create'),
    path('leave-requests/<int:pk>/approve/', views.approve_leave_request, name='approve_leave_request'),
    path('leave-requests/<int:pk>/reject/', views.reject_leave_request, name='reject_leave_request'),
    
    # Attendance
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    
    # Employee Advances
    path('advances/', views.EmployeeAdvanceListView.as_view(), name='advance_list'),
    path('advances/create/', views.EmployeeAdvanceCreateView.as_view(), name='advance_create'),
    path('advances/<int:pk>/approve/', views.approve_advance, name='approve_advance'),
    
    # Recruitment
    path('recruitment/', views.RecruitmentListView.as_view(), name='recruitment_list'),
    path('recruitment/create/', views.RecruitmentCreateView.as_view(), name='recruitment_create'),
    
    # Job Applications
    path('applications/', views.JobApplicationListView.as_view(), name='job_application_list'),
    path('applications/<int:pk>/', views.JobApplicationDetailView.as_view(), name='job_application_detail'),
]
