import json

from django.http            import JsonResponse
from django.views           import View
from django.core.exceptions import ValidationError
from django.db.models       import F, Sum

from core.utils             import authorization
from .models                import Cart
from items.models           import Item

class CartView(View):
    @authorization
    def get(self, request):
        try:
            user = request.user

            if not Cart.objects.filter(user_id=user.id).exists():
                return JsonResponse({'ERROR' : 'Cart does not exist'}, status=400)

            carts = Cart.objects.filter(user=user).select_related('item')

            cart_total = [{
                'cart_id' : cart.id,
                'name' : cart.item.name,
                'price' : cart.item.price,
                'quantity' : cart.quantity,
                'image' : cart.item.image,
            } for cart in carts]

            price_total = carts.aggregate(price_total=Sum(F('item__price') * F('quantity')))

            return JsonResponse({'MESSAGE' : 'SUCCESS', 'RESULT' : cart_total, 'PRICE_TOTAL' : price_total}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)

    @authorization
    def post(self, request):
        try:
            data = json.loads(request.body)

            user = request.user
            user_id = user.id

            item_id = data['id']
            quantity = data['quantity']

            if not Item.objects.filter(id=item_id):
                return JsonResponse({'ERROR' : 'Item does not exist'}, status=400)

            if quantity > Item.objects.get(id=item_id).quantity:
                return JsonResponse({'ERROR' : 'Item stock unavailable'}, status=400)

            cart, created = Cart.objects.get_or_create(
                user_id = user_id,
                item_id = item_id,
                defaults = {'quantity' : quantity}
            )

            if not created:
                cart.quantity += quantity
                cart.save()
                return JsonResponse({'MESSAGE' : 'Updated'}, status=200)

            return JsonResponse({'MESSAGE' : 'Created'}, status=201)

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)

    @authorization
    def delete(self, request):
        try:
            data = json.loads(request.body)

            user = request.user

            cart_id = data['id']

            if not Cart.objects.filter(id=cart_id).exists():
                return JsonResponse({'ERROR' : 'Cart does not exist'}, status=400)

            cart = Cart.objects.get(
                id=cart_id,
                user__id=user.id
            )
            cart.delete()

            return JsonResponse({'MESSAGE' : 'Deleted'}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)