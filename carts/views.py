import json

from django.http            import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models       import F, Sum
from rest_framework.views   import APIView
from drf_yasg.utils import swagger_auto_schema

from core.utils             import authorization
from .models                import Cart
from items.models           import Item

class CartView(APIView):
    """
    장바구니 관리 API
    - 장바구니 담기, 조회, 수량 수정, 삭제 기능을 제공합니다.
    """
    @authorization
    @swagger_auto_schema(operation_description="장바구니에 담긴 상품 목록을 불러옵니다.")
    def get(self, request):
        try:
            user = request.user

            carts = Cart.objects.filter(user=user).select_related('item')

            if not carts.exists():
                return JsonResponse({'ERROR': 'CART_DOES_NOT_EXIST'}, status=400)

            cart_total = [{
                'cart_id': cart.id,
                'name': cart.item.name,
                'price': cart.item.price,
                'quantity': cart.quantity,
                'image': cart.item.image.url if cart.item.image else None,
            } for cart in carts]

            price_total = carts.aggregate(total=Sum(F('item__price') * F('quantity')))
            total_price = price_total['total'] if price_total['total'] else 0

            return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': cart_total, 'TOTAL_PRICE': total_price}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @authorization
    @swagger_auto_schema(operation_description="상품을 장바구니에 추가합니다.")
    def post(self, request):
        """
        상품을 장바구니에 추가합니다.
        - 동일한 상품이 이미 있을 경우 수량만 증가시킵니다.
        """
        try:
            data = json.loads(request.body)
            user = request.user

            item_id = data['id']
            quantity = int(data['quantity'])

            try:
                item = Item.objects.get(id=item_id)
            except Item.DoesNotExist:
                return JsonResponse({'ERROR': 'ITEM_DOES_NOT_EXIST'}, status=404)

            if quantity > Item.objects.get(id=item_id).quantity:
                return JsonResponse({'ERROR': 'ITEM_STOCK_UNAVAILABLE'}, status=400)

            cart, created = Cart.objects.get_or_create(
                user     = user,
                item     = item,
                defaults = {'quantity': quantity}
            )

            if not created:
                cart.quantity += quantity
                cart.save()
                return JsonResponse({'MESSAGE': 'UPDATED'}, status=200)

            return JsonResponse({'MESSAGE': 'CREATED'}, status=201)

        except ValidationError as e:
            return JsonResponse({'ERROR': e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @authorization
    def delete(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            cart_id = data['id']

            cart = Cart.objects.get(id=cart_id, user=user)
            cart.delete()

            return JsonResponse({'MESSAGE': 'DELETED'}, status=200)

        except Cart.DoesNotExist:
            return JsonResponse({'ERROR': 'CART_DOES_NOT_EXIST'}, status=404)

        except KeyError:
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)