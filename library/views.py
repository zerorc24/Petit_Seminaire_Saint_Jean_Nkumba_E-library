import csv
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
# 🧾 REGISTER (SAFE)
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

        # SAFE DEFAULTS (ONLY IF FIELD EXISTS)
        if hasattr(user, "status"):
            user.status = "pending"

        if hasattr(user, "is_approved"):
            user.is_approved = False

        user.is_active = True
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

    # SAFE STATUS CHECK
    status = getattr(user, "status", "pending")

    if not user.is_staff and status != "approved":
        messages.error(request, "Waiting for admin approval")
        return redirect("login")

    request.session["pending_user_id"] = user.id
    return redirect("send_code_page")


# =========================================================
# 📧 OTP PAGE
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
# 📩 SEND OTP (SAFE EMAIL)
# =========================================================
def send_verification_code(request):

    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("login")

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("login")

    code = str(random.randint(100000, 999999))

    request.session["email_code"] = code
    request.session["code_time"] = time.time()

    try:
        send_mail(
            "Login Verification Code",
            f"Your OTP code is: {code}",
            settings.EMAIL_HOST_USER,
            [user.email],
        )
    except Exception:
        messages.error(request, "Email service not available")
        return redirect("login")

    return redirect("verify_code")


# =========================================================
# 🔐 VERIFY OTP
# =========================================================
def verify_code(request):

    user_id = request.session.get("pending_user_id")
    if not user_id:
        return redirect("login")

    if request.method == "GET":
        return render(request, "library/verify_code.html")

    entered_code = request.POST.get("code")
    saved_code = request.session.get("email_code")

    if not saved_code:
        messages.error(request, "Session expired")
        return redirect("login")

    if time.time() - request.session.get("code_time", 0) > 300:
        messages.error(request, "Code expired")
        return redirect("login")

    if entered_code == saved_code:

        user = User.objects.filter(id=user_id).first()
        if not user:
            return redirect("login")

        login(request, user)

        # CLEAN SESSION
        request.session.pop("pending_user_id", None)
        request.session.pop("email_code", None)
        request.session.pop("code_time", None)

        return redirect("admin_dashboard" if user.is_staff else "home")

    messages.error(request, "Invalid code")
    return redirect("verify_code")


# =========================================================
# 🚪 LOGOUT
# =========================================================
def logout_view(request):
    logout(request)
    request.session.flush()
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
# 👨‍💼 ADMIN DASHBOARD (PRO + SAFE)
# =========================================================
@staff_member_required
# =========================================================
# 👨‍💼 ADMIN DASHBOARD (PRO LEVEL 2 - CRASH PROOF)
# =========================================================
@staff_member_required
def admin_dashboard(request):

    users = User.objects.all()
    books = Book.objects.all()

    pending = []
    approved = []
    rejected = []

    for u in users:

        # SAFE STATUS SYSTEM (NEVER CRASHES EVEN IF FIELD DOES NOT EXIST)
        status = getattr(u, "status", None)

        if status == "approved":
            approved.append(u)

        elif status == "rejected":
            rejected.append(u)

        else:
            pending.append(u)

    return render(request, "library/admin_dashboard.html", {
        "users": users,
        "books": books,

        "pending_users": pending,
        "approved_users": approved,
        "rejected_users": rejected,

        "total_users": users.count(),
        "total_books": books.count(),
        "staff_users": users.filter(is_staff=True).count(),
    })


# =========================================================
# 👤 APPROVE USER (ULTRA SAFE)
# =========================================================
@staff_member_required
def approve_user(request, user_id):

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("admin_dashboard")

    # SAFE FIELD UPDATE (ONLY IF EXISTS)
    if hasattr(user, "status"):
        user.status = "approved"

    if hasattr(user, "is_approved"):
        user.is_approved = True

    # ALWAYS SAFE
    user.is_active = True
    user.save()

    return redirect("admin_dashboard")


# =========================================================
# ❌ REJECT USER (ULTRA SAFE)
# =========================================================
@staff_member_required
def reject_user(request, user_id):

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("admin_dashboard")

    if hasattr(user, "status"):
        user.status = "rejected"

    if hasattr(user, "is_approved"):
        user.is_approved = False

    # SAFER SECURITY BEHAVIOR
    user.is_active = False
    user.save()

    return redirect("admin_dashboard")


# =========================================================
# 🧹 RESET USERS (SAFE + NON-DESTRUCTIVE)
# =========================================================
@staff_member_required
def reset_users(request):

    # ONLY RUN IF FIELD EXISTS IN DATABASE MODEL
    if "status" in [f.name for f in User._meta.fields]:
        User.objects.filter(status="approved").update(status="pending")

    return redirect("admin_dashboard")

# =========================================================
# 📖 READ BOOK
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


# =========================================================
# 📦 BULK UPLOAD
# =========================================================
@staff_member_required
def bulk_upload_books(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "Upload CSV file")
            return redirect("bulk_upload_books")

        try:
            decoded = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded)

            for row in reader:
                Book.objects.create(
                    title=row.get("title", ""),
                    subject=row.get("subject", ""),
                    level=row.get("level", ""),
                    pdf_url=row.get("pdf_url", "")
                )

        except Exception:
            messages.error(request, "Invalid CSV format")
            return redirect("bulk_upload_books")

        return redirect("library")

    return render(request, "library/bulk_upload.html")