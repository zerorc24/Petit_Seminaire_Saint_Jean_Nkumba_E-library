import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.paginator import Paginator
from django.http import HttpResponse

from .models import Book
from .forms import BookForm
from django.contrib.auth.models import User


# -------------------------------
# Helper decorators
# -------------------------------
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


# -------------------------------
# Homepage
# -------------------------------
def home(request):
    latest_books = Book.objects.order_by('-id')[:8]

    return render(request, "library/home.html", {
        "latest_books": latest_books
    })

# -------------------------------
# Auth Views
# -------------------------------
def login_view(request):
    next_url = request.GET.get("next", "home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        next_post = request.POST.get("next", "home")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if url_has_allowed_host_and_scheme(next_post, allowed_hosts={request.get_host()}):
                return redirect(next_post)

            return redirect("home")

        messages.error(request, "Invalid username or password")

    return render(request, "library/login.html", {"next": next_url})


def logout_view(request):
    logout(request)
    return redirect("login")


# -------------------------------
# TEMP: Create Admin (DELETE AFTER USE)
# -------------------------------
def create_admin(request):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@email.com',
            password='123456'
        )
        return HttpResponse("Admin created ✅")

    return HttpResponse("Admin already exists")


# -------------------------------
# Dashboard
# -------------------------------
@login_required(login_url="login")
def dashboard(request):
    books = Book.objects.all()
    total_books = books.count()
    subject_counts = books.values('subject').annotate(count=Count('id'))
    level_counts = books.values('level').annotate(count=Count('id'))

    context = {
        'books': books,
        'total_books': total_books,
        'subject_counts': subject_counts,
        'level_counts': level_counts,
    }
    return render(request, 'library/dashboard.html', context)


# -------------------------------
# Library List
# -------------------------------
@login_required(login_url="login")
def library_list(request):
    query = request.GET.get("q", "").strip()
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(subject__icontains=query) |
            Q(level__icontains=query)
        )

    books = books.order_by("level", "subject", "title")
    paginator = Paginator(books, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "library/library.html", {
        "page_obj": page_obj,
        "query": query,
    })


# -------------------------------
# Read Book
# -------------------------------
@login_required(login_url='login')
def read_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return redirect(book.pdf_url)


# -------------------------------
# Admin CRUD
# -------------------------------
@login_required(login_url='login')
@admin_required
def add_book(request):
    form = BookForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('library')
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Add'})


@login_required(login_url='login')
@admin_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, request.FILES or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect('library')
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Edit'})


@login_required(login_url='login')
@admin_required
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('library')
    return render(request, 'library/book_confirm_delete.html', {'book': book})


# -------------------------------
# Bulk Upload (CSV)
# -------------------------------
@login_required(login_url="login")
def bulk_upload_books(request):
    if not request.user.is_superuser:
        return redirect("library")

    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")

        if not csv_file or not csv_file.name.endswith(".csv"):
            messages.error(request, "Please upload a valid CSV file.")
            return redirect("bulk_upload_books")

        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        created = 0
        for row in reader:
            Book.objects.create(
                title=row["title"].strip(),
                subject=row["subject"].strip(),
                level=row["level"].strip(),
                pdf_url=row["pdf_url"].strip(),
            )
            created += 1

        messages.success(request, f"{created} books uploaded successfully.")
        return redirect("library")

    return render(request, "library/bulk_upload.html")