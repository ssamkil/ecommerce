import json, math
from django.http                import JsonResponse
from rest_framework.views       import APIView
from drf_spectacular.utils      import extend_schema, OpenApiParameter, OpenApiTypes
from .models                    import Post
from core.utils                 import authorization

class PostView(APIView):
    """
    게시글 관리 API
    """

    @extend_schema(
        summary="게시글 조회",
        description="ID를 통한 단일 게시글 조회 또는 페이지네이션이 적용된 목록 조회를 수행합니다.",
        parameters=[
            OpenApiParameter(name='id', description='조회할 게시글 ID (단일 조회 시)', required=False, type=int),
            OpenApiParameter(name='page', description='페이지 번호 (목록 조회 시, 기본값: 1)', required=False, type=int),
        ]
    )
    def get(self, request):
        post_id = request.GET.get('id')
        if post_id:
            try:
                post = Post.objects.get(id=post_id)
                return JsonResponse({'TITLE': post.title, 'BODY': post.body}, status=200)

            except Post.DoesNotExist:
                return JsonResponse({'ERROR': 'POST_DOES_NOT_EXIST'}, status=404)

        else:
            try:
                page_size = 3
                page = int(request.GET.get('page', 1))

                if page < 1:
                    page = 1

                post_query  = Post.objects.all().order_by('-id')
                total_items = post_query.count()

                limit       = page_size * page
                offset      = limit - page_size
                total_pages = math.ceil(total_items / page_size)

                posts = list(post_query[offset:limit].values('id', 'title', 'user__name', 'created_at'))

                return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': posts, 'PAGES': {'CURRENT': page, 'TOTAL': total_pages}}, status=200)

            except ValueError:
                return JsonResponse({'ERROR': 'INVALID_PAGE_NUMBER'}, status=400)

    @extend_schema(
        summary="게시글 작성",
        description="새로운 게시글을 작성합니다.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': '게시글 제목'},
                    'body': {'type': 'string', 'description': '게시글 본문'}
                },
                'required': ['title', 'body']
            }
        }
    )
    @authorization
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = request.user

            Post.objects.create(
                title   = data['title'],
                body    = data['body'],
                user_id = user.id
            )

            return JsonResponse({'MESSAGE': 'CREATED'}, status=201)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'ERROR': 'JSON_DECODE_ERROR'}, status=400)

    @extend_schema(
        summary="게시글 수정",
        description="본인이 작성한 게시글의 제목이나 본문을 수정합니다.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'description': '수정할 게시글 ID'},
                    'title': {'type': 'string', 'description': '수정할 제목'},
                    'body': {'type': 'string', 'description': '수정할 본문'}
                },
                'required': ['id']
            }
        },
        responses={
            200: OpenApiTypes.OBJECT,
            403: {"description": "작성자가 아님"},
            404: {"description": "게시글 없음"}
        }
    )
    @authorization
    def patch(self, request):
        try:
            data    = json.loads(request.body)
            user    = request.user
            post_id = data['id']

            post    = Post.objects.get(id=post_id)

            if post.user_id != user.id:
                return JsonResponse({'ERROR': 'NOT_PERMITTED_TO_UPDATE_THIS_POST'}, status=403)

            if 'title' in data:
                post.title = data['title']

            if 'body' in data:
                post.body = data['body']

            post.save()

            return JsonResponse({'MESSAGE': 'UPDATED'}, status=200)

        except Post.DoesNotExist:
            return JsonResponse({'ERROR': 'POST_DOES_NOT_EXIST'}, status=404)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @extend_schema(
        summary="게시글 삭제",
        description="본인이 작성한 게시글을 삭제합니다.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer', 'description': '삭제할 게시글 ID'}
                },
                'required': ['id']
            }
        },
        responses={
            200: OpenApiTypes.OBJECT,
            403: {"description": "작성자가 아님"},
            404: {"description": "게시글 없음"}
        }
    )
    @authorization
    def delete(self, request):
        try:
            data    = json.loads(request.body)
            user    = request.user
            post_id = data['id']

            post    = Post.objects.get(id=post_id)

            if post.user_id != user.id:
                return JsonResponse({'ERROR': 'NOT_PERMITTED_TO_DELETE_THIS_POST'}, status=403)

            post.delete()

            return JsonResponse({'MESSAGE': 'DELETED'}, status=200)

        except Post.DoesNotExist:
            return JsonResponse({'ERROR': 'POST_DOES_NOT_EXIST'}, status=404)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)