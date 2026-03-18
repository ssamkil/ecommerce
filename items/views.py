import json

from django.http                import JsonResponse
from django.core.cache          import cache
from django.core.exceptions     import ValidationError
from django.core.serializers    import serialize
from django.core.paginator      import Paginator
from django.db                  import transaction, DatabaseError
from rest_framework.views       import APIView
from drf_spectacular.utils      import extend_schema, OpenApiParameter

from .models                    import Item, Category, Review
from core.utils                 import authorization

class ItemListView(APIView):
    """
        상품 관리 API
    """

    @extend_schema(
        summary="상품 목록 조회",
        description="전체 상품 목록 또는 검색어에 따른 상품 목록을 페이징하여 조회합니다. 캐싱을 지원합니다.",
        parameters=[
            OpenApiParameter(name='name', description='검색할 상품 이름', required=False, type=str),
            OpenApiParameter(name='page', description='페이지 번호 (기본값: 1)', required=False, type=int),
        ]
    )
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
                items = Item.objects.filter(name__icontains=name).select_related('category').order_by('-created_at')
            else:
                items = Item.objects.all().select_related('category').order_by('-created_at')

            paginator = Paginator(items, 20)
            items_page = paginator.get_page(page)

            result = []
            for item in items_page:
                image_url = item.image.url if item.image else None
                result.append({
                    'id': item.id,
                    'name': item.name,
                    'category_name': item.category.name,
                    'price': item.price,
                    'quantity': item.quantity,
                    'image_url': image_url,
                    'category_id': item.category_id,
                    'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'modified_at': item.modified_at.strftime('%Y-%m-%d %H:%M:%S')
                })

            cache.set(cache_key, result, timeout=600)

            return JsonResponse({
                'MESSAGE': 'SUCCESS (DB)',
                'RESULT': result,
                'TOTAL_COUNT': paginator.count,
                'TOTAL_PAGES': paginator.num_pages,
                'CURRENT_PAGE': items_page.number
            }, status=200)

        except (ValidationError, KeyError, Exception) as e:
            return JsonResponse({'ERROR': str(e)}, status=400)

    @extend_schema(
        summary="상품 등록",
        description="새로운 상품을 등록합니다. 이미지 파일을 포함할 수 있으며 등록 시 캐시 버전이 갱신됩니다.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'category_id': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'price': {'type': 'integer'},
                    'quantity': {'type': 'integer'},
                    'image': {'type': 'string', 'format': 'binary'}
                },
                'required': ['category_id', 'name', 'price', 'quantity']
            }
        }
    )
    @authorization
    def post(self, request):
        try:
            category_id = request.POST['category_id']
            name = request.POST['name']
            price = request.POST['price']
            quantity = request.POST['quantity']
            image_file = request.FILES.get('image')

            if not name or not price or not quantity:
                return JsonResponse({'ERROR': 'EMPTY_VALUE'}, status=400)

            category = Category.objects.get(id=category_id)

            if Item.objects.filter(name=name).exists():
                return JsonResponse({'ERROR': 'ITEM_ALREADY_EXISTS'}, status=400)

            Item.objects.create(
                category=category,
                name=name,
                price=price,
                quantity=quantity,
                image=image_file,
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

class ItemDetailView(APIView):
    """
        상품 관리 API
    """

    @extend_schema(
        summary="상품 정보 수정",
        description="기존 상품 정보를 수정합니다. DB 락을 통해 동시성 제어를 수행합니다.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'price': {'type': 'integer'},
                    'quantity': {'type': 'integer'},
                    'image': {'type': 'string', 'format': 'binary'}
                }
            }
        }
    )
    @authorization
    def patch(self, request, item_id):
        try:
            with transaction.atomic():
                item = Item.objects.select_for_update(nowait=True).get(id=item_id)

                update_fields = ['name', 'price', 'quantity']
                fields_to_save = []
                updated_data_exists = False

                for field in update_fields:
                    val = request.data.get(field)
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
                    if cache.get('item_list_version') is None:
                        cache.set('item_list_version', 1)
                    else:
                        cache.incr('item_list_version')

                    return JsonResponse({'MESSAGE': 'UPDATED'}, status=200)

            return JsonResponse({'MESSAGE': 'NO_CHANGES_WERE_MADE'}, status=200)

        except DatabaseError:
            return JsonResponse({'ERROR': 'ITEM_UNDER_MODIFICATION'}, status=409)
        except (ValidationError, KeyError) as e:
            return JsonResponse({'ERROR': str(e)}, status=400)

    @extend_schema(summary="상품 삭제", description="특정 상품을 삭제하고 캐시 버전을 갱신합니다.")
    def delete(self, request, item_id):
        try:
            item = Item.objects.get(id=item_id)
            item.delete()

            try:
                cache.incr('item_list_version')
            except ValueError:
                cache.set('item_list_version', 1)

            return JsonResponse({'MESSAGE': 'DELETED'}, status=200)

        except Item.DoesNotExist:
            return JsonResponse({'ERROR': 'ITEM_DOES_NOT_EXIST'}, status=404)
        except (ValidationError, KeyError) as e:
            return JsonResponse({'ERROR': str(e)}, status=400)

