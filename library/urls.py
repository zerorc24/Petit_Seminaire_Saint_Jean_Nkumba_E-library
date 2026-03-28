from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("library/", views.library_list, name="library"),

    path("read/<int:pk>/", views.read_book, name="read_book"),

    path("book/add/", views.add_book, name="add_book"),
    path("book/edit/<int:pk>/", views.edit_book, name="edit_book"),
    path("book/delete/<int:pk>/", views.delete_book, name="delete_book"),

    path("books/bulk-upload/", views.bulk_upload_books, name="bulk_upload_books"),

]