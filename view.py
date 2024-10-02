from datetime import date, datetime, timedelta
from decimal import Decimal
from django.contrib.humanize.templatetags.humanize import naturaltime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User as djangouser
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import *


def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not djangouser.objects.filter(username=username).exists():
            messages.error(request, "invalid username")
            return redirect("/login/")

        userauth = authenticate(username=username, password=password)
        if userauth is None:
            messages.error(request, "Invalid Password")
            return redirect("/login/")

        else:
            login(request, userauth)
            return redirect("/")
    return render(request, "login.html")


def logout_page(request):
    logout(request)
    return redirect("/login/")


def register(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        username = request.POST.get("username")
        password = request.POST.get("password")

        usersss = djangouser.objects.filter(username=username)
        if usersss.exists():
            messages.info(request, "User Name is alrady exits")

            return redirect("/register/")

        user = djangouser.objects.create(
            first_name=firstname,
            last_name=lastname,
            username=username,
        )
        user.set_password(password)
        user.save()
        messages.info(request, "Acount created successfully")

        return redirect("/register/")

    return render(request, "register.html")


@login_required(login_url="/login/")
def searchpage(request):
    search = request.GET.get("search")
    result = Searchmodeldata.objects.all()

    user_interests = []
    total_amount = 0.0
    all_user_interest = 0.0
    total_month = 0.0

    current_date = date.today()
    if search:
        query_parts = search.split()
        filters = Q()
        for part in query_parts:
            filters |= Q(gender__icontains=part)
            filters |= Q(fname__icontains=part)
            filters |= Q(lname__icontains=part)
            filters |= Q(email__icontains=part)
            filters |= Q(permanentad__icontains=part)
            filters |= Q(curentad__icontains=part)  # Corrected field name
            filters |= Q(bilnumber__icontains=part)  # Add filter for asd
            filters |= Q(bondnumber__icontains=part)

            if part.isdigit():
                filters |= Q(amount=part)
                filters |= Q(phone=part)
                filters |= Q(interest_rate=part)

        result = Searchmodeldata.objects.filter(filters)

    for user in result:
        amount = float(user.amount)
        interest_rate = float(user.interest_rate)
        time_to_give = user.time_to_give
        due_date = user.due_date

        total_interest = (amount * (interest_rate / 100) * time_to_give) / 12
        all_user_interest += total_interest
        total_amount += amount
        total_month += time_to_give

        total_day = total_month * 30.44
        average_profit_perday = all_user_interest / total_day if total_day else 0

        is_today = current_date >= due_date

        user_interests.append(
            {
                "user": user,
                "total_interest": total_interest,
                "daily_interest": total_interest / (time_to_give * 30.44),
                "is_today": is_today,
                "bilnumber": user.bilnumber,
            }
        )

    paginator = Paginator(user_interests, 25)  # Show 25 results per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "result": page_obj,
        "search": search,
    }

    return render(request, "search.html", context)


