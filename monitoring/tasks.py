from apscheduler.schedulers.background import BackgroundScheduler
from .firebase import get_data_from_firebase
from .models import QecData, QtaData, QscData, AlertData
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import math  # Import the math module
from django.core.exceptions import ObjectDoesNotExist
from .models import EmailSettings


def send_email_alert(temperature, humidity, database_key):
    try:
        # Attempt to fetch the latest email settings from the database
        email_setting = EmailSettings.objects.latest('id')
        sender_email = email_setting.sender_email
        receiver_email = email_setting.receiver_email
        password = email_setting.password  # Assuming you store the password here, consider securing this properly
    except ObjectDoesNotExist:
        # Fallback to default values or handle the absence of settings appropriately
        print("No email settings found. Please configure them in the admin panel.")
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = "Alert: Temperature/Humidity Out of Range"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Convert database_key to uppercase for the email body
    database_key_upper = database_key.upper()
    
    text = f"""\
    Hi,
    An alert condition was detected in the {database_key_upper} Server Room !!!
    Temperature: {temperature}
    Humidity: {humidity}
    Please check the server of {database_key_upper}."""
    
    part = MIMEText(text, "plain")
    message.attach(part)
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

   # Save alert data to database
    AlertData.objects.create(
        temperature=temperature,
        humidity=humidity,
        database_key=database_key,
        sender_email=sender_email,
        receiver_email=receiver_email,
        message=text,  # Save the plain text content of the message
        date=datetime.datetime.now().date(),  # Add the current date
        time=datetime.datetime.now().time()  # Add the current time
    )
      
    
def fetch_and_save_data():
    model_mapping = {
        'qec': QecData,
        'qsc': QscData,
        'qta': QtaData,
    }
    
    for database_key in ['qec', 'qsc', 'qta']:
        data = get_data_from_firebase(database_key)
        for key, value in data.items():
            
            # Check if temperature or humidity is NaN and replace with 0.0
            temperature = float(value['temperature']) if not math.isnan(float(value['temperature'])) else 0.0
            humidity = float(value['humidity']) if not math.isnan(float(value['humidity'])) else 0.0
            
            # Save the data as before
            model = model_mapping.get(database_key)
            if model:
                model.objects.create(
                    date=datetime.datetime.strptime(value['date'], "%Y-%m-%d").date(),
                    time=datetime.datetime.strptime(value['time'], "%H:%M:%S").time(),
                    temperature=temperature,
                    humidity=humidity
                )

            # Send an email if the conditions are met
            if (temperature > 27 or temperature < 18) or (humidity > 60 or humidity < 40):
                send_email_alert(temperature, humidity, database_key)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_save_data, 'interval', minutes=30)  # Adjusted back to a more reasonable interval
    scheduler.start()
