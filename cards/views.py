from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from .models import CardTemplate
from .forms import CardTemplateForm
import logging
import os
from django.views.decorators.http import require_POST
from django.http import JsonResponse


logger = logging.getLogger(__name__)


@login_required
def card_template_list(request: HttpRequest) -> HttpResponse:
    """
    Отображает список всех шаблонов карточек.
    """
    templates = CardTemplate.objects.all().select_related("creator")
    return render(request, 'cards/template_list.html', {'templates': templates})


@login_required
def create_template(request: HttpRequest) -> HttpResponse:
    """
    Создает новый шаблон карточки.
    """
    if request.method == 'POST':
        form = CardTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.creator = request.user
            template.description = request.POST.get('description', '')
            template.is_favorite = bool(request.POST.get('is_favorite'))
            try:
                template.save()
                logger.info(f"[Создание] Шаблон '{template.name}' создан пользователем {request.user}")
                return redirect('template_list')
            except Exception as e:
                logger.error(f"[Ошибка] Не удалось сохранить шаблон: {e}")
                form.add_error(None, "Ошибка при сохранении шаблона.")
    else:
        form = CardTemplateForm()

    return render(request, 'cards/template_form.html', {'form': form})


@login_required
def template_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Отображает подробную информацию о шаблоне карточки.
    """
    template = get_object_or_404(CardTemplate, pk=pk)
    is_owner = request.user == template.creator or request.user.is_staff
    return render(request, 'cards/template_detail.html', {
        'template': template,
        'is_owner': is_owner
    })


@login_required
def template_update(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Обновляет существующий шаблон карточки.
    Только владелец шаблона или администратор может редактировать.
    """
    template = get_object_or_404(CardTemplate, pk=pk)

    if request.user != template.creator and not request.user.is_staff:
        raise PermissionDenied("Недостаточно прав для редактирования шаблона.")

    if request.method == 'POST':
        form = CardTemplateForm(request.POST, request.FILES, instance=template)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.description = request.POST.get('description', '')
            instance.is_favorite = bool(request.POST.get('is_favorite'))

            # Удаление старого изображения, если указано
            if request.POST.get('remove_preview') == '1' and instance.preview_image:
                if os.path.isfile(instance.preview_image.path):
                    os.remove(instance.preview_image.path)
                instance.preview_image = None

            # Если загружено новое изображение — заменить
            if 'preview_image' in request.FILES:
                instance.preview_image = request.FILES['preview_image']

            try:
                instance.save()
                logger.info(f"[Обновление] Шаблон '{instance.name}' обновлён пользователем {request.user}")
                return redirect('template_list')
            except Exception as e:
                logger.error(f"[Ошибка] Обновление шаблона '{template.name}' не удалось: {e}")
                form.add_error(None, "Ошибка при сохранении изменений.")
    else:
        form = CardTemplateForm(instance=template)

    return render(request, 'cards/template_form.html', {'form': form})


@login_required
def template_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Удаляет шаблон карточки.
    Только владелец или администратор может удалить.
    """
    template = get_object_or_404(CardTemplate, pk=pk)

    if request.user != template.creator and not request.user.is_staff:
        raise PermissionDenied("Недостаточно прав для удаления шаблона.")

    if request.method == 'POST':
        # Удаление изображения, если есть
        if template.preview_image and os.path.isfile(template.preview_image.path):
            os.remove(template.preview_image.path)

        name = template.name
        template.delete()
        logger.info(f"[Удаление] Шаблон '{name}' удалён пользователем {request.user}")
        return redirect('template_list')

    # Удаление теперь должно вызываться через JS-модалку (не используется отдельная страница)
    raise PermissionDenied("Удаление должно происходить через POST.")

@require_POST
@login_required
def toggle_favorite(request, pk):
    """
    Переключает статус 'избранное' для шаблона.

    Args:
        request (HttpRequest): Запрос от пользователя
        pk (int): ID шаблона

    Returns:
        JsonResponse: Новый статус is_favorite
    """
    template = get_object_or_404(CardTemplate, pk=pk)

    if template.creator != request.user and not request.user.is_staff:
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)

    template.is_favorite = not template.is_favorite
    template.save()
    return JsonResponse({'is_favorite': template.is_favorite})


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