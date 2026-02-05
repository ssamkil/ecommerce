import json

from django.views   import View
from django.http                import JsonResponse
from django.core.exceptions     import ValidationError

from posts.models import Post
from .models        import Comment
from core.utils     import authorization

class CommentView(View):
    def get(self, request):
        try:
            data = json.loads(request.body)
            comment_id = data['id']

            comment = Comment.objects.get(id=comment_id)

            return JsonResponse({'text : ' : comment.text}, status=200)

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