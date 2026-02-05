import jwt

from django.http            import JsonResponse

from users.models           import User
from my_settings            import SECRET_KEY, ALGORITHM

def authorization(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            token        = request.headers.get('Authorization')

            if not token:
                return JsonResponse({'ERROR' : 'Token required'}, status = 401)

            payload      = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            request.user = User.objects.get(id=payload['id'])

            return func(self, request, *args, **kwargs)

        except jwt.exceptions.DecodeError:
            return JsonResponse({'ERROR' : 'Invalid token'}, status = 401)

        except User.DoesNotExist:
            return JsonResponse({'ERROR' : 'Invalid User'}, status = 401)

    return wrapper