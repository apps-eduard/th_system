from django.shortcuts import render, redirect
from django.http import Http404
from django.utils import timezone
from .models import QecData, QtaData, QscData
from .forms import EmailSettingsForm
from django.core.exceptions import ObjectDoesNotExist
from .firebase import get_data_from_firebase
from datetime import datetime, date, time, timedelta
from django.core.cache import cache  # Import Django's cache functions
from .models import AlertData
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
   # Check if the data is cached
    latest_data = cache.get('latest_data')
    
    # If data is not cached, fetch it from Firebase and cache it
    if latest_data is None:
        latest_data = {}
        for database_key in ['qec', 'qsc', 'qta']:
            data = get_data_from_firebase(database_key)
            for key, value in data.items():
                # Convert date string to date object
                value['date'] = datetime.strptime(value['date'], '%Y-%m-%d').date()
                # Convert time string to time object
                value['time'] = datetime.strptime(value['time'], '%H:%M:%S').time()
            latest_data[database_key] = data
        
        # Cache the data with a timeout of 10 minutes (adjust as needed)
        cache.set('latest_data', latest_data, timeout=60)

    # Process the fetched data as needed
    context = {'latest_data': latest_data, 'show_navbar': True}
    return render(request, 'monitoring/dashboard.html', context)



def trend_page(request):
    # Category mapping to model classes
    model_map = {
        'qec': QecData,
        'qta': QtaData,
        'qsc': QscData,
    }
    
    # Calculate dates for the last month
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Format dates for the input fields
    default_end_date = end_date.strftime('%Y-%m-%d')
    default_start_date = start_date.strftime('%Y-%m-%d')
    
    # Get category and dates from GET request or use defaults
    category = request.GET.get('category', 'qsc').lower()  # Default to 'qsc' if not provided
    selected_start_date = request.GET.get('start_date', default_start_date)
    selected_end_date = request.GET.get('end_date', default_end_date)

    # Validate category
    if category not in model_map:
        return render(request, 'error_page.html', {'error': 'Invalid category specified'})

    # Get the model based on the category
    model = model_map[category]

    # Fetch data from the model based on the selected date range
    data = model.objects.filter(
        date__gte=selected_start_date,
        date__lte=selected_end_date
    ).order_by('-date', '-time')

    context = {
        'category': category.upper(),
        'data': data,
        'start_date': selected_start_date,
        'end_date': selected_end_date,
        'show_navbar': True
    }

    return render(request, 'monitoring/trend_page.html', context)

def email_settings(request):
    if request.method == "POST":
        form = EmailSettingsForm(request.POST)
        if form.is_valid():
            form.save()
            # Ensure you have a URL named 'success_url' defined in your urls.py, or change this to an appropriate redirect.
            return redirect('monitoring:dashboard')  # Example: redirecting to the dashboard after saving.
    else:
        form = EmailSettingsForm()
    
    # Adjusted the template path to include the app name as a namespace.
    return render(request, 'monitoring/email_settings.html', {'form': form, 'show_navbar': True})


from datetime import datetime, timedelta

def email_alerts(request):
    # Retrieve page size from request, default to 10 if not provided or invalid
    page_size = int(request.GET.get('page_size', 10))
    
    # Calculate default start and end dates (one month ago from today)
    default_end_date = datetime.now().strftime('%Y-%m-%d')
    default_start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # Retrieve all email alerts from the database
    alerts_list = AlertData.objects.all()

    # Paginate the alerts with the specified page size
    paginator = Paginator(alerts_list, page_size)
    page = request.GET.get('page')

    try:
        alerts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        alerts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        alerts = paginator.page(paginator.num_pages)

    return render(request, 'monitoring/email_alerts.html', {'alerts': alerts, 'page_size': page_size, 'default_start_date': default_start_date, 'default_end_date': default_end_date, 'show_navbar': True})
