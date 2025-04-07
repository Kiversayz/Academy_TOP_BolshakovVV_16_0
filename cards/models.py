from django.db import models
from django.core.exceptions import ValidationError
from users.models import User

def validate_fields_structure(value: dict) -> None:
    """
    Валидатор для поля `fields`. Проверяет, что каждое поле в JSON 
    содержит обязательные ключи 'type' и 'label'.
    
    Args:
        value (dict): Значение поля `fields`.
    
    Raises:
        ValidationError: Если структура полей некорректна.
    """
    required_keys = {"type", "label"}
    for field_name, config in value.items():
        if not isinstance(config, dict):
            raise ValidationError(f"Поле '{field_name}' должно быть словарем")
        if not all(key in config for key in required_keys):
            raise ValidationError(f"Поле '{field_name}' должно содержать ключи: {required_keys}")

class CardTemplate(models.Model):
    """
    Модель для создания шаблонов игровых или обучающих карточек.
    
    Эта модель используется для определения структуры шаблонов карточек,
    которые могут быть использованы в играх, обучающих приложениях или других целях.
    
    Атрибуты:
        name (CharField): 
            Название шаблона. Максимальная длина — 100 символов.
            Пример: "Карточки по биологии".
        creator (ForeignKey): 
            Пользователь, создавший шаблон. Связь с моделью User.
            При удалении пользователя связанные шаблоны также удаляются.
        fields (JSONField): 
            Конфигурация полей карточки в формате JSON.
            Валидируется функцией `validate_fields_structure`.
            Пример структуры:
                {
                    "term": {"type": "text", "label": "Термин"},
                    "definition": {"type": "textarea", "label": "Определение"}
                }
        preview_image (ImageField): 
            Превью шаблона (опционально). Загружается в директорию 'previews/'.
        created_at (DateTimeField): 
            Дата и время создания шаблона. Устанавливается автоматически.
    
    Методы:
        __str__: 
            Возвращает строковое представление шаблона в формате "<name> (ID: <id>)".
    
    Пример использования:
        >>> user = User.objects.get(username="example_user")
        >>> template = CardTemplate.objects.create(
        ...     name="Карточки по биологии",
        ...     creator=user,
        ...     fields={
        ...         "term": {"type": "text", "label": "Термин"},
        ...         "definition": {"type": "textarea", "label": "Определение"}
        ...     }
        ... )
        >>> print(template)
        Карточки по биологии (ID: 1)
    """

    name = models.CharField(
        max_length=100,
        verbose_name="Название шаблона",
        help_text="Максимальная длина — 100 символов. Пример: 'Карточки для викторины'"
    )
    
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Создатель",
        related_name="templates",
        help_text="Пользователь, создавший этот шаблон"
    )
    
    fields = models.JSONField(
        verbose_name="Поля шаблона",
        validators=[validate_fields_structure],
        help_text="""
            JSON-структура с описанием полей. Пример:
            {
                "image": {
                    "type": "image", 
                    "label": "Изображение",
                    "max_size": 1024  // в килобайтах (опционально)
                },
                "question": {
                    "type": "text", 
                    "label": "Вопрос",
                    "max_length": 200
                }
            }
        """
    )
    
    preview_image = models.ImageField(
        upload_to='previews/',
        verbose_name="Превью шаблона",
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Автоматически устанавливается при создании"
    )

    class Meta:
        verbose_name = "Шаблон карточки"
        verbose_name_plural = "Шаблоны карточек"
        ordering = ["-created_at"]  # Сортировка по убыванию даты
        indexes = [
            models.Index(fields=["name"]),  # Индекс для ускорения поиска по имени
        ]
        # constraints = [
        #     models.CheckConstraint(
        #         check=models.Q(fields__lengthes=5000),  # TODO: Ограничение размера JSON (реализовать через валидатор)
        #         name="fields_max_size"
        #     )
        # ]

    def __str__(self) -> str:
        """Строковое представление для админки и API."""
        return f"{self.name} (автор: {self.creator.username})"

    # TODO: Добавить метод для генерации превью карточки
    # def get_preview_html(self) -> str:
    #     """Генерирует HTML-превью на основе fields."""
    #     pass


class CardInstance(models.Model):
    template = models.ForeignKey(
        CardTemplate, 
        on_delete=models.CASCADE,
        related_name="cards"
    )
    data = models.JSONField(verbose_name="Данные карточки")  # Пример: {"question": "Текст", "image": "previews/img1.png"}
    created_at = models.DateTimeField(auto_now_add=True)