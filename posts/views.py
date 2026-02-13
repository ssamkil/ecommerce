import json, math

from django.views               import View
from django.http                import JsonResponse
from django.core.exceptions     import ValidationError

from .models                    import Post
from core.utils                 import authorization

class PostView(View):
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