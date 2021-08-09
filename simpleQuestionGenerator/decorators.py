from django.shortcuts import redirect
from django.contrib.auth import logout


def unauthenticated_Creator(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('creatorPage')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_Creator(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                logout(request)
                return redirect('signIn')

        return wrapper_func
    return decorator
