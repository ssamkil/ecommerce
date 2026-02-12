import json, math

from django.views               import View
from django.http                import JsonResponse
from django.core.exceptions     import ValidationError

from .models                    import Post
from core.utils                 import authorization

class PostView(View):
    def get(self, request):
        try:
            data    = json.loads(request.body)

            post_id = data['id']

            post    = Post.objects.get(id=post_id)

            return JsonResponse({'title': post.title, 'body': post.body}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @authorization
    def post(self, request):
        try:
            data    = json.loads(request.body)

            user    = request.user

            title   = data['title']
            body    = data['body']
            user_id = user.id

            Post.objects.create(
                title   = title,
                body    = body,
                user_id = user_id
            )

            return JsonResponse({'MESSAGE': 'CREATED'}, status=201)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @authorization
    def patch(self, request):
        try:
            data    = json.loads(request.body)

            user    = request.user

            post_id = data['id']
            user_id = user.id

            post    = Post.objects.get(id=post_id)

            if not post.user_id == user_id:
                return JsonResponse({'ERROR': 'Not permitted to update this post'}, status=400)

            post.title = data['title']
            post.body = data['body']

            post.save()

            return JsonResponse({'MESSAGE': 'UPDATED'}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @authorization
    def delete(self, request):
        try:
            data    = json.loads(request.body)

            user    = request.user

            post_id = data['id']
            user_id = user.id

            post    = Post.objects.get(id=post_id)

            if not post.user_id == user_id:
                return JsonResponse({'ERROR': 'NOT_PERMITTED_TO_DELETE_THIS_POST'}, status=400)

            post.delete()

            return JsonResponse({'MESSAGE': 'DELETED'}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

class PostListView(View):
    def get(self, request, page_num):
        try:
            post_list      = Post.objects.all().order_by('id')
            page           = int(request.GET.get('page', page_num))
            page_size      = 3
            limit          = int(page_size * page)
            offset         = int(limit - page_size)

            total_items    = post_list.count()
            total_pages    = math.ceil(total_items / page_size)
            product_offset = list(post_list[offset:limit].values())

            return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': product_offset, 'PAGES_TOTAL': total_pages, 'ITEMS_TOTAL': total_items}, status=200)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

        except ValueError:
            return JsonResponse({'ERROR': 'INVALID_PARAMETER'}, status=400)