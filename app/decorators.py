from django.shortcuts import redirect

def no_firefox(view_func):
    """
    Make another a function more beautiful.
    """
    def _decorated(request, *args, **kwargs):
    	if request.META['HTTP_USER_AGENT'].lower().find('firefox') != -1:
    		return redirect('unsupported-browser-url')
        return view_func(*args, **kwargs)
    return _decorated