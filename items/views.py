import json

from django.views               import View
from django.http                import JsonResponse
from django.core.cache          import cache
from django.core.exceptions     import ValidationError
from django.core.serializers    import serialize
from django.core.paginator      import Paginator
from django.db                  import transaction, DatabaseError

from .models                    import Item, Category, Review
from core.utils                 import authorization

# Create your views here.
class ItemView(View):
    def get(self, request):
        try:
            name = request.GET.get('name', None)
            page = request.GET.get('page', 1)

            global_version = cache.get('item_list_version', 1)

            if name:
                cache_key = f"item_search:v{global_version}:{name}:page:{page}"
            else:
                cache_key = f"item_list:{global_version}:total:page:{page}"

            cached_result = cache.get(cache_key)

            if cached_result:
                return JsonResponse({'MESSAGE': 'SUCCESS (CACHE)', 'RESULT': cached_result}, status=200)

            if name:
                items = Item.objects.filter(name__icontains=name)
            else:
                items = Item.objects.all().order_by('-created_at')

            paginator = Paginator(items, 20)
            items_page = paginator.get_page(page)

            result = []
            for item in items_page:
                image_url = item.image.url if item.image else None
                result.append({
                    'id'            : item.id,
                    'name'          : item.name,
                    'price'         : item.price,
                    'quantity'      : item.quantity,
                    'image_url'     : image_url,
                    'created_at'    : item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'modified_at'   : item.modified_at.strftime('%Y-%m-%d %H:%M:%S')
                })

            cache.set(cache_key, result, timeout=600)

            return JsonResponse({
                'MESSAGE'       : 'SUCCESS (DB)',
                'RESULT'        : result,
                'TOTAL_COUNT'   : paginator.count,
                'TOTAL_PAGES'   : paginator.num_pages,
                'CURRENT_PAGE'  : items_page.number
            }, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

        except Exception as e:
            return JsonResponse({'ERROR': str(e)}, status=400)

    @authorization
    def post(self, request):
        try:
            category_id = request.POST['category_id']
            name        = request.POST['name']
            price       = request.POST['price']
            quantity    = request.POST['quantity']
            image_file  = request.FILES.get('image')

            if not name or not price or not quantity:
                return JsonResponse({'ERROR': 'EMPTY_VALUE'}, status=400)

            category = Category.objects.get(id=category_id)

            if Item.objects.filter(name=name).exists():
                return JsonResponse({'ERROR': 'ITEM_ALREADY_EXISTS'}, status=400)

            Item.objects.create(
                category    = category,
                name        = name,
                price       = price,
                quantity    = quantity,
                image       = image_file,
            )

            try:
                cache.incr('item_list_version')
            except ValueError:
                cache.set('item_list_version', 1)

            return JsonResponse({'MESSAGE': 'CREATED'}, status=201)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @authorization
    def patch(self, request, item_id):
        try:
            item_id = item_id

            with transaction.atomic():
                item = Item.objects.select_for_update(nowait=True).get(id=item_id)

                update_fields = ['name', 'price', 'quantity']
                fields_to_save = []

                updated_data_exists = False

                for field in update_fields:
                    val = request.POST.get(field)
                    if val is not None:
                        setattr(item, field, val)
                        fields_to_save.append(field)
                        updated_data_exists = True

                image_file = request.FILES.get('image')
                if image_file:
                    item.image = image_file
                    fields_to_save.append('image')
                    updated_data_exists = True

                if updated_data_exists:
                    item.save(update_fields=fields_to_save)
                    cache.incr('item_list_version')

                    return JsonResponse({'MESSAGE': 'UPDATED'}, status=200)

            return JsonResponse({'MESSAGE': 'NO_CHANGES_WERE_MADE'}, status=200)

        except DatabaseError as e:
            return JsonResponse({'ERROR': 'ITEM_UNDER_MODIFICATION'}, status=409)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @authorization
    def delete(self, request):
        try:
            data = json.loads(request.body)

            item_name = data['name']

            item = Item.objects.filter(name=item_name)

            if item.exists():
                item.delete()

                return JsonResponse({'MESSAGE': 'Deleted'}, status=200)

            else:
                return JsonResponse({'ERROR': 'Item does not exist'}, status=400)

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)

class SearchItemView(View):
    def get(self, request):
        try:
            item_name = request.GET.get('name', None)

            result = Item.objects.filter(name__icontains=item_name)

            serialized_data = serialize('json', result)
            serialized_data = json.loads(serialized_data)

            return JsonResponse({'MESSAGE' : 'SUCCESS', 'RESULT' : serialized_data[0]['fields']}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)

class ReviewView(View):
    def get(self, request):
        try:
            item_name = request.GET.get('name', None)

            review_found = Review.objects.filter(item__name=item_name)

            serialized_data = serialize('json', review_found)
            serialized_data = json.loads(serialized_data)

            return JsonResponse({'MESSAGE' : 'SUCCESS', 'RESULT' : serialized_data[0]['fields']})

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)

    @authorization
    def post(self, request):
        try:
            data = json.loads(request.body)

            user = request.user

            body = data['body']

            item_name = request.GET.get('name', None)
            item = Item.objects.get(name=item_name)

            Review.objects.create(
                item = item,
                user = user,
                body = body
            )

            return JsonResponse({'MESSAGE' : 'Created'}, status=201)

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)

    @authorization
    def patch(self, request):
        try:
            data = json.loads(request.body)

            user = request.user

            item_name = request.GET.get('name', None)

            review = Review.objects.get(item__name=item_name, user=user)

            review.body = data['body']
            review.save()

            return JsonResponse({'MESSAGE': 'Updated'}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @authorization
    def delete(self, request):
        try:
            user = request.user

            item_name = request.GET.get('name', None)

            review = Review.objects.filter(item__name=item_name, user=user)

            if review.exists():
                review.delete()

                return JsonResponse({'MESSAGE': 'Deleted'}, status=200)

            else:
                return JsonResponse({'ERROR': 'Review does not exist'}, status=400)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)