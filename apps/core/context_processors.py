from .models import SiteSetting

def site_settings_processor(request):
    """
    Makes site-wide settings and basic navigation accessible in all templates.
    """
    try:
        settings_obj = SiteSetting.load()
    except Exception:
        settings_obj = None

    return {
        'site_setting': settings_obj,
    }