class SearchItemView(APIView):
    """
    상품 검색 API
    """
    @extend_schema(
        summary="상품명 검색 (단순 조회)",
        description="상품 이름을 통해 해당 상품의 필드 정보를 JSON으로 반환합니다.",
        parameters=[OpenApiParameter(name='name', description='검색할 상품 정확한 이름', required=True, type=str)]
    )
    def get(self, request):
        try:
            item_name = request.GET.get('name', None)
            result = Item.objects.filter(name__icontains=item_name)
            serialized_data = serialize('json', result)
            serialized_data = json.loads(serialized_data)

            return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': serialized_data[0]['fields']}, status=200)

        except (ValidationError, KeyError, Exception):
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

class ReviewView(APIView):
    """
    리뷰 관리 API
    """

    @extend_schema(
        summary="상품 리뷰 조회",
        description="상품 이름을 쿼리 파라미터로 받아 해당 상품의 리뷰를 조회합니다.",
        parameters=[OpenApiParameter(name='name', description='상품 이름', required=True, type=str)]
    )
    def get(self, request):
        try:
            item_name = request.GET.get('name', None)
            review_found = Review.objects.filter(item__name=item_name)
            serialized_data = serialize('json', review_found)
            serialized_data = json.loads(serialized_data)

            return JsonResponse({'MESSAGE': 'SUCCESS', 'RESULT': serialized_data[0]['fields']})

        except (ValidationError, KeyError, Exception):
            return JsonResponse({'ERROR': 'KEY_ERROR'}, status=400)

    @extend_schema(
        summary="리뷰 작성",
        description="특정 상품에 대한 리뷰를 작성합니다.",
        parameters=[OpenApiParameter(name='name', description='상품 이름', required=True, type=str)],
        request={'application/json': {'type': 'object', 'properties': {'body': {'type': 'string'}}, 'required': ['body']}}
    )
    @authorization
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            body = data['body']
            item_name = request.GET.get('name', None)
            item = Item.objects.get(name=item_name)

            Review.objects.create(item=item, user=user, body=body)
            return JsonResponse({'MESSAGE': 'Created'}, status=201)

        except (ValidationError, KeyError, Exception) as e:
            return JsonResponse({'ERROR': str(e)}, status=400)

    @extend_schema(
        summary="리뷰 수정",
        description="작성한 리뷰 내용을 수정합니다.",
        parameters=[OpenApiParameter(name='name', description='상품 이름', required=True, type=str)],
        request={'application/json': {'type': 'object', 'properties': {'body': {'type': 'string'}}}}
    )
    @authorization
    def patch(self, request):
        try:
            data = json.loads(request.body)
            user = request.user
            item_name = request.GET.get('name', None)
            review = Review.objects.get(item__name=item_name, user=user)

            review.body = data['body']
            review.save()
            return JsonResponse({'MESSAGE': 'UPDATED'}, status=200)

        except (ValidationError, KeyError, Exception) as e:
            return JsonResponse({'ERROR': str(e)}, status=400)

    @extend_schema(
        summary="리뷰 삭제",
        description="작성한 리뷰를 삭제합니다.",
        parameters=[OpenApiParameter(name='name', description='상품 이름', required=True, type=str)]
    )
    @authorization
    def delete(self, request):
        try:
            user = request.user
            item_name = request.GET.get('name', None)
            review = Review.objects.filter(item__name=item_name, user=user)

            if review:
                review.delete()
                return JsonResponse({'MESSAGE': 'DELETED'}, status=200)
            return JsonResponse({'ERROR': 'REVIEW_DOES_NOT_EXIST'}, status=400)

        except (ValidationError, KeyError, Exception) as e:
            return JsonResponse({'ERROR': str(e)}, status=400)