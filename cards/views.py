from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from .models import CardTemplate, CardInstance
from .forms import CardTemplateForm
import logging
from django.db import transaction
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

@login_required
def card_template_list(request: HttpRequest) -> HttpResponse:
    """Отображает список шаблонов карточек."""
    templates = CardTemplate.objects.filter(
        is_active=True
    ).select_related("creator")
    return render(request, 'cards/template_list.html', {'templates': templates})


@login_required
def create_template(request: HttpRequest) -> HttpResponse:
    """Создание нового шаблона."""
    if request.method == 'POST':
        form = CardTemplateForm(request.POST)
        if form.is_valid():
            try:
                template = form.save(commit=False)
                template.creator = request.user
                template.save()
                logger.info(f"Создан шаблон {template.name}")
                return redirect('cards:template_list')
            except Exception as e:
                logger.error(f"Ошибка создания шаблона: {e}")
                form.add_error(None, "Ошибка сохранения")
    else:
        form = CardTemplateForm()
    return render(request, 'cards/template_form.html', {'form': form})


@login_required
def template_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Просмотр деталей шаблона."""
    template = get_object_or_404(CardTemplate, pk=pk, is_active=True)
    return render(request, 'cards/template_detail.html', {
        'template': template,
        'is_owner': request.user == template.creator
    })


@login_required
def template_update(request: HttpRequest, pk: int) -> HttpResponse:
    """Редактирование шаблона."""
    template = get_object_or_404(CardTemplate, pk=pk, is_active=True)

    if not (request.user == template.creator or request.user.is_staff):
        raise PermissionDenied("Нет прав на редактирование")

    if request.method == 'POST':
        form = CardTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return redirect('cards:template_detail', pk=pk)
    else:
        form = CardTemplateForm(instance=template)

    return render(request, 'cards/template_form.html', {'form': form})


@require_POST
@login_required
def template_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """Мягкое удаление шаблона."""
    template = get_object_or_404(CardTemplate, pk=pk, is_active=True)

    if not (request.user == template.creator or request.user.is_staff):
        raise PermissionDenied("Нет прав на удаление")

    template.is_active = False
    template.save()
    return JsonResponse({'status': 'success'})


@require_POST
@login_required
def toggle_favorite(request, pk):
    """Переключение избранного статуса."""
    template = get_object_or_404(CardTemplate, pk=pk, is_active=True)

    if template.creator != request.user:
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    template.is_favorite = not template.is_favorite
    template.save()
    return JsonResponse({'is_favorite': template.is_favorite})


def parse_form_data(post_data, fields_schema):
    """Парсинг и предварительная обработка данных формы"""
    result = {
        'card_data': {},
        'tags': [tag.strip() for tag in post_data.get('tags', '').split(',') if tag.strip()]
    }

    for field_name in fields_schema.keys():
        field_config = fields_schema[field_name]
        value = post_data.get(field_name)

        # Преобразование типов данных
        if field_config.get('type') == 'number':
            try:
                result['card_data'][field_name] = float(
                    value) if '.' in value else int(value)
            except (TypeError, ValueError):
                result['card_data'][field_name] = None
        elif field_config.get('type') == 'checkbox':
            result['card_data'][field_name] = bool(value)
        else:
            result['card_data'][field_name] = value.strip() if value else None

    return result


def validate_card_data(form_data, fields_schema):
    """Валидация данных по схеме шаблона"""
    errors = {}

    for field_name, config in fields_schema.items():
        value = form_data['card_data'].get(field_name)
        if value is None:
            continue  # Если поле необязательное
        field_label = config.get('label', field_name)

        # Проверка обязательных полей
        if config.get('required') and not value:
            errors[field_name] = f'{field_label} - обязательное поле'
            continue
        
        # Валидация по типу поля
        field_type = config.get('type', 'text')

        if field_type == 'number':
            if not isinstance(value, (int, float)):
                errors[field_name] = 'Требуется числовое значение'

        elif field_type == 'select':
            options = [str(opt.get('value', opt))
                       for opt in config.get('options', [])]
            if value not in options:
                errors[field_name] = 'Недопустимое значение для выбора'

        elif field_type == 'checkbox':
            if not isinstance(value, bool):
                errors[field_name] = 'Некорректное значение флажка'

    if errors:
        raise ValidationError({'fields': errors})


@require_POST
@login_required
@transaction.atomic
def create_card_instance(request, template_id):
    """
    Создание экземпляра карточки с валидацией по шаблону
    """
    try:
        # 1. Получение шаблона
        template = CardTemplate.objects.select_related('creator').get(
            pk=template_id,
            is_active=True
        )

        # 2. Проверка прав доступа
        if not (request.user == template.creator or
                request.user.has_perm('cards.add_cardinstance')):
            return JsonResponse({
                'status': 'error',
                'message': 'Недостаточно прав для создания карточки'
            }, status=403)

        # 3. Парсинг данных формы
        form_data = parse_form_data(request.POST, template.fields)

        # 4. Валидация данных
        validate_card_data(form_data, template.fields)

        # 5. Создание карточки
        card = CardInstance.objects.create(
            template=template,
            data=form_data['card_data'],
            created_by=request.user,
            meta_data={
                'tags': form_data['tags'],
                'created_via': 'web_form'
            }
        )

        return JsonResponse({
            'status': 'success',
            'card_id': card.id,
            'preview_url': card.get_absolute_url()
        })

    except CardTemplate.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Шаблон не найден или удален'
        }, status=404)

    except ValidationError as e:
        return JsonResponse({
            'status': 'validation_error',
            'errors': e.message_dict
        }, status=400)

    except Exception as e:
        logger.error(f"Error creating card: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Внутренняя ошибка сервера'
        }, status=500)


@login_required
def publish_template(request, pk):
    """
    Заглушка: Сделать шаблон публичным.
    """
    return JsonResponse({'status': 'stub', 'message': 'Публикация временно не реализована.'})


@login_required
def unpublish_template(request, pk):
    """
    Заглушка: Снять шаблон с публикации.
    """
    return JsonResponse({'status': 'stub', 'message': 'Снятие с публикации временно не реализовано.'})
