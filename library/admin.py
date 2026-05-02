from django.contrib import admin
from django.utils.html import format_html
from .models import Book, CustomUser


# =========================================================
# 📚 BOOK ADMIN
# =========================================================
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):

    list_display = ("title", "subject", "level", "created_at")
    list_filter = ("subject", "level")
    search_fields = ("title",)
    ordering = ("-created_at",)


# =========================================================
# 👤 CUSTOM USER ADMIN (PRO DASHBOARD STYLE)
# =========================================================
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):

    list_display = (
        "username",
        "email",
        "status_badge",
        "is_verified",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "status",
        "is_verified",
        "is_active",
        "is_staff",
    )

    search_fields = ("username", "email")

    ordering = ("-id",)

    actions = ["approve_users", "reject_users", "reset_to_pending"]

    # =========================================================
    # 🎨 STATUS BADGE (PRO UI)
    # =========================================================
    def status_badge(self, obj):

        colors = {
            "approved": "#28a745",  # green
            "pending": "#ffc107",   # yellow
            "rejected": "#dc3545",  # red
        }

        color = colors.get(obj.status, "#6c757d")

        return format_html(
            '<span style="padding:4px 10px;border-radius:12px;'
            'color:white;font-weight:bold;background:{};">{}</span>',
            color,
            obj.status.upper()
        )

    status_badge.short_description = "Status"

    # =========================================================
    # ⚡ BULK ACTIONS (ADMIN POWER TOOLS)
    # =========================================================
    def approve_users(self, request, queryset):
        queryset.update(status="approved")
    approve_users.short_description = "✅ Approve selected users"

    def reject_users(self, request, queryset):
        queryset.update(status="rejected")
    reject_users.short_description = "❌ Reject selected users"

    def reset_to_pending(self, request, queryset):
        queryset.update(status="pending")
    reset_to_pending.short_description = "🔄 Reset to pending"

    # =========================================================
    # 🔐 FIELD PROTECTION (IMPORTANT FIX)
    # =========================================================
    def get_fieldsets(self, request, obj=None):

        return (
            ("User Info", {
                "fields": ("username", "email", "password")
            }),
            ("Status & Permissions", {
                "fields": (
                    "status",
                    "is_verified",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            }),
            ("OTP Info", {
                "fields": ("otp_code", "otp_created_at")
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("password",)
        return ()