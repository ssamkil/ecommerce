import os, django, time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "board.settings")
django.setup()

from items.models    import Item
from items.factories import ItemFactory

def run_seed():
    total_count = 100000
    batch_size  = 5000

    print(f"START CREATING {total_count} DUMMIES")
    start_time = time.time()

    for i in range(0, total_count, batch_size):
        items_instances = ItemFactory.build_batch(batch_size)
        Item.objects.bulk_create(items_instances)
        print(f"PROGRESS: {i + batch_size}/{total_count}")

    end_time = time.time()
    print(f"TOTAL TIME: {end_time - start_time:.2f}sec")

if __name__ == "__main__":
    run_seed()