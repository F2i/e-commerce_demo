from locust import HttpUser, task, between
from random import randint

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        response = self.client.post(
            '/store/carts/',
            name='create a cart'
        )
        result = response.json()
        self.cart_id = result['id']
        return super().on_start()

    @task(1)
    def view_products(self):
        # print('View products')
        collection_id = randint(2, 6)
        self.client.get(
            f'/store/products/?collection_id={collection_id}',
            name='view products'
        )

    @task(2)
    def view_single_product(self):
        # print('View product\'s detail')
        product_id = randint(1, 1000)
        self.client.get(
            f'/store/products/{product_id}/',
            name='view single product'
        )

    @task(4)
    def add_product_to_cart(self):
        # print('Add product to cart')
        product_id =  randint(1, 1000)
        self.client.post(
            f'/store/carts/{self.cart_id}/cartitems/',
            name='add product to cart',
            json={
                'product_id': product_id,
                'quantity': 3,
            }
        )