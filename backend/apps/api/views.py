"""Views for Foodgram API."""
from apps.recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from apps.users.models import Subscription
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeMinifiedSerializer,
    RecipeSerializer,
    SetAvatarSerializer,
    TagSerializer,
    UserSerializer,
    UserWithRecipesSerializer,
)
from .utils import generate_shopping_list

User = get_user_model()


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for Docker."""
    # Определяем версию API из DRF версионирования
    version = getattr(request, "version", "v1")

    return JsonResponse(
        {
            "status": "healthy",
            "message": f"Foodgram API {version} is running",
            "version": version,
            "api_endpoints": {
                "users": f"/api/{version}/users/",
                "recipes": f"/api/{version}/recipes/",
                "tags": f"/api/{version}/tags/",
                "ingredients": f"/api/{version}/ingredients/",
            },
        }
    )


class UserViewSet(DjoserUserViewSet):
    """ViewSet для управления пользователями."""

    serializer_class = UserSerializer

    def get_serializer_context(self):
        """Добавляем версию API в контекст сериализатора."""
        context = super().get_serializer_context()
        context["api_version"] = getattr(self.request, "version", "v1")
        return context

    def get_permissions(self):
        """Получить разрешения для действия."""
        if self.action in ["list", "retrieve", "create", "reset_password"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Получить список подписок пользователя."""
        subscriptions = User.objects.filter(
            subscribers__user=request.user
        ).prefetch_related("recipes")

        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = UserWithRecipesSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserWithRecipesSerializer(
            subscriptions, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """Подписаться на пользователя."""
        author = get_object_or_404(User, id=id)
        user = request.user

        if user == author:
            return Response(
                {"errors": "Нельзя подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = Subscription.objects.filter(user=user, author=author)

        if subscription.exists():
            return Response(
                {"errors": "Вы уже подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Subscription.objects.create(user=user, author=author)
        serializer = UserWithRecipesSerializer(
            author, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        """Отписаться от пользователя."""
        author = get_object_or_404(User, id=id)
        user = request.user

        subscription = Subscription.objects.filter(user=user, author=author)

        if not subscription.exists():
            return Response(
                {"errors": "Вы не были подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["put"],
        permission_classes=[IsAuthenticated],
        url_path="me/avatar",
    )
    def avatar(self, request):
        """Установить аватар пользователя."""
        user = request.user
        serializer = SetAvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.avatar = serializer.validated_data["avatar"]
        user.save()
        return Response({"avatar": user.avatar.url if user.avatar else None})

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удалить аватар пользователя."""
        user = request.user
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="set_password",
    )
    def set_password(self, request):
        """Изменить пароль пользователя."""
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not current_password or not new_password:
            return Response(
                {"errors": "Требуются current_password и new_password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(current_password):
            return Response(
                {"errors": "Неверный текущий пароль"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()

        # Обновляем сессию, чтобы пользователь не был автоматически разлогинен
        update_session_auth_hash(request, user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_serializer_context(self):
        """Добавляем версию API в контекст сериализатора."""
        context = super().get_serializer_context()
        context["api_version"] = getattr(self.request, "version", "v1")
        return context


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None

    def get_serializer_context(self):
        """Добавляем версию API в контекст сериализатора."""
        context = super().get_serializer_context()
        context["api_version"] = getattr(self.request, "version", "v1")
        return context


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для рецептов."""

    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags", "recipe_ingredients__ingredient"
    )
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_context(self):
        """Добавляем версию API в контекст сериализатора."""
        context = super().get_serializer_context()
        context["api_version"] = getattr(self.request, "version", "v1")
        return context

    def get_permissions(self):
        """Получить разрешения для действия."""
        if self.action in ["list", "retrieve", "get_link"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Выбрать сериализатор в зависимости от действия."""
        if self.action in ["create", "update", "partial_update"]:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def _add_to_collection(self, model, user, recipe, error_message):
        """Общий метод для добавления в избранное/корзину."""
        obj = model.objects.filter(user=user, recipe=recipe)

        if obj.exists():
            return Response(
                {"errors": error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeMinifiedSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from_collection(self, model, user, recipe, error_message):
        """Общий метод для удаления из избранного/корзины."""
        obj = model.objects.filter(user=user, recipe=recipe)

        if not obj.exists():
            return Response(
                {"errors": error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """Добавить рецепт в избранное."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._add_to_collection(
            Favorite, request.user, recipe, "Рецепт уже в избранном"
        )

    @favorite.mapping.delete
    def remove_favorite(self, request, pk=None):
        """Удалить рецепт из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._remove_from_collection(
            Favorite, request.user, recipe, "Рецепта нет в избранном"
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Добавить рецепт в список покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._add_to_collection(
            ShoppingCart, request.user, recipe, "Рецепт уже в списке покупок"
        )

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        """Удалить рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._remove_from_collection(
            ShoppingCart, request.user, recipe, "Рецепта нет в списке покупок"
        )

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        user = request.user
        shopping_content = generate_shopping_list(user)

        response = HttpResponse(
            shopping_content.encode("utf-8"),
            content_type="text/plain; charset=utf-8",
        )
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(
        detail=True,
        methods=["get"],
        url_path="get-link",
        permission_classes=[AllowAny],
    )
    def get_link(self, request, pk=None):
        """Получить короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        # Простая реализация короткой ссылки
        short_link = f"{request.build_absolute_uri('/s/')}{recipe.pk}/"
        return Response({"short-link": short_link})


@api_view(["GET"])
@permission_classes([AllowAny])
def short_link_redirect(request, recipe_id):
    """Перенаправление с короткой ссылки на полную страницу рецепта."""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    # Перенаправляем на фронтенд страницу рецепта
    return redirect(f"/recipes/{recipe.pk}")
