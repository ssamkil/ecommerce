import json
from datetime                   import datetime

from django.views               import View
from django.http                import JsonResponse
from django.core.exceptions     import ValidationError
from django.core.serializers    import serialize
from django.db                  import transaction

from .models                    import Item, Category, Review
from core.utils                 import authorization

# Create your views here.
class ItemView(View):
    def get(self, request):
        try:
            name = request.GET.get('name', None)

            item_found = Item.objects.filter(name=name)

            serialized_data = serialize('json', item_found)
            serialized_data = json.loads(serialized_data)

            created_at_str = serialized_data[0]['fields']['created_at']
            created_at_obj = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
            modified_at_str = serialized_data[0]['fields']['created_at']
            modified_at_obj = datetime.strptime(modified_at_str, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')

            serialized_data[0]['fields']['created_at'] = created_at_obj
            serialized_data[0]['fields']['modified_at'] = modified_at_obj

            return JsonResponse({'MESSAGE' : 'SUCCESS', 'RESULT' : serialized_data[0]['fields']}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)

    @authorization
    def post(self, request):
        try:
            data  = json.loads(request.body)

            category_id = data['category_id']
            name        = data['name']
            price       = data['price']
            quantity    = data['quantity']
            image_url   = data['image_url']

            category = Category.objects.get(id=category_id)

            if Item.objects.filter(name=name).exists():
                return JsonResponse({'ERROR' : 'Item already exist'}, status=400)

            Item.objects.create(
                category    = category,
                name        = name,
                price       = price,
                quantity    = quantity,
                image_url   = image_url,
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
            item_id = data['id']

            with transaction.atomic():
                item = Item.objects.select_for_update().get(id=item_id)

                update_fields = ['name', 'price', 'quantity', 'image_url']
                fields_to_save = []

                updated_data_exists = False

                for field in update_fields:
                    if field in data:
                        setattr(item, field, data[field])
                        fields_to_save.append(field)
                        updated_data_exists = True

                if updated_data_exists:
                    item.save(update_fields=fields_to_save)
                    return JsonResponse({'MESSAGE' : 'UPDATED'}, status=200)

            return JsonResponse({'MESSAGE' : 'NO CHANGES WERE MADE'}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)

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