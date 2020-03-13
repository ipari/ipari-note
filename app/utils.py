from app.config.config import get_config


def config(key=None, default=None):
    return get_config(key=key, default=default)


def generate_random_string(length=32):
    import random
    import string

    letters = string.ascii_letters + string.digits
    text = ''.join(random.choice(letters) for _ in range(length))
    return text
