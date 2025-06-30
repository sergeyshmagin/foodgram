"""Кастомные поля для API."""
import base64
import binascii
import imghdr
import uuid

from django.core.files.base import ContentFile

from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    Поле для работы с изображениями в формате base64.

    Декодирует base64 строку в файл изображения.
    """

    def to_internal_value(self, data):
        """Преобразование base64 в файл."""
        # Проверяем, что это base64 строка
        if isinstance(data, str) and data.startswith("data:image/"):
            # Извлекаем format и данные
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            # Декодируем base64
            try:
                decoded_data = base64.b64decode(imgstr)
                # Проверяем, что это действительно изображение
                img_format = imghdr.what(None, decoded_data)
                if img_format:
                    ext = img_format

                # Генерируем уникальное имя файла
                filename = f"{uuid.uuid4()}.{ext}"
                data = ContentFile(decoded_data, name=filename)
            except binascii.Error:
                raise serializers.ValidationError(
                    "Невалидная base64 строка изображения."
                )

        return super().to_internal_value(data)
