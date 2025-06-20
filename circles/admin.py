from django.contrib import admin
from .models import Circle, Contribution, Claim, Membership

class MembershipInline(admin.TabularInline):  # or admin.StackedInline
    model = Membership
    extra = 1

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'balance', 'frequency', 'member_count']
    inlines = [MembershipInline]
    
    def member_count(self, obj):
        return obj.members.count()

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'circle', 'is_active', 'payment_warnings', 'last_contribution_date']
    list_filter = ['is_active', 'circle']
    search_fields = ['user__username']
    # Add filter_horizontal here if you want it for the user/circle selection when creating memberships
    # filter_horizontal = ['user']  # If your Membership model has a M2M field

@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ['user', 'circle', 'amount', 'timestamp', 'is_automatic', 'refunded']
    list_filter = ['circle', 'is_automatic', 'refunded']

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['user', 'circle', 'amount', 'status', 'fraud_risk', 'created_at']
    list_filter = ['status', 'circle']
    readonly_fields = ['processed_at']

    def fraud_risk(self, obj):
        if obj.amount > 3000:
            return "⚠️ High"
        elif Claim.objects.filter(user=obj.user).count() > 2:
            return "⚠️ Frequent Claimer"
        return "Low"