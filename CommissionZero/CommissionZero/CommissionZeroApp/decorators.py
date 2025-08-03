from functools import wraps
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            redirect_url = '/'
            if hasattr(user, 'providerprofile'):
                role = 'provider'
                redirect_url = '/service_dashboard/'
            elif hasattr(user, 'customerprofile'):
                role = 'customer'
                redirect_url = '/customer_dashboard/'
            elif user.is_superuser:
                role = 'admin'
                redirect_url = '/admin_dashboard/'
            else:
                role = 'unknown'

            if role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return render(request, 'CommissionZeroApp/permission_denied.html', {
                'dashboard_url': redirect_url,
                'timer': 5
            })
        return _wrapped_view
    return decorator
