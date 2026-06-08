from django.contrib import admin
from .models import Member, Contribution, Loan, LoanPayment


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'join_date', 'is_active']
    list_filter = ['is_active', 'join_date']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['join_date']


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ['member', 'amount', 'date', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['member__name', 'description']
    readonly_fields = ['created_at']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['id', 'member', 'principal', 'interest', 'status', 'due_date', 'created_at']
    list_filter = ['status', 'created_at', 'due_date']
    search_fields = ['member__name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Loan Information', {
            'fields': ('member', 'principal', 'interest', 'due_date', 'status')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LoanPayment)
class LoanPaymentAdmin(admin.ModelAdmin):
    list_display = ['loan', 'amount', 'payment_date', 'created_at']
    list_filter = ['payment_date', 'created_at']
    search_fields = ['loan__id', 'loan__member__name']
    readonly_fields = ['created_at']
