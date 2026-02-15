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

BASE_URL = 'http://127.0.0.1:8000/'

KAKAO_CALLBACK_URI = BASE_URL + 'users/kakao/callback/'

def kakao_login(request):
    client_id = os.environ.get('KAKAO_REST_API_KEY')
    return redirect(f'https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code')

def kakao_callback(request):
    client_id = os.environ.get('KAKAO_REST_API_KEY')
    client_secret = os.environ.get('KAKAO_SECRET_KEY')
    code = request.GET.get('code', None)

    if code is None:
        return JsonResponse({'ERROR': 'failed to get code'}, status=400)

    token_request       = requests.get(f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}&client_secret={client_secret}')
    token_response_json = token_request.json()

    access_token = token_response_json.get('access_token')

    profile_request = requests.post(
        'https://kapi.kakao.com/v2/user/me',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    profile_json = profile_request.json()

    kakao_account = profile_json.get('kakao_account')

    name = kakao_account.get('profile').get('nickname')

    latest_data = User.objects.latest('id')
    latest_email_num = latest_data.email.split("@")[0][-1]

    if User.objects.filter(name=name):
        return JsonResponse({'ERROR' : 'Duplicate Name'}, status=400)

    # temporary for backend usage only until frontend is figured
    password = '12345678'

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # only for kakao since retrieving email is currently unavailable
    if User.objects.filter(email='test1@naver.com').exists():
        User.objects.create(
            name     = name,
            email    = 'test' + str(latest_email_num + 1) + '@naver.com',
            password = hashed_password,
        )
    else:
        User.objects.create(
            name     = name,
            email    = 'test1@naver.com',
            password = hashed_password,
        )

    return JsonResponse({'MESSAGE': name}, json_dumps_params={'ensure_ascii':False}, status=200)

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