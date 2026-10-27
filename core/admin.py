from django.contrib import admin
from .models import Item, Claim, MatchNotification

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'category', 'location', 'reported_by', 'is_resolved', 'created_at')
    list_filter = ('report_type', 'category', 'is_resolved')
    search_fields = ('name', 'location', 'description', 'reported_by__username')

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('item', 'claimant', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(MatchNotification)
class MatchNotificationAdmin(admin.ModelAdmin):
    list_display = ('lost_item', 'found_item', 'recipient_email', 'match_score', 'email_sent', 'email_sent_at')
    list_filter = ('email_sent', 'created_at')
    search_fields = ('lost_item__name', 'found_item__name', 'recipient_email')
    readonly_fields = ('lost_item', 'found_item', 'recipient_email', 'match_score', 'email_sent', 'email_sent_at', 'created_at')
