import json, jwt, bcrypt
from dotenv                          import load_dotenv
from django.http                     import JsonResponse
from django.core.exceptions          import ValidationError
from django.shortcuts                import render
from rest_framework.views            import APIView
from drf_spectacular.utils           import extend_schema, OpenApiResponse
from .models                         import User
from .validators                     import Validator
from my_settings                     import SECRET_KEY, ALGORITHM

load_dotenv()

def index(request):
    return render(request, 'user/index.html', {})

class SignUpView(APIView):
    """
    회원가입 API
    """

    @extend_schema(
        summary="사용자 회원가입",
        description="새로운 사용자를 등록합니다. 이메일 형식과 비밀번호 복잡성 유효성 검사를 포함합니다.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': '사용자 이름'},
                    'email': {'type': 'string', 'description': '이메일 주소(ID)'},
                    'password': {'type': 'string', 'description': '비밀번호'}
                },
                'required': ['name', 'email', 'password']
            }
        },
        responses={
            201: OpenApiResponse(description="회원가입 성공"),
            400: OpenApiResponse(description="중복된 계정 또는 유효성 검사 실패")
        }
    )
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
    """
    로그인 API
    """

    @extend_schema(
        summary="사용자 로그인",
        description="이메일과 비밀번호를 확인하여 JWT 인증 토큰을 발급합니다.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['email', 'password']
            }
        },
        responses={
            200: OpenApiResponse(description="로그인 성공 및 토큰 발급"),
            401: OpenApiResponse(description="등록되지 않은 이메일"),
            400: OpenApiResponse(description="비밀번호 불일치 또는 유효성 검사 실패")
        }
    )
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