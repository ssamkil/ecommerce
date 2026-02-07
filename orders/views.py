import json, uuid

from core.utils             import authorization
from carts.models           import Cart
from .models                import Order, OrderItem, OrderStatus
from items.models           import Item

from django.http            import JsonResponse
from django.views           import View
from django.db              import transaction, IntegrityError
from django.db.models       import F, Sum
from django.core.exceptions import ValidationError

class OrderView(View):
    @authorization
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            address = data['address']

            order = Order.objects.create(
                user=user,
                address=address,
                order_number=str(uuid.uuid4()),
                order_status_id=OrderStatus.Status.PENDING
            )
            try:
                with transaction.atomic():
                    carts = Cart.objects.filter(
                        user=user
                    ).select_related(
                        'item'
                    ).annotate(
                        price = Sum(F('item__quantity') * F('item__price'))
                    )

                    if not carts.exists():
                        return JsonResponse({'MESSAGE' : 'EMPTY_CART'}, status=400)

                    cart_items = list(carts)
                    item_ids = [cart.item.id for cart in cart_items]

                    locked_item = Item.objects.select_for_update().filter(id__in=item_ids)  # 데이터 잠금 - 여러명이 동시 주문시 문제 발생
                    item_map = {item.id: item for item in locked_item}

                    order_items = []

                    for cart in cart_items:
                        item = item_map.get(cart.item.id)

                        if item.quantity < cart.quantity:
                            raise IntegrityError(f'INSUFFICIENT_STOCK : {item.name}')

                        item.quantity -= cart.quantity
                        item.save()

                        order_items.append(OrderItem(
                            item=cart.item,
                            order=order,
                            quantity=cart.quantity
                        ))

                    Cart.objects.filter(user=user).delete()

                    OrderItem.objects.bulk_create(order_items)

                    order.order_status_id = OrderStatus.Status.COMPLETED
                    order.save()

                    return JsonResponse({'MESSAGE': 'Created'}, status=201)

            except Exception as e:
                order.order_status_id = OrderStatus.Status.DECLINED
                order.save()
                return JsonResponse({'MESSAGE' : str(e)}, status=400)

        except (IntegrityError, ValidationError, KeyError, ValueError) as e:
            return JsonResponse({'ERROR' : str(e)}, status=400)

    @authorization
    def get(self, request, order_id):
        try:
            user = request.user

            try:
                order = Order.objects.get(user=user, id=order_id)
            except Order.DoesNotExist:
                return JsonResponse({'MESSAGE' : 'ORDER_NOT_FOUND'}, status=404)

            order_items = OrderItem.objects.filter(
                order=order
            ).select_related(
                'item'
            ).annotate(
                total_price=Sum(F('quantity') * F('item__price'))
            )

            total_order_price = order_items.aggregate(
                sum_price=Sum('total_price')
            )['sum_price'] or 0

            result = {
                'name' : user.name,
                'address' : order.address,
                'order_number' : order.order_number,
                'total_price' : total_order_price,
                'order_item' : [
                    {
                        'item' : order_item.item.name,
                        'quantity' : order_item.quantity,
                        'price' : order_item.item.price
                    } for order_item in order_items
                ]
            }

            return JsonResponse({'MESSAGE' : 'SUCCESS', 'RESULT' : result}, status=200)

        except ValidationError as e:
            return JsonResponse({'ERROR' : e.message}, status=400)

        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)