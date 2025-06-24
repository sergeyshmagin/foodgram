"""Views for Foodgram API."""
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)

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
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        """Подписаться/отписаться от пользователя."""
        author = get_object_or_404(User, id=id)
        user = request.user

        if user == author:
            return Response(
                {"errors": "Нельзя подписаться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = Subscription.objects.filter(user=user, author=author)

        if request.method == "POST":
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

        if not subscription.exists():
            return Response(
                {"errors": "Вы не были подписаны на этого пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["put", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="me/avatar",
    )
    def avatar(self, request):
        """Установить/удалить аватар пользователя."""
        user = request.user

        if request.method == "PUT":
            serializer = SetAvatarSerializer(data=request.data)
            if serializer.is_valid():
                user.avatar = serializer.validated_data["avatar"]
                user.save()
                return Response(
                    {"avatar": user.avatar.url if user.avatar else None}
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        # DELETE
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
        from django.contrib.auth import update_session_auth_hash
        
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
        
        return Response(
            {"detail": "Пароль успешно изменен"},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="reset_password",
    )
    def reset_password(self, request):
        """Сброс пароля пользователя."""
        email = request.data.get("email")

        if not email:
            return Response(
                {"errors": "Требуется email"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            User.objects.get(email=email)
            # В реальном проекте здесь бы отправлялось письмо
            # Пока просто возвращаем успешный ответ
            return Response(
                {"detail": "Инструкции отправлены на email"},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            # Не раскрываем информацию о существовании пользователя
            return Response(
                {"detail": "Инструкции отправлены на email"},
                status=status.HTTP_200_OK,
            )


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

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        """Добавить/удалить рецепт из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        favorite = Favorite.objects.filter(user=user, recipe=recipe)

        if request.method == "POST":
            if favorite.exists():
                return Response(
                    {"errors": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Favorite.objects.create(user=user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not favorite.exists():
            return Response(
                {"errors": "Рецепта нет в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        """Добавить/удалить рецепт из списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)

        if request.method == "POST":
            if shopping_cart.exists():
                return Response(
                    {"errors": "Рецепт уже в списке покупок"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not shopping_cart.exists():
            return Response(
                {"errors": "Рецепта нет в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        user = request.user

        # Получаем агрегированный список ингредиентов
        ingredients = (
            IngredientInRecipe.objects.filter(
                recipe__in_shopping_cart__user=user
            )
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )

        # Формируем текст файла
        shopping_list = ["Список покупок\n\n"]
        if not ingredients.exists():
            shopping_list.append(
                "Ваша корзина пуста.\n"
                "Добавьте рецепты в корзину, чтобы создать список покупок.\n"
            )
        else:
            for ingredient in ingredients:
                shopping_list.append(
                    f"• {ingredient['ingredient__name']} "
                    f"({ingredient['ingredient__measurement_unit']}) - "
                    f"{ingredient['total_amount']}\n"
                )

        # Создаем HTTP response с правильными заголовками
        shopping_content = "".join(shopping_list)

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
