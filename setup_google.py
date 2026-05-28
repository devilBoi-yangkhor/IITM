# fix_google_auth.py
import os
import django
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'training_institute.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

def fix_google_auth():
    print("🔧 Fixing Google Authentication...")
    
    # Delete ALL existing Google apps
    google_apps = SocialApp.objects.filter(provider='google')
    count = google_apps.count()
    google_apps.delete()
    print(f"✅ Deleted {count} duplicate Google app(s)")
    
    # Get or create site
    site, _ = Site.objects.get_or_create(
        id=1,
        defaults={'domain': 'localhost:8000', 'name': 'localhost'}
    )
    
    # Create single Google app
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        name='Google',
        defaults={
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
        }
    )
    
    # Clear existing sites and add the current one
    app.sites.clear()
    app.sites.add(site)
    app.save()
    
    print(f"✅ {'Created' if created else 'Updated'} Google app")
    print(f"   ID: {app.id}")
    print(f"   Client ID: {app.client_id[:30]}...")
    print(f"   Sites: {', '.join([s.domain for s in app.sites.all()])}")
    
    # Verify
    verify_apps = SocialApp.objects.filter(provider='google')
    print(f"\n📊 Final check: {verify_apps.count()} Google app(s) in database")
    
    if verify_apps.count() == 1:
        print("🎉 PERFECT! Single Google app configured correctly")
    else:
        print("⚠️ Still have issues - run again or check admin panel")

if __name__ == '__main__':
    fix_google_auth()