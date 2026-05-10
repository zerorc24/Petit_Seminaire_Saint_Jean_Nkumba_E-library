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
    return render(request, "library/home.html", {
        "latest_books": latest_books
    })


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

        if hasattr(user, "status"):
            user.status = "pending"

        user.save()

        messages.success(
            request,
            "Account created successfully. Wait for admin approval."
        )

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

    user = authenticate(
        request,
        username=username,
        password=password
    )

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
# 📩 SEND VERIFICATION CODE
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

    # Save OTP in session
    request.session["email_code"] = code
    request.session["code_time"] = time.time()

    print("OTP CODE:", code)

    try:

        # ONLY try email if credentials exist
        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:

            send_mail(
                subject="Login Verification Code",
                message=f"Your OTP code is: {code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=True
            )

            print("EMAIL SENT")

    except Exception as e:

        print("EMAIL ERROR:", e)

    # IMPORTANT:
    # Never crash
    return redirect("verify_code")

# =========================================================
# 🔐 VERIFY CODE
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

    # expire after 5 mins
    if time.time() - request.session.get("code_time", 0) > 300:
        messages.error(request, "Code expired")
        return redirect("login")

    if entered_code == saved_code:

        user = User.objects.filter(id=user_id).first()

        if not user:
            return redirect("login")

        login(request, user)

        # clear session
        request.session.pop("pending_user_id", None)
        request.session.pop("email_code", None)
        request.session.pop("code_time", None)

        if user.is_staff:
            return redirect("admin_dashboard")

        return redirect("home")

    messages.error(request, "Invalid verification code")

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

    paginator = Paginator(
        books.order_by("-id"),
        9
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

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
        "subject_counts": Book.objects.values(
            "subject"
        ).annotate(count=Count("id")),
        "level_counts": Book.objects.values(
            "level"
        ).annotate(count=Count("id")),
    })


# =========================================================
# 👨‍💼 ADMIN DASHBOARD
# =========================================================
@staff_member_required
def admin_dashboard(request):

    users = User.objects.all()
    books = Book.objects.all()

    pending = []
    approved = []
    rejected = []

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
        "books": books,
        "pending_users": pending,
        "approved_users": approved,
        "rejected_users": rejected,
        "total_users": users.count(),
        "total_books": books.count(),
        "staff_users": users.filter(is_staff=True).count(),
    })


# =========================================================
# 👤 APPROVE USER
# =========================================================
@staff_member_required
def approve_user(request, user_id):

    user = User.objects.filter(id=user_id).first()

    if user:

        if hasattr(user, "status"):
            user.status = "approved"

        user.is_active = True
        user.save()

    return redirect("admin_dashboard")


# =========================================================
# ❌ REJECT USER
# =========================================================
@staff_member_required
def reject_user(request, user_id):

    user = User.objects.filter(id=user_id).first()

    if user:

        if hasattr(user, "status"):
            user.status = "rejected"

        user.is_active = False
        user.save()

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

    return render(
        request,
        "library/book_detail.html",
        {"book": book}
    )


# =========================================================
# ➕ ADD BOOK
# =========================================================
@staff_member_required
def add_book(request):

    form = BookForm(
        request.POST or None,
        request.FILES or None
    )

    if form.is_valid():
        form.save()
        return redirect("library")

    return render(
        request,
        "library/book_form.html",
        {"form": form}
    )


# =========================================================
# ✏️ EDIT BOOK
# =========================================================
@staff_member_required
def edit_book(request, pk):

    book = get_object_or_404(Book, pk=pk)

    form = BookForm(
        request.POST or None,
        request.FILES or None,
        instance=book
    )

    if form.is_valid():
        form.save()
        return redirect("library")

    return render(
        request,
        "library/book_form.html",
        {"form": form}
    )


# =========================================================
# 🗑 DELETE BOOK
# =========================================================
@staff_member_required
def delete_book(request, pk):

    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        book.delete()
        return redirect("library")

    return render(
        request,
        "library/book_confirm_delete.html",
        {"book": book}
    )
# =========================================================
# 📦 BULK UPLOAD BOOKS
# =========================================================
@staff_member_required
def bulk_upload_books(request):

    if request.method == "POST":

        csv_file = request.FILES.get("csv_file")

        if not csv_file:
            messages.error(request, "Please upload a CSV file")
            return redirect("bulk_upload_books")

        # Check file type
        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Only CSV files are allowed")
            return redirect("bulk_upload_books")

        try:

            decoded_file = csv_file.read().decode("utf-8").splitlines()

            reader = csv.DictReader(decoded_file)

            added_count = 0

            for row in reader:

                title = row.get("title")
                subject = row.get("subject")
                level = row.get("level")
                pdf_url = row.get("pdf_url")

                # Skip empty rows
                if not title:
                    continue

                Book.objects.create(
                    title=title,
                    subject=subject,
                    level=level,
                    pdf_url=pdf_url
                )

                added_count += 1

            messages.success(
                request,
                f"{added_count} books uploaded successfully"
            )

            return redirect("library")

        except Exception as e:

            print("CSV ERROR:", e)

            messages.error(
                request,
                "CSV upload failed"
            )

            return redirect("bulk_upload_books")

    return render(
        request,
        "library/bulk_upload.html"
    )