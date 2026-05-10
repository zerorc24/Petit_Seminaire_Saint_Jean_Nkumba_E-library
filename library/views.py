import random
import time

from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse

from .models import Book
from .forms import BookForm

User = get_user_model()


# =========================================================
# 🏠 HOME
# =========================================================
def home(request):
    latest_books = Book.objects.order_by("-id")[:6]
    return render(request, "library/home.html", {"latest_books": latest_books})


# =========================================================
# 🧾 REGISTER
# =========================================================
def register(request):
    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            messages.error(request, "All fields are required")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.is_active = True
        user.status = "pending" if hasattr(user, "status") else None
        user.save()

        messages.success(request, "Account created. Wait for admin approval.")
        return redirect("login")

    return render(request, "library/register.html")


# =========================================================
# 🔐 LOGIN
# =========================================================
def login_view(request):

    if request.method == "GET":
        return render(request, "library/login.html")

    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)

    if not user:
        messages.error(request, "Invalid credentials")
        return redirect("login")

    status = getattr(user, "status", "pending")

    if not user.is_staff and status != "approved":
        messages.error(request, "Waiting for admin approval")
        return redirect("login")

    request.session["pending_user_id"] = user.id
    return redirect("send_code_page")


# =========================================================
# 📧 SEND CODE PAGE
# =========================================================
def send_code_page(request):

    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("login")

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("login")

    return render(request, "library/send_code.html", {"email": user.email})


# =========================================================
# 📩 SEND OTP (100% SAFE)
# =========================================================
def send_verification_code(request):

    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("login")

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("login")

    # Generate OTP
    code = str(random.randint(100000, 999999))

    request.session["email_code"] = code
    request.session["code_time"] = time.time()

    print("OTP CODE:", code)

    # 🚨 NEVER try email on Render unless configured properly
    email_host = getattr(settings, "EMAIL_HOST_USER", None)
    email_pass = getattr(settings, "EMAIL_HOST_PASSWORD", None)

    # SAFE MODE: if email not fully configured → just show OTP page
    if not email_host or not email_pass:
        return render(request, "library/otp_display.html", {
            "code": code
        })

    # Try email ONLY if configured
    try:
        send_mail(
            subject="Your Login OTP",
            message=f"Your OTP is: {code}",
            from_email=email_host,
            recipient_list=[user.email],
            fail_silently=True
        )

    except Exception as e:
        print("EMAIL ERROR:", e)

        # fallback instead of crashing
        return render(request, "library/otp_display.html", {
            "code": code
        })

    return redirect("verify_code")

# =========================================================
# 🚪 LOGOUT
# =========================================================
def logout_view(request):
    logout(request)
    return redirect("home")


# =========================================================
# 📚 LIBRARY
# =========================================================
def library(request):
    if not request.user.is_authenticated:
        return redirect("login")

    query = request.GET.get("q", "")
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(subject__icontains=query) |
            Q(level__icontains=query)
        )

    paginator = Paginator(books.order_by("-id"), 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "library/library.html", {
        "page_obj": page_obj,
        "query": query
    })


# =========================================================
# 📊 DASHBOARD
# =========================================================
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "library/dashboard.html", {
        "total_books": Book.objects.count(),
        "subject_counts": Book.objects.values("subject").annotate(count=Count("id")),
        "level_counts": Book.objects.values("level").annotate(count=Count("id")),
    })


# =========================================================
# 👨‍💼 ADMIN DASHBOARD
# =========================================================
@staff_member_required
def admin_dashboard(request):

    users = User.objects.all()

    pending, approved, rejected = [], [], []

    for u in users:
        status = getattr(u, "status", None)

        if status == "approved":
            approved.append(u)
        elif status == "rejected":
            rejected.append(u)
        else:
            pending.append(u)

    return render(request, "library/admin_dashboard.html", {
        "users": users,
        "books": Book.objects.all(),
        "pending_users": pending,
        "approved_users": approved,
        "rejected_users": rejected,
        "total_users": users.count(),
        "total_books": Book.objects.count(),
        "staff_users": users.filter(is_staff=True).count(),
    })


# =========================================================
# 👤 APPROVE / REJECT
# =========================================================
@staff_member_required
def approve_user(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        user.status = "approved"
        user.is_active = True
        user.save()
    return redirect("admin_dashboard")


@staff_member_required
def reject_user(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if user:
        user.status = "rejected"
        user.is_active = False
        user.save()
    return redirect("admin_dashboard")


# =========================================================
# 📖 BOOK
# =========================================================
def read_book(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    book = get_object_or_404(Book, pk=pk)

    if book.pdf_url and book.pdf_url.startswith("http"):
        return redirect(book.pdf_url)

    return render(request, "library/book_detail.html", {"book": book})


# =========================================================
# 🛠 BOOK CRUD
# =========================================================
@staff_member_required
def add_book(request):
    form = BookForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect("library")
    return render(request, "library/book_form.html", {"form": form})


@staff_member_required
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, request.FILES or None, instance=book)
    if form.is_valid():
        form.save()
        return redirect("library")
    return render(request, "library/book_form.html", {"form": form})


@staff_member_required
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        return redirect("library")
    return render(request, "library/book_confirm_delete.html", {"book": book})