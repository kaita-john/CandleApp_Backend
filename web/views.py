from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from appuser.models import AppUser
from constants import COMPANYAMOUNT
from request.models import Request


@never_cache
def login_view(request):
    print(f"Here")
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        if not email or not password:
            messages.error(request, _("Username and password are required!"))
            return redirect("loginpage")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, _("Login successful!"))
            return redirect("homepage")
        else:
            messages.error(request, _("Invalid username or password. Please try again."))
            return redirect("loginpage")
    return render(request, "loginadmin.html")



def users_view(request):
    users = AppUser.objects.all()
    filter_counts = {
        "all": users.count(),
        "celeb": users.filter(roles__name="CELEB", is_celeb = True).count(),
        "client": users.filter(is_celeb=False).count(),
        "unapproved": users.filter(is_admin=True).count(),
    }
    unapproved_celebs = users.filter(roles__name="CELEB", is_admin=True).count()
    return render(request,"users.html",{
            "users": users,
            "filter_counts": filter_counts,
            "unapproved_celebs": unapproved_celebs,
        }
    )



def requests_view(request):
    requests = Request.objects.all()
    filter_counts = {
        "all": requests.count(),
        "PENDING": requests.filter(state="PENDING").count(),
        "COMPLETED": requests.filter(state="COMPLETED").count(),
        "CANCELED": requests.filter(state="CANCELED").count(),
        "WITHDRAWN": requests.filter(state ="WITHDRAWN").count(),
        "WITHDRAW": requests.filter(withdraw_request=True, state = "WITHDRAWREQUEST").count(),
    }

    for req in requests:
        req.withdraw_amount = float(Decimal(req.amount)) - (float(Decimal(req.amount) * Decimal(COMPANYAMOUNT)))
        req.company_amount = float(req.amount) - req.withdraw_amount
    return render(request, "requests.html", {"requests": requests, "filter_counts": filter_counts})


def homepage_view(request):
    if not request.user.is_authenticated:
        messages.error(request, _("You must be logged in to view the homepage."))
        return redirect("loginpage")

    # Fetch all users
    users = AppUser.objects.all()
    total_users = users.objects.all().count()
    total_clients = users.filter(is_celeb=False).count()
    total_celebs = users.filter(roles__name="CELEB", is_celeb=True).count()
    unapproved_celebrities = users.filter(is_admin=True).count(),

    # Requests metrics
    requests = Request.objects.all()
    total_requests = requests.count()
    pending_requests = requests.filter(state="PENDING")
    withdrawal_requests = requests.filter(state="WITHDRAWREQUEST")
    withdrawn_requests = requests.filter(state="WITHDRAWN")

    total_amount_transacted = withdrawn_requests.aggregate( total_transacted=Sum("amount"))["total_transacted"] or Decimal(0)
    total_paid_to_clients = withdrawn_requests.aggregate(total_withdrawn=Sum("clientamount"))["total_withdrawn"] or Decimal(0)
    total_paid_to_company = withdrawn_requests.aggregate(total_withdrawn=Sum("companyamount"))["total_withdrawn"] or Decimal(0)

    # Pass metrics to template
    context = {
        "total_users": total_users,
        "total_clients": total_clients,
        "total_celebs": total_celebs,
        "unapproved_celebs": unapproved_celebrities,
        "total_requests": total_requests,
        "pending_requests": pending_requests.count(),
        "withdrawal_requests_count": withdrawal_requests.count(),
        "withdrawn_requests_count": withdrawn_requests.count(),
        "total_amount_transacted": total_amount_transacted,
        "total_paid_to_clients": total_paid_to_clients,
        "total_paid_to_company": total_paid_to_company,
    }

    return render(request, "adminindex.html", context)