# base page
@login_required(login_url="/login/")
def basepage(request):
    users = User.objects.all()

    user_interests = []
    total_amount = 0.0
    all_user_interest = 0.0
    total_month = 0.0
    average_profit_perday = 0.0

    current_date = date.today()

    for user in users:
        amount = float(user.amount)
        interest_rate = float(user.interest_rate)
        time_to_give = user.time_to_give
        due_date = user.due_date

        total_interest = (amount * (interest_rate / 100) * time_to_give) / 12
        all_user_interest += total_interest
        total_amount += amount
        total_month += time_to_give

        total_day = total_month * 30.44
        average_profit_perday = total_interest / (time_to_give * 30.44)

        is_today = current_date >= due_date

        user_interests.append(
            {
                "user": user,
                "total_interest": total_interest,
                "daily_interest": total_interest
                / (time_to_give * 30.44),  # Daily interest calculation
                "is_today": is_today,
            }
        )

    graphbarchart = [
        {"label": "Total Interest", "y": all_user_interest, "color": "#FF6384"},  # Red
        {
            "label": "Daily Interest",
            "y": average_profit_perday,
            "color": "#36A2EB",
        },  # Blue
        {"label": "Total Amount", "y": total_amount, "color": "#FFCE56"},  # Yellow
        {"label": "Total Month", "y": total_month, "color": "#4BC0C0"},  # Teal
    ]
    graphpichart = [
        {"label": "Total Interest", "y": all_user_interest, "color": "#FF6384"},  # Red
        {
            "label": "Daily Interest",
            "y": average_profit_perday,
            "color": "#36A2EB",
        },  # Blue
        {"label": "Total Amount", "y": total_amount, "color": "#FFCE56"},  # Yellow
        {"label": "Total Month", "y": total_month, "color": "#4BC0C0"},  # Teal
    ]

    context = {
        "user_interests": user_interests,
        "total_amount": total_amount,
        "all_user_interest": all_user_interest,
        "total_month": total_month,
        "average_profit_perday": average_profit_perday,
        "graphpichart": graphpichart,
        "graphbarchart": graphbarchart,
    }

    return render(request, "indexx.html", context)


@login_required(login_url="/login/")
def paymentdone_view(request):
    payments = PaymentDon.objects.all()
    total_amount = 0.0
    all_user_interest = 0.0
    total_month = 0.0
    average_profit_perday = 0.0

    current_date = date.today()

    for payment in payments:
        amount = float(payment.user_amount) if payment.user_amount else 0.0
        interest_rate = float(payment.user_interest) if payment.user_interest else 0.0
        time_to_give = (
            float(payment.user_time_to_give) if payment.user_time_to_give else 0.0
        )

        total_interest = (amount * (interest_rate / 100) * time_to_give) / 12

        total_amount += amount
        all_user_interest += total_interest
        total_month += time_to_give

    if total_month > 0:
        average_profit_perday = all_user_interest / (
            total_month * 30.44
        )  # Approximate days in a month

    context = {
        "payments": payments,
        "total_amount": total_amount,
        "all_user_interest": all_user_interest,
        "total_month": total_month,
        "average_profit_perday": average_profit_perday,
    }

    return render(request, "paymentdone.html", context)


@login_required(login_url="/login/")
def userdata(request):
    users = User.objects.all()

    user_interests = []
    total_amount = 0.0
    all_user_interest = 0.0
    total_month = 0.0
    

    current_date = date.today()

    if users.exists():
        for user in users:
            amount = float(user.amount)
            interest_rate = float(user.interest_rate)
            time_to_give = user.time_to_give
            due_date = user.due_date

            # Calculate total interest and days passed
            total_interest = (amount * (interest_rate / 100) * time_to_give) / 12
            all_user_interest += total_interest
            total_amount += amount
            total_month += time_to_give

            total_day = total_month * 30.44
            average_profit_perday = all_user_interest / total_day if total_day else 0

            # Calculate days passed and days remaining
            

            is_today = current_date >= due_date

            user_interests.append(
                {
                    "user": user,
                    "total_interest": total_interest,
                    "daily_interest": total_interest / (time_to_give * 30.44),
                    "is_today": is_today,
                }
            )
    else:
        average_profit_perday = 0.0

    # Apply pagination
    paginator = Paginator(user_interests, 10)  # Show 10 records per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,   
        "total_amount": total_amount,
        "all_user_interest": all_user_interest,
        "average_profit_perday": average_profit_perday,
        "total_month": total_month,
    }

    return render(request, "datatables.html", context)
