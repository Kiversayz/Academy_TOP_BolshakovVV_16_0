from django.db import models
from django.core.exceptions import ValidationError
from users.models import User

def validate_fields_structure(value: dict) -> None:
    """
    Валидатор для поля `fields`. Проверяет структуру JSON.
    
    Правила:
    1. Верхний уровень должен быть словарем.
    2. Каждое поле должно быть словарем с ключами 'type' и 'label'.
    3. Тип поля должен быть одним из: text, textarea, image, number.
    4. Для типа 'select' обязательно наличие списка 'options'.
    """
    required_keys = {"type", "label"}
    allowed_types = {"text", "textarea", "image", "number", "select"}

    if not isinstance(value, dict):
        raise ValidationError("Основная структура должна быть словарем.")

    for field_name, config in value.items():
        # Проверка типа конфига
        if not isinstance(config, dict):
            raise ValidationError(f"Поле '{field_name}' должно быть словарем.")
        
        # Проверка обязательных ключей
        missing_keys = required_keys - config.keys()
        if missing_keys:
            raise ValidationError(
                f"Поле '{field_name}' не содержит ключи: {missing_keys}."
            )
        
        # Проверка допустимых типов
        field_type = config.get("type")
        if field_type not in allowed_types:
            raise ValidationError(
                f"Недопустимый тип '{field_type}' для поля '{field_name}'. "
                f"Допустимые типы: {allowed_types}."
            )
        
        # Дополнительные проверки для специфичных типов
        if field_type == "select" and "options" not in config:
            raise ValidationError(
                f"Поле '{field_name}' типа 'select' требует ключ 'options'."
            )


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
                    "max_size": 1024
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
        creator_username = self.creator.username if self.creator else "Неизвестный"
        return f"{self.name} (автор: {creator_username})"

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