import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # move it to os.getenv
    CELERY_BROKER_URL ="redis://localhost:6379" 
    RESULT_BACKEND ="redis://localhost:6379" 

    DATA_PATH="input"
    moving_average_conf=[
        {
            'days':5,
            'type':'exponential',
            'label':'EMA5'
        },
        {
            'days':20,
            'type':'simple',
            'label':'SMA20'
        }]

    tsi_conf=[
        {
            'days':7,
            'label':'TSI-7'
        },
        {
            'days':8,
            'label':'TSI-8'
        },
        {
            'days':9,
            'label':'TSI-9'
        },
        {
            'days':10,
            'label':'TSI-10'
        },
        {
            'days':11,
            'label':'TSI-11'
        },
        {
            'days':12,
            'label':'TSI-12'
        }

        
    ]

    PRICE_COL='Close'
    # DB_HOSTNAME="73.10.33.109"
    # DB_USERNAME="dbuser"
    # DB_PASSWORD="admin"
    # DB_DATABASE="stockDB"

    DB_HOSTNAME="localhost"
    DB_USERNAME="dbuser"
    DB_PASSWORD="admin"
    DB_DATABASE="stockDB"
    DB_PORT=5432
    FLASK_PORT=5000
    SECRET_KEY = os.getenv('SECRET_KEY', default='A very terrible secret key.')
 
    swagger_url="swagger/ui/index"

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_PORT=5000
    DB_LOCAL_HOSTNAME="localhost"
    DB_LOCAL_USERNAME="postgres"
    DB_LOCAL_PASSWORD="admin"
    DB_LOCAL_DATABASE="stockDB"
    DB_LOCAL_PORT=5432