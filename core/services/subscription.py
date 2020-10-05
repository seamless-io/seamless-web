import enum


class Product(enum.Enum):
    """
    Product names created in stripe
    """
    JOB = 'jobs'


def create_customer(user_id: int):
    """
    Creating customer
    Should be called when user enters his credit card info
    """
    pass


def _create(customer_id: int, product: Product):
    """
    Creates a subscription for user for chosen products
    Calls when user buy something for a first time
    """
    pass


def add_product(subscription_id: int, product: Product):
    """
    Adds a product to subscription
    """
    pass


def remove_product(subscription_id: int, product: Product):
    """
    Removes a product from subscription
    """
    pass


def update_subscription(user_id: int):
    """
    Updates a subscription for a user
    """
    pass
