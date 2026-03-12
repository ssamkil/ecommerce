import json, jwt, bcrypt, os, requests

from dotenv                          import load_dotenv

from django.http                     import JsonResponse
from django.core.exceptions          import ValidationError
from django.shortcuts                import render, redirect
from rest_framework.views            import APIView

from .models                         import User
from .validators                     import Validator
from my_settings                     import SECRET_KEY, ALGORITHM

load_dotenv()

def index(request):
    return render(request, 'user/index.html', {})

class SignUpView(APIView):
    def post(self, request):
        try:
            data     = json.loads(request.body)
            name     = data['name']
            email    = data['email']
            password = data['password']

            if User.objects.filter(email=email).exists():
                return JsonResponse({'ERROR': 'ACCOUNT_ALREADY_EXISTS'}, status=400)

            validator = Validator()
            validator.validate_email(email)
            validator.validate_password(password)

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            User.objects.create(
                name     = name,
                email    = email,
                password = hashed_password
            )

            return JsonResponse({'MESSAGE': 'CREATED'}, status=201)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

class SignInView(APIView):
    def post(self, request):
        try:
            data            = json.loads(request.body)

            email           = data['email']
            password        = data['password']

            validator = Validator()
            validator.validate_email(email)
            validator.validate_password(password)

            user            = User.objects.get(email=email)
            hashed_password = user.password.encode('utf-8')

            if not bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return JsonResponse({'ERROR': 'FAILED_TO_LOGIN'}, status=400)

            payload = {'id' : user.id}
            token   = jwt.encode(payload, SECRET_KEY, ALGORITHM)

            return JsonResponse({'MESSAGE': 'SUCCESS', 'TOKEN': token}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'ERROR': 'INVALID_USER'}, status=401)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)