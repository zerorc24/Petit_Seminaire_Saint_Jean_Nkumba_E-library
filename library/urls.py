from django.urls import path
from . import views

urlpatterns = [

    # =========================================================
    # 🏠 HOME
    # =========================================================
    path("", views.home, name="home"),


    # =========================================================
    # 🔐 AUTH SYSTEM
    # =========================================================
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),


    # =========================================================
    # 📧 OTP FLOW
    # =========================================================
    path("send-code-page/", views.send_code_page, name="send_code_page"),
    path("send-code/", views.send_verification_code, name="send_verification_code"),
    path("verify-code/", views.verify_code, name="verify_code"),


    # =========================================================
    # 📚 USER AREA
    # =========================================================
    path("library/", views.library, name="library"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("book/<int:pk>/", views.read_book, name="read_book"),


    # =========================================================
    # 🛠 BOOK MANAGEMENT (STAFF ONLY)
    # =========================================================
    path("add-book/", views.add_book, name="add_book"),
    path("edit-book/<int:pk>/", views.edit_book, name="edit_book"),
    path("delete-book/<int:pk>/", views.delete_book, name="delete_book"),
    path("bulk-upload/", views.bulk_upload_books, name="bulk_upload_books"),


    # =========================================================
    # 👨‍💼 ADMIN DASHBOARD (MAIN CONTROL SYSTEM)
    # =========================================================
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/", views.admin_dashboard, name="admin_panel"),


    # =========================================================
    # ⚙️ ADMIN ACTIONS (SAFE + CLEAN)
    # =========================================================
    path("admin-dashboard/approve/<int:user_id>/", views.approve_user, name="approve_user"),
    path("admin-dashboard/reject/<int:user_id>/", views.reject_user, name="reject_user"),
    path("reset-users/", views.reset_users, name="reset_users"),
]