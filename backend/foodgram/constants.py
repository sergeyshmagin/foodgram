"""Constants for Foodgram project."""

# User related constants
MAX_USERNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 254
MAX_FIRST_NAME_LENGTH = 150
MAX_LAST_NAME_LENGTH = 150

# Recipe related constants
MAX_RECIPE_NAME_LENGTH = 200
MAX_RECIPE_TEXT_LENGTH = 5000
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000

# Ingredient related constants
MAX_INGREDIENT_NAME_LENGTH = 200
MAX_INGREDIENT_UNIT_LENGTH = 200
MIN_INGREDIENT_AMOUNT = 1
MAX_INGREDIENT_AMOUNT = 32000

# Tag related constants
MAX_TAG_NAME_LENGTH = 200
MAX_TAG_SLUG_LENGTH = 200
MAX_TAG_COLOR_LENGTH = 7  # Hex color code like #FF0000

# Pagination
RECIPES_PAGE_SIZE = 6
USERS_PAGE_SIZE = 6
MAX_PAGE_SIZE = 100

# API Permissions
SAFE_HTTP_METHODS = ("GET", "HEAD", "OPTIONS")

# File upload
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif"]

# Cart and favorites
CART_LIMIT = 100
FAVORITES_LIMIT = 100

# Subscriptions
SUBSCRIPTIONS_LIMIT = 100

# Admin
ADMIN_LIST_PER_PAGE = 25
ADMIN_LIST_PER_PAGE_LARGE = 50

# UI constants
COLOR_PREVIEW_SIZE = 20  # pixels
IMAGE_PREVIEW_SIZE = 100  # pixels
