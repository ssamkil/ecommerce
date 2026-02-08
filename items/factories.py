import factory

from factory.django import DjangoModelFactory
from .models        import Item

class ItemFactory(DjangoModelFactory):
    class Meta:
        model = Item

    name        = factory.Faker('sentence', nb_words=2, locale='ko_KR')
    price       = factory.Faker('random_int', min=1, max=300000)
    quantity    = factory.Faker('random_int', min=1, max=100)
    image_url   = factory.Faker('image_url')
    category_id = 1