# form user
@login_required(login_url="/login/")
def adduser(request):
    if request.method == "POST":
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        permanentad = request.POST.get("permanentad")
        curentad = request.POST.get("curentad")
        facepic = request.FILES.get("facepic")
        phone = request.POST.get("phone")
        citizenshipf = request.FILES.get("citizenshipf")
        citizenshipb = request.FILES.get("citizenshipb")
        amount = request.POST.get("amount")
        interest = request.POST.get("interest")
        duedate = request.POST.get("duedate")
        timetogive = request.POST.get("month")
        gender = request.POST.get("gender")
        bilnumber = request.POST.get("bilnumber")
        bondnumber = request.POST.get("bondnumber")

        # Save data in User model
        savedatas = User.objects.create(
            fname=fname,
            lname=lname,
            email=email,
            permanentad=permanentad,
            curentad=curentad,
            gender=gender,
            phone=phone,
            citizenshipf=citizenshipf,
            citizenshipb=citizenshipb,
            amount=amount,
            interest_rate=interest,
            due_date=duedate,
            time_to_give=timetogive,
            facepic=facepic,
            bilnumber=bilnumber,
            bondnumber=bondnumber,
        )

        Searchmodeldata.objects.create(
            uuid=savedatas.uuid,
            gender=savedatas.gender,
            amount=savedatas.amount,
            interest_rate=savedatas.interest_rate,
            time_to_give=savedatas.time_to_give,
            due_date=savedatas.due_date,
            fname=savedatas.fname,
            lname=savedatas.lname,
            email=savedatas.email,
            permanentad=savedatas.permanentad,
            curentad=savedatas.curentad,
            phone=savedatas.phone,
            citizenshipf=savedatas.citizenshipf,
            citizenshipb=savedatas.citizenshipb,
            facepic=savedatas.facepic,
            bilnumber=bilnumber,
            bondnumber=bondnumber,
        )

    return render(request, "form_basics.html")


#  graph part


