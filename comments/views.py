import json

from django.http                import JsonResponse
from django.core.exceptions     import ValidationError
from rest_framework.views       import APIView
from drf_spectacular.utils      import extend_schema

from posts.models import Post
from .models        import Comment
from core.utils     import authorization
from rest_framework import serializers

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'replies']

    def get_replies(self, obj):
        if obj.parent_id is None:
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class CommentView(APIView):
    """
    댓글 관리 API
    """

    @extend_schema(
        summary="댓글 목록 조회",
        description="특정 게시글의 모든 댓글과 대댓글을 계층 구조로 조회합니다.",
        responses={200: CommentSerializer(many=True)}
    )
    def get(self, request, post_id):
        try:
            parent_comments = Comment.objects.filter(post_id=post_id, parent=None).prefetch_related('replies')
            serializer = CommentSerializer(parent_comments, many=True)

            return JsonResponse({'comments' : serializer.data}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)
        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @extend_schema(
        summary="댓글 작성",
        description="게시글에 새로운 댓글을 작성합니다. parent_id를 포함하면 해당 댓글의 대댓글로 등록됩니다.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'text': {'type': 'string', 'description': '댓글 내용'},
                    'parent_id': {'type': 'integer', 'description': '부모 댓글 ID (대댓글일 경우)', 'nullable': True}
                },
                'required': ['text']
            }
        }
    )
    @authorization
    def post(self, request, post_id):
        try:
            data        = json.loads(request.body)
            user        = request.user
            text        = data['text']
            parent_id   = data.get('parent_id')

            Comment.objects.create(
                text        = text,
                user_id     = user.id,
                post_id     = post_id,
                parent_id   = parent_id
            )

            return JsonResponse({'MESSAGE' : 'Created'}, status=201)

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)
        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)