from askomics.app import create_app, create_celery

application = create_app(config='config/askomics.ini')
celery = create_celery(application)

if __name__ == '__main__':
    application.run()
