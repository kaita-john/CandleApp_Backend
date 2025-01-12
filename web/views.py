from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache

from appuser.models import AppUser
from constants import COMPANYAMOUNT
from request.models import Request


@never_cache
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        if not email or not password:
            messages.error(request, _("Username and password are required!"))
            return redirect("loginpage")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                messages.success(request, _("Login successful!"))
                return redirect("homepage")
            else:
                messages.error(request, _("You must be a superuser to access this page."))
                return redirect("loginpage")
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
        "WITHDRAW": requests.filter(withdraw_request=True).exclude(state="WITHDRAWN").count(),
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
    total_users = users.count()
    total_clients = users.filter(is_celeb=False).count()
    total_celebs = users.filter(roles__name="CELEB", is_celeb=True).count()
    unapproved_celebrities = users.filter(is_admin=True).count()

    # Requests metrics
    requests = Request.objects.all()
    total_requests = requests.count()
    pending_requests = requests.filter(state="PENDING")
    withdrawal_requests = requests.filter(state="WITHDRAWREQUEST")
    withdrawn_requests = requests.filter(state="WITHDRAWN")

    total_amount_transacted = requests.aggregate( total_transacted=Sum("amount"))["total_transacted"]
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

def delete_user(request, user_id):
    user = get_object_or_404(AppUser, id=user_id)
    user.delete()
    messages.success(request, "User has been successfully deleted.")
    return redirect('userspage')

def deactivate_user(request, user_id):
    user = get_object_or_404(AppUser, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, "User has been successfully deactivated.")
    return redirect('userspage')


def approve_celeb(request, user_id):
    user = get_object_or_404(AppUser, id=user_id)
    if user.is_admin:
        user.is_admin = False
        user.save()
        messages.success(request, "Celeb has been successfully approved.")
    else:
        messages.error(request, "This user is already approved or is not a celeb.")
    return redirect('userspage')



def mark_paid(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    req.complete_requested_by_celeb = False
    req.state = 'WITHDRAWN'
    req.withdrawn = True
    req.withdrawn_date = timezone.now()
    req.save()
    return redirect('requestspage')

def refund_request(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    if req.refund_Request:
        req.refunded = True
        req.refundedOn = timezone.now()
        req.save()
        messages.success(request, "Request refunded successfully.")
    else:
        messages.error(request, "Refund not allowed for this request.")
    return redirect("requestspage")



def custom_logout_view(request):
    logout(request)
    return redirect("loginpage")  # Replace 'homepage' with your desired redirect URL
