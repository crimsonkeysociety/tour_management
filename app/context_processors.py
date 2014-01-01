def style_protocol(request):
    from django.conf import settings
    return {'style_protocol': settings.STYLE_PROTOCOL}