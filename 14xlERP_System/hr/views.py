from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count
from datetime import datetime
from .models import (
    Employee, Department, Position, LeaveType, LeaveRequest, Attendance,
    EmployeeAdvance, PerformanceReview, Training, EmployeeTraining,
    Recruitment, JobApplication, OrganizationStructure
)
from .forms import (
    EmployeeForm, DepartmentForm, PositionForm, LeaveRequestForm,
    AttendanceForm, EmployeeAdvanceForm, PerformanceReviewForm,
    RecruitmentForm, JobApplicationForm
)


@login_required
def hr_dashboard(request):
    """HR dashboard overview"""
    tenant = request.user.profile.tenant if hasattr(request.user, 'profile') else None
    
    context = {
        'total_employees': Employee.objects.filter(tenant=tenant).count() if tenant else 0,
        'active_employees': Employee.objects.filter(tenant=tenant, employment_status='active').count() if tenant else 0,
        'departments': Department.objects.filter(tenant=tenant).count() if tenant else 0,
        'pending_leave_requests': LeaveRequest.objects.filter(tenant=tenant, status='pending').count() if tenant else 0,
        'open_positions': Recruitment.objects.filter(tenant=tenant, status='open').count() if tenant else 0,
        'pending_applications': JobApplication.objects.filter(tenant=tenant, status='submitted').count() if tenant else 0,
        'active_trainings': Training.objects.filter(tenant=tenant, status='ongoing').count() if tenant else 0,
    }
    return render(request, 'hr/dashboard.html', context)


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'hr/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return Employee.objects.filter(tenant=tenant).select_related('department', 'position')
        return Employee.objects.none()


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'hr/employee_detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leave_requests'] = self.object.leave_requests.all()[:5]
        context['performance_reviews'] = self.object.performance_reviews.all()[:5]
        context['advances'] = self.object.advances.all()[:5]
        return context


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        messages.success(self.request, 'Employee created successfully!')
        return super().form_valid(form)


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')

    def form_valid(self, form):
        messages.success(self.request, 'Employee updated successfully!')
        return super().form_valid(form)


class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'hr/department_list.html'
    context_object_name = 'departments'
    paginate_by = 10

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return Department.objects.filter(tenant=tenant)
        return Department.objects.none()


class DepartmentCreateView(LoginRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        messages.success(self.request, 'Department created successfully!')
        return super().form_valid(form)


class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully!')
        return super().form_valid(form)


class LeaveRequestListView(LoginRequiredMixin, ListView):
    model = LeaveRequest
    template_name = 'hr/leave_request_list.html'
    context_object_name = 'requests'
    paginate_by = 10

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return LeaveRequest.objects.filter(tenant=tenant).order_by('-created_at')
        return LeaveRequest.objects.none()


class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'hr/leave_request_form.html'
    success_url = reverse_lazy('hr:leave_request_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        form.instance.employee = self.request.user.employee_profile
        messages.success(self.request, 'Leave request submitted successfully!')
        return super().form_valid(form)


@login_required
def approve_leave_request(request, pk):
    """Approve a leave request"""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        leave_request.status = 'approved'
        leave_request.approved_by = request.user
        leave_request.approval_date = datetime.now()
        leave_request.save()
        messages.success(request, 'Leave request approved!')
        return redirect('hr:leave_request_list')
    return render(request, 'hr/approve_leave.html', {'leave_request': leave_request})


@login_required
def reject_leave_request(request, pk):
    """Reject a leave request"""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        leave_request.status = 'rejected'
        leave_request.rejection_reason = request.POST.get('rejection_reason', '')
        leave_request.save()
        messages.success(request, 'Leave request rejected!')
        return redirect('hr:leave_request_list')
    return render(request, 'hr/reject_leave.html', {'leave_request': leave_request})


class AttendanceListView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'hr/attendance_list.html'
    context_object_name = 'attendance_records'
    paginate_by = 20

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return Attendance.objects.filter(tenant=tenant).order_by('-date')
        return Attendance.objects.none()


class AttendanceCreateView(LoginRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'hr/attendance_form.html'
    success_url = reverse_lazy('hr:attendance_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        messages.success(self.request, 'Attendance record created successfully!')
        return super().form_valid(form)


class EmployeeAdvanceListView(LoginRequiredMixin, ListView):
    model = EmployeeAdvance
    template_name = 'hr/advance_list.html'
    context_object_name = 'advances'
    paginate_by = 10

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return EmployeeAdvance.objects.filter(tenant=tenant).order_by('-created_at')
        return EmployeeAdvance.objects.none()


class EmployeeAdvanceCreateView(LoginRequiredMixin, CreateView):
    model = EmployeeAdvance
    form_class = EmployeeAdvanceForm
    template_name = 'hr/advance_form.html'
    success_url = reverse_lazy('hr:advance_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        form.instance.employee = self.request.user.employee_profile
        messages.success(self.request, 'Advance request submitted successfully!')
        return super().form_valid(form)


@login_required
def approve_advance(request, pk):
    """Approve an employee advance"""
    advance = get_object_or_404(EmployeeAdvance, pk=pk)
    if request.method == 'POST':
        advance.status = 'approved'
        advance.approved_by = request.user
        advance.approval_date = datetime.now()
        advance.save()
        messages.success(request, 'Advance approved!')
        return redirect('hr:advance_list')
    return render(request, 'hr/approve_advance.html', {'advance': advance})


class RecruitmentListView(LoginRequiredMixin, ListView):
    model = Recruitment
    template_name = 'hr/recruitment_list.html'
    context_object_name = 'openings'
    paginate_by = 10

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return Recruitment.objects.filter(tenant=tenant).order_by('-posted_date')
        return Recruitment.objects.none()


class RecruitmentCreateView(LoginRequiredMixin, CreateView):
    model = Recruitment
    form_class = RecruitmentForm
    template_name = 'hr/recruitment_form.html'
    success_url = reverse_lazy('hr:recruitment_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        messages.success(self.request, 'Job opening created successfully!')
        return super().form_valid(form)


class JobApplicationListView(LoginRequiredMixin, ListView):
    model = JobApplication
    template_name = 'hr/job_application_list.html'
    context_object_name = 'applications'
    paginate_by = 20

    def get_queryset(self):
        tenant = self.request.user.profile.tenant if hasattr(self.request.user, 'profile') else None
        if tenant:
            return JobApplication.objects.filter(tenant=tenant).order_by('-applied_date')
        return JobApplication.objects.none()


class JobApplicationDetailView(LoginRequiredMixin, DetailView):
    model = JobApplication
    template_name = 'hr/job_application_detail.html'
    context_object_name = 'application'
