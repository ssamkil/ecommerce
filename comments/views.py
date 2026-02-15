import json

from django.http                import JsonResponse
from django.core.exceptions     import ValidationError
from rest_framework.views       import APIView

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
    def get(self, request, post_id):
        try:
            parent_comments = Comment.objects.filter(post_id=post_id, parent=None).prefetch_related('replies')
            serializer = CommentSerializer(parent_comments, many=True)

            return JsonResponse({'comments' : serializer.data}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

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