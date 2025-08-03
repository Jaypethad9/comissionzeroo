from .models import Review
from django.db.models import Avg

def provider_avg_rating(request):
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'provider':
        avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
        return {'avg_rating': round(avg_rating or 0, 1)}
    return {}
