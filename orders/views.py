import json, uuid

from core.utils             import authorization
from carts.models           import Cart
from .models                import Order, OrderItem, OrderStatus
from items.models           import Item

from django.http            import JsonResponse
from django.db              import transaction, IntegrityError, DatabaseError
from django.db.models       import F, Sum
from django.core.exceptions import ValidationError
from rest_framework.views   import APIView
from drf_spectacular.utils  import extend_schema, OpenApiResponse

class OrderListView(APIView):
    """
        주문 관리 API
    """

    @extend_schema(
        summary="주문 생성",
        description="장바구니의 상품들을 주문 처리합니다. 트랜잭션과 DB 락을 사용하여 재고 무결성을 보장합니다.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'address': {'type': 'string', 'description': '배송 주소'}
                },
                'required': ['address']
            }
        },
        responses={
            201: OpenApiResponse(description="주문 성공"),
            400: OpenApiResponse(description="장바구니 비어있음 또는 재고 부족"),
            409: OpenApiResponse(description="동시 주문으로 인한 일시적 충돌 (Retry 필요)")
        }
    )
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
                        price=Sum(F('item__quantity') * F('item__price'))
                    )

                    if not carts.exists():
                        return JsonResponse({'MESSAGE': 'EMPTY_CART'}, status=400)

                    cart_items = list(carts)
                    item_ids = [cart.item.id for cart in cart_items]

                    locked_item = Item.objects.select_for_update(nowait=True).filter(id__in=item_ids)
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
                    order.save()

                    return JsonResponse({'MESSAGE': 'ORDER_RESERVED'}, status=201)

            except IntegrityError as e:
                order.order_status_id = OrderStatus.Status.DECLINED
                order.save()
                return JsonResponse({'ERROR': str(e)}, status=400)

            except DatabaseError:
                return JsonResponse({'ERROR': 'ITEM_UNDER_MODIFICATION'}, status=409)

            except Exception as e:
                order.order_status_id = OrderStatus.Status.DECLINED
                order.save()
                return JsonResponse({'ERROR': str(e)}, status=400)

        except (ValidationError, KeyError, ValueError) as e:
            return JsonResponse({'ERROR': str(e)}, status=400)

class OrderDetailView(APIView):
    """
    주문 관리 API
    """

    @extend_schema(
        summary="주문 상세 조회",
        description="특정 주문 번호에 대한 상세 내역과 총 결제 금액을 조회합니다.",
        responses={
            200: OpenApiResponse(description="조회 성공"),
            404: OpenApiResponse(description="주문 내역 없음")
        }
    )
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

        except (ValidationError, KeyError) as e:
            return JsonResponse({'ERROR' : str(e)}, status=400)