@login_required(login_url="/login/")
def datagraph(request):
    total_amount_user = 0.0
    all_user_interest_user = 0.0
    total_month_user = 0.0

    total_amount_paymentdon = 0.0
    all_user_interest_paymentdon = 0.0
    total_month_paymentdon = 0.0

    total_amount_interestpayed = 0.0
    all_user_interest_interestpayed = 0.0
    total_month_interestpayed = 0.0

    users = User.objects.all()
    for user in users:
        amount = float(user.amount) if user.amount else 0
        interest_rate = float(user.interest_rate) if user.interest_rate else 0
        time_to_give = user.time_to_give or 0
        total_interest = (amount * (interest_rate / 100) * time_to_give) / 12
        all_user_interest_user += total_interest
        total_amount_user += amount
        total_month_user += time_to_give

    payments = PaymentDon.objects.all()
    for payment in payments:
        amount = float(payment.user_amount) if payment.user_amount else 0
        interest_rate = float(payment.user_interest) if payment.user_interest else 0
        time_to_give = (
            int(payment.user_time_to_give) if payment.user_time_to_give else 0
        )

        total_interest = (amount * (interest_rate / 100) * time_to_give) / 12
        all_user_interest_paymentdon += total_interest
        total_amount_paymentdon += amount
        total_month_paymentdon += time_to_give

    interests = Interestpayed.objects.all()
    for interest in interests:
        amount = float(interest.interest_amount) if interest.interest_amount else 0
        interest_rate = (
            float(interest.interest_interest) if interest.interest_interest else 0
        )
        time_to_give = (
            int(interest.interest_time_to_give) if interest.interest_time_to_give else 0
        )

        total_interest = (amount * (interest_rate / 100) * time_to_give) / 12
        all_user_interest_interestpayed += total_interest
        total_amount_interestpayed += amount
        total_month_interestpayed += time_to_give

    monthly_data = {
        "months": [],
        "amount_user": [],
        "amount_paymentdon": [],
        "amount_interestpayed": [],
    }

    for month_offset in range(12):
        month = (datetime.now().month - month_offset - 1) % 12 + 1
        year = datetime.now().year - ((datetime.now().month - month_offset - 1) // 12)
        date = datetime(year, month, 1)

        monthly_data["months"].append(date.strftime("%B %Y"))

        monthly_amount_user = sum(
            float(user.amount)
            for user in users
            if user.created_at.month == month and user.created_at.year == year
        )
        monthly_amount_paymentdon = sum(
            float(payment.user_amount)
            for payment in payments
            if payment.payment_date.month == month and payment.payment_date.year == year
        )
        monthly_amount_interestpayed = sum(
            float(interest.interest_amount)
            for interest in interests
            if hasattr(interest, "payment_date")
            and interest.payment_date.month == month
            and interest.payment_date.year == year
        )

        monthly_data["amount_user"].append(monthly_amount_user)
        monthly_data["amount_paymentdon"].append(monthly_amount_paymentdon)
        monthly_data["amount_interestpayed"].append(monthly_amount_interestpayed)

    graphpichart1 = [
        {"label": "Total Interest", "y": all_user_interest_user, "color": "#FF6384"},
        {"label": "Total Amount", "y": total_amount_user, "color": "#36A2EB"},
        {"label": "Total Month", "y": total_month_user, "color": "#FFCE56"},
    ]

    graphpichart2 = [
        {
            "label": "Total Interest",
            "y": all_user_interest_paymentdon,
            "color": "#FF6384",
        },
        {"label": "Total Amount", "y": total_amount_paymentdon, "color": "#36A2EB"},
        {"label": "Total Month", "y": total_month_paymentdon, "color": "#FFCE56"},
    ]

    graphpichart3 = [
        {
            "label": "Total Interest",
            "y": all_user_interest_interestpayed,
            "color": "#FF6384",
        },
        {"label": "Total Amount", "y": total_amount_interestpayed, "color": "#36A2EB"},
        {"label": "Total Month", "y": total_month_interestpayed, "color": "#FFCE56"},
    ]

    line_chart_data = {
        "months": monthly_data["months"],
        "amount_user": monthly_data["amount_user"],
        "amount_paymentdon": monthly_data["amount_paymentdon"],
        "amount_interestpayed": monthly_data["amount_interestpayed"],
    }

    context = {
        "graphpichart1": graphpichart1,
        "graphpichart2": graphpichart2,
        "graphpichart3": graphpichart3,
        "line_chart_data": line_chart_data,
    }

    return render(request, "charts.html", context)


@login_required(login_url="/login/")
def dynamicrouting(request, uuid):
    user = get_object_or_404(User, uuid=uuid)

    amount = float(user.amount)
    interest_rate = float(user.interest_rate)
    time_to_give = user.time_to_give
    createdat = user.created_at
    month_to_day = time_to_give * 30.44
    total_interest = amount * (interest_rate / 100) * time_to_give / 12
    daily_interest = total_interest / month_to_day

    due_date = user.due_date
    fname = user.fname
    lname = user.lname
    email = user.email
    gender = user.gender
    permanented = user.permanentad
    curentad = user.curentad

    phone = user.phone
    citizenshipf = user.citizenshipf
    citizenshipb = user.citizenshipb
    facepic = user.facepic
    bilnumber = user.bilnumber
    bondnumber = user.bondnumber

    # Generate graph data
    graph_data = []
    accumulated_interest = 0

    current_date = datetime.now().date()
    is_today = current_date >= due_date

    days_since_created = (current_date - createdat).days
    for day in range(int(month_to_day)):
        date = createdat + timedelta(days=day)
        if accumulated_interest >= total_interest:
            accumulated_interest = total_interest
            break

        if day <= days_since_created:
            accumulated_interest += daily_interest

        graph_data.append(
            {
                "label": date.strftime("%Y- %m-%d"),
                "y": min(accumulated_interest, total_interest),
            }
        )

    context = {
        "totalinterest": total_interest,
        "dailyinterest": daily_interest,
        "amount": amount,
        "interest_rate": interest_rate,
        "time_to_give": time_to_give,
        "graph_data": graph_data,
        "fname": fname,
        "lname": lname,
        "email": email,
        "gender": gender,
        "permanented": permanented,
        "curentad": curentad,
        "phone": phone,
        "citizenshipf": citizenshipf,
        "citizenshipb": citizenshipb,
        "facepic": facepic,
        "is_today": is_today,
        "due_date": due_date,
        "createdat": createdat,
        "bilnumber": bilnumber,
        "bondnumber": bondnumber,
    }
    return render(request, "dynamicrouting.html", context)


from django.utils import timezone


# payment don dynamic url or per user detail
@login_required(login_url="/login/")
def paymentdonedynamic(request, user_uuid):
    user = get_object_or_404(PaymentDon, user_uuid=user_uuid)

    amount = float(user.user_amount)
    interest_rate = float(user.user_interest)  # Annual interest rate
    time_to_give = int(
        user.user_time_to_give
    )  # Number of months, ensure this is an integer
    createdat = user.user_created_at  # Already a date object
    month_to_day = time_to_give * 30.44
    total_interest = amount * (interest_rate / 100) * time_to_give / 12
    daily_interest = total_interest / month_to_day

    due_date = user.user_due_date
    fname = user.user_fname
    lname = user.user_lname
    email = user.user_email
    gender = user.user_gender

    permanented = user.user_permanentad
    curentad = user.user_curentad
    phone = user.user_phone
    citizenshipf = user.user_citizenshipf
    citizenshipb = user.user_citizenshipb
    facepic = user.user_facepic
    bilnumber = user.user_bilnumber
    bondnumber = user.user_bondnumber

    current_date = timezone.now().date()
    is_today = current_date >= due_date

    context = {
        "totalinterest": total_interest,
        "dailyinterest": daily_interest,
        "amount": amount,
        "interest_rate": interest_rate,
        "time_to_give": time_to_give,
        "fname": fname,
        "lname": lname,
        "email": email,
        "gender": gender,
        "permanented": permanented,
        "createdat": createdat,
        "phone": phone,
        "citizenshipf": citizenshipf,
        "citizenshipb": citizenshipb,
        "facepic": facepic,
        "is_today": is_today,
        "due_date": due_date,
        "createdat": createdat,
        "bilnumber": bilnumber,
        "bondnumber": bondnumber,
    }

    return render(request, "paymentdoneperuser.html", context)


@login_required(login_url="/login/")
def mark_payment_done(request, user_uuid):
    # Get the user object or a 404 error if not found
    user = get_object_or_404(User, uuid=user_uuid)

    # Create a PaymentDon object using the data from the User object
    payment = PaymentDon.objects.create(
        donuser=user,
        user_amount=user.amount,
        user_fname=user.fname,
        user_lname=user.lname,
        user_email=user.email,
        user_phone=user.phone,
        user_permanentad=user.permanentad,
        user_uuid=user.uuid,
        user_interest=user.interest_rate,
        user_facepic=user.facepic,
        user_citizenshipf=user.citizenshipf,
        user_citizenshipb=user.citizenshipb,
        user_created_at=user.created_at,
        user_time_to_give=user.time_to_give,
        user_due_date=user.due_date,
        user_gender=user.gender,
        user_curentad=user.curentad,
        user_bilnumber=user.bilnumber,
        user_bondnumber=user.bondnumber,
    )

    payment.save()

    user.delete()

    return redirect(reverse("userdata"))


@login_required(login_url="/login/")
def interestpayed(request, user_uuid):
    user = get_object_or_404(User, uuid=user_uuid)

    payment = Interestpayed.objects.create(
        donusers=user,
        interest_amount=user.amount,
        interest_bilnumber=user.bilnumber,
        interest_fname=user.fname,
        interest_lname=user.lname,
        interest_email=user.email,
        interest_phone=user.phone,
        interest_permanentad=user.permanentad,
        interest_uuid=user.uuid,
        interest_interest=user.interest_rate,
        interest_facepic=user.facepic,
        interest_citizenshipf=user.citizenshipf,
        interest_citizenshipb=user.citizenshipb,
        interest_created_at=user.created_at,
        interest_time_to_give=user.time_to_give,
        interest_due_date=user.due_date,
        interest_gender=user.gender,
        interest_curentad=user.curentad,
        interest_bondnumber=user.bondnumber,
    )
    payment.save()

    user.delete()

    return redirect(reverse("userdata"))


##############interest payed user to pyed user
@login_required(login_url="/login/")
def interestpayedsave(request, interest_uuid):
    intpy = get_object_or_404(Interestpayed, interest_uuid=interest_uuid)

    new_payment = PaymentDon.objects.create(
        donuser=intpy.donusers,
        user_amount=intpy.interest_amount,
        user_bilnumber=intpy.interest_bilnumber,
        user_bondnumber=intpy.interest_bondnumber,
        user_fname=intpy.interest_fname,
        user_lname=intpy.interest_lname,
        user_email=intpy.interest_email,
        user_phone=intpy.interest_phone,
        user_permanentad=intpy.interest_permanentad,
        user_uuid=intpy.interest_uuid,
        user_interest=intpy.interest_interest,
        user_facepic=intpy.interest_facepic,
        user_citizenshipf=intpy.interest_citizenshipf,
        user_citizenshipb=intpy.interest_citizenshipb,
        user_created_at=intpy.interest_created_at,
        user_time_to_give=intpy.interest_time_to_give,
        user_due_date=intpy.interest_due_date,
        user_gender=intpy.interest_gender,
        user_curentad=intpy.interest_curentad,
    )

    new_payment.save()
    intpy.delete()

    return redirect(reverse("interestpayeduserlist"))


# interest paied per user list
@login_required(login_url="/login/")
def interestpayeduserlist(request):
    paymentsss = Interestpayed.objects.all()

    total_amount = 0.0
    all_user_interest = 0.0
    total_month = 0.0
    average_profit_perday = 0.0

    current_date = date.today()

    for payment in paymentsss:
        amount = float(payment.interest_amount) if payment.interest_amount else 0.0
        interest_rate = (
            float(payment.interest_interest) if payment.interest_interest else 0.0
        )
        time_to_give = (
            float(payment.interest_time_to_give)
            if payment.interest_time_to_give
            else 0.0
        )

        total_interest = (amount * (interest_rate / 100) * time_to_give) / 12
        total_amount += amount
        all_user_interest += total_interest
        total_month += time_to_give

    if total_month > 0:
        average_profit_perday = all_user_interest / (total_month * 30.44)
    context = {
        "paymentss": paymentsss,
        "total_amount": total_amount,
        "all_user_interest": all_user_interest,
        "total_month": total_month,
        "average_profit_perday": average_profit_perday,
    }

    return render(request, "interestpayeduser.html", context)


# interest payed per user detail


@login_required(login_url="/login/")
def interestpayeddinamic(request, interest_uuid):
    # Get the interest record for the user
    user = get_object_or_404(Interestpayed, interest_uuid=interest_uuid)

    # Fetch and convert user attributes (ensure float conversion for interest_amount and interest_rate)
    amount = float(user.interest_amount)
    interest_rate = float(user.interest_interest)
    time_to_give = int(user.interest_time_to_give)

    # Calculate total and daily interest
    total_interest = amount * (interest_rate / 100) * time_to_give / 12
    month_to_day = time_to_give * 30.44  # Approximation of days in months
    daily_interest = total_interest / month_to_day if month_to_day else 0  # Avoid division by zero

    # Fetch payment records associated with the interest_uuid
    payments = Interestandpayment.objects.filter(interestpaymentt_uuid=interest_uuid)

    # Calculate remaining amounts and interest
    original_amount = float(user.interest_amount)
    original_interest = float(total_interest)
    remaining_amount = original_amount
    remaining_interest = original_interest

    table_data = []
    for payment in payments:
        remaining_amount -= float(payment.paymentpaid) if payment.paymentpaid else 0
        remaining_interest -= float(payment.interestpaid) if payment.interestpaid else 0
        table_data.append(
            {
                "date": payment.datess,
                "amount": payment.paymentpaid,
                "interest": payment.interestpaid,
                "remainingamount": remaining_amount,
                'remaininginterest': remaining_interest,
                "uuid": payment.interestpaymentt_uuid,
            }
        )

    # Prepare context with payment and user data
    context = {
        "totalinterest": total_interest,
        "dailyinterest": daily_interest,
        "amount": amount,
        "interest_rate": interest_rate,
        "time_to_give": time_to_give,
        "payments": payments,
        "table_data": table_data,
        "fname": user.interest_fname,
        "lname": user.interest_lname,
        "email": user.interest_email,
        "gender": user.interest_gender,
        "permanented": user.interest_permanentad,
        "curentad": user.interest_curentad,
        "phone": user.interest_phone,
        "citizenshipf": user.interest_citizenshipf,
        "citizenshipb": user.interest_citizenshipb,
        "facepic": user.interest_facepic,
        "bilnumber": user.interest_bilnumber,
        "bondnumber": user.interest_bondnumber,
        "due_date": user.interest_due_date,
        "createdat": user.interest_created_at,
        "is_today": timezone.now().date() >= user.interest_due_date,
    }

    # Handle form submission for recording interest payment
    if request.method == "POST":
        interest_paid = request.POST.get("interest_paid")
        payment_paid = request.POST.get("payment_paid")
        payment_date = request.POST.get("payment_date")

        # Convert payment_date to a date object
        try:
            payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d').date()
        except ValueError:
            # Handle invalid date format if necessary
            context['error'] = "Invalid date format. Please use YYYY-MM-DD."
            return render(request, "interestpayeddinamic.html", context)

        # Ensure remaining_amount and remaining_interest are calculated properly
        remaining_amount -= float(payment_paid) if payment_paid else 0
        remaining_interest -= float(interest_paid) if interest_paid else 0

        # Check if remaining_amount or remaining_interest is below 0
        if remaining_amount < 0 or remaining_interest < 0:
            context['error'] = "Remaining amount or interest cannot be negative."
            return render(request, "interestpayeddinamic.html", context)

        # Create a new Interestandpayment instance (ensure float conversion)
        payment = Interestandpayment(
            interestpaymentt_uuid=interest_uuid,
            interestpaid=float(interest_paid) if interest_paid else 0,
            paymentpaid=float(payment_paid) if payment_paid else 0,
            datess=payment_date_obj,
            remaining_amount=remaining_amount,
            remaining_interest=remaining_interest
        )
        payment.save()

        # Redirect to the same view after handling POST to prevent form resubmission
        return redirect(reverse('interestpayeddinamic', args=[interest_uuid]))

    return render(request, "interestpayeddinamic.html", context)
# dynamic search per user detail page
@login_required(login_url="/login/")
def dynamic_search_detail(request, uuid):
    user = get_object_or_404(Searchmodeldata, uuid=uuid)

    current_date = date.today()
    is_today = current_date >= user.due_date

    amount = Decimal(user.amount)
    interest_rate = Decimal(user.interest_rate)
    time_to_give = Decimal(user.time_to_give)

    total_interest = (amount * (interest_rate / Decimal(100)) * time_to_give) / Decimal(
        12
    )
    daily_interest = (
        total_interest / (time_to_give * Decimal(30.44)) if time_to_give else Decimal(0)
    )

    context = {
        "fname": user.fname,
        "lname": user.lname,
        "gender": user.gender,
        "curentad": user.curentad,
        "permanented": user.permanentad,
        "email": user.email,
        "phone": user.phone,
        "createdat": user.created_at,
        "due_date": user.due_date,
        "amount": amount,
        "totalinterest": total_interest,
        "time_to_give": time_to_give,
        "dailyinterest": daily_interest,
        "facepic": user.facepic,
        "citizenshipf": user.citizenshipf,
        "citizenshipb": user.citizenshipb,
        "is_today": is_today,
        "bilnumber": user.bilnumber,
        "bondnumber": user.bondnumber,
    }

    return render(request, "dynamicsearchdetail.html", context)
