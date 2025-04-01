from django.core.exceptions import ValidationError

def validate_image_config(config: dict) -> None:
    """Проверяет конфигурацию поля типа 'image'."""
    allowed_formats = ["png", "jpg", "jpeg"]
    if config.get("type") == "image":
        if "allowed_formats" in config:
            if not set(config["allowed_formats"]).issubset(allowed_formats):
                raise ValidationError(f"Допустимые форматы: {allowed_formats}")