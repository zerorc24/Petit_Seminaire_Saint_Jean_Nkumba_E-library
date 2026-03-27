from django.urls import path
from library import views

urlpatterns = [
    path("", views.home, name="home"),                  # <-- homepage
    path("library/", views.library_list, name="library"), # library list moved to /library/
    path("dashboard/", views.dashboard, name="dashboard"),
    path("bulk-upload/", views.bulk_upload_books, name="bulk_upload_books"),
    path("book/read/<int:pk>/", views.read_book, name="read_book"),
    path("book/add/", views.add_book, name="add_book"),
    path("book/edit/<int:pk>/", views.edit_book, name="edit_book"),
    path("book/delete/<int:pk>/", views.delete_book, name="delete_book"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]