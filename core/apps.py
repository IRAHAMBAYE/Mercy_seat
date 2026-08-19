import sys
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """
        Runs automatically on server initialization. Tells Railway to
        silently execute database migrations right before serving web pages.
        """
        # Prevents execution loops during administrative management operations
        if 'migrate' not in sys.argv and 'makemigrations' not in sys.argv and 'collectstatic' not in sys.argv:
            try:
                from django.core.management import call_command
                print("⛪ Cloud DB Sync Node: Executing automated model migrations...")
                call_command('migrate', interactive=False, sys_stdout=sys.stdout)
                print("✨ Cloud DB Sync Node: Live tables synchronized successfully.")
            except Exception as e:
                print(f"⚠️ Cloud DB Sync Node: Migration skip condition handled: {str(e)}")
