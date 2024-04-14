import firebase_admin
from firebase_admin import credentials, db

def init_firebase():
    configs = {
        'qec': {
            'databaseURL': "https://qec-monitoring-default-rtdb.asia-southeast1.firebasedatabase.app/",
            'credential': credentials.Certificate("qec-firebase-key.json")
        },
        'qsc': {
            'databaseURL': "https://qsc-monitoring-default-rtdb.asia-southeast1.firebasedatabase.app/",
            'credential': credentials.Certificate("qsc-firebase-key.json")
        },
        'qta': {
            'databaseURL': "https://qta-monitoring-default-rtdb.asia-southeast1.firebasedatabase.app/",
            'credential': credentials.Certificate("qta-firebase-key.json")
        }
    }

    firebase_apps = {}
    for key, config in configs.items():
        firebase_apps[key] = firebase_admin.initialize_app(config['credential'], {
            'databaseURL': config['databaseURL']
        }, name=key)
    
    return firebase_apps

firebase_apps = init_firebase()

def get_data_from_firebase(database_key):
    ref = db.reference('/', app=firebase_apps[database_key])
    data = ref.get()
    return data