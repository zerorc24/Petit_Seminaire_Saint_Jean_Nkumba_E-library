from django.urls import path
from . import views

urlpatterns = [
    # ---------------- HOME ----------------
    path("", views.home, name="home"),

    # ---------------- AUTH ----------------
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # ---------------- OTP FLOW ----------------
    path("send-code/", views.send_code_page, name="send_code_page"),
    path("send-otp/", views.send_verification_code, name="send_verification_code"),
    path("verify/", views.verify_code, name="verify_code"),

    # ---------------- USER AREA ----------------
    path("library/", views.library, name="library"),
    path("dashboard/", views.dashboard, name="dashboard"),

    # ---------------- ADMIN ----------------
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("approve/<int:user_id>/", views.approve_user, name="approve_user"),
    path("reject/<int:user_id>/", views.reject_user, name="reject_user"),

    # ---------------- BOOK MANAGEMENT ----------------
    path("bulk-upload/",views.bulk_upload_books,name="bulk_upload_books"),
    path("add-book/", views.add_book, name="add_book"),
    path("edit-book/<int:pk>/", views.edit_book, name="edit_book"),
    path("delete-book/<int:pk>/", views.delete_book, name="delete_book"),
    path("read-book/<int:pk>/", views.read_book, name="read_book"),
]