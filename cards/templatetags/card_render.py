import json
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()

@register.simple_tag
def render_card_fields(fields_data, form_mode=False):
    """
    Рендерит поля карточки из JSON-структуры
    :param fields_data: JSON-строка или словарь
    :param form_mode: Режим формы (True) или превью (False)
    :return: Сгенерированный HTML
    """
    try:
        # Конвертируем строку JSON в словарь при необходимости
        if isinstance(fields_data, str):
            fields = json.loads(fields_data)
        else:
            fields = fields_data
        
        if not isinstance(fields, dict):
            return ''
            
        html = []
        for field_name, config in fields.items():
            html.append(render_single_field(field_name, config, form_mode))
        
        return mark_safe(''.join(html))  # Безопасно, так как все вставки экранированы
    
    except json.JSONDecodeError:
        return mark_safe('<div class="alert alert-danger">Ошибка в формате JSON</div>')


def render_single_field(field_name, config, form_mode):
    """Рендерит одно поле"""
    field_type = config.get('type', 'text')
    label = config.get('label', field_name.capitalize())
    required = 'required' if config.get('required', False) else ''
    placeholder = config.get('placeholder', '')
    classes = config.get('classes', '')
    default_value = config.get('default', '')
    
    # Базовые классы стилей
    base_classes = "form-control mb-3" if form_mode else "card-field mb-2"
    field_id = f"field_{field_name}"

    # Генерация HTML в зависимости от типа поля
    if field_type == 'textarea':
        return textarea_field(field_id, field_name, label, placeholder, required, classes, base_classes, default_value, form_mode)
    
    elif field_type == 'number':
        return number_field(field_id, field_name, label, placeholder, required, classes, base_classes, default_value, form_mode)
    
    elif field_type == 'select':
        return select_field(field_id, field_name, label, config.get('options', []), placeholder, required, classes, base_classes, default_value, form_mode)
    
    elif field_type == 'checkbox':
        return checkbox_field(field_id, field_name, label, required, classes, base_classes, default_value, form_mode)
    
    elif field_type == 'image':  # Добавлено новое поле
        return image_field(field_id, field_name, label, placeholder, required, classes, base_classes, default_value, form_mode)
    
    else:  # text по умолчанию
        return text_field(field_id, field_name, label, placeholder, required, classes, base_classes, default_value, form_mode)


def text_field(field_id, name, label, placeholder, required, classes, base_classes, value, form_mode):
    """Текстовое поле"""
    if form_mode:
        return f'''
        <div class="form-group {classes}">
            <label for="{field_id}" class="form-label">{escape(label)}</label>
            <input type="text" id="{field_id}" name="{name}" 
                   class="{base_classes}" placeholder="{escape(placeholder)}" 
                   value="{escape(value)}" {required}>
        </div>
        '''
    else:
        return f'''
        <div class="card-field-item {classes}">
            <div class="card-field-label">{escape(label)}</div>
            <div class="card-field-value">{escape(value or placeholder)}</div>
        </div>
        '''


def textarea_field(field_id, name, label, placeholder, required, classes, base_classes, value, form_mode):
    """Многострочное текстовое поле"""
    if form_mode:
        return f'''
        <div class="form-group {classes}">
            <label for="{field_id}" class="form-label">{escape(label)}</label>
            <textarea id="{field_id}" name="{name}" 
                      class="{base_classes}" rows="3"
                      placeholder="{escape(placeholder)}" {required}>{escape(value)}</textarea>
        </div>
        '''
    else:
        return f'''
        <div class="card-field-item {classes}">
            <div class="card-field-label">{escape(label)}</div>
            <div class="card-field-value">{escape(value or placeholder)}</div>
        </div>
        '''


def select_field(field_id, name, label, options, placeholder, required, classes, base_classes, value, form_mode):
    """Выпадающий список"""
    options_html = ''.join(
        f'<option value="{escape(opt.get("value", opt))}" '
        f'{"selected" if str(opt.get("value", opt)) == str(value) else ""}>{escape(opt.get("label", opt))}</option>'
        for opt in options
    )
    
    if form_mode:
        return f'''
        <div class="form-group {classes}">
            <label for="{field_id}" class="form-label">{escape(label)}</label>
            <select id="{field_id}" name="{name}" 
                    class="{base_classes}" {required}>
                <option value="">{escape(placeholder or '-- Выберите --')}</option>
                {options_html}
            </select>
        </div>
        '''
    else:
        selected_option = next(
            (escape(opt.get('label', opt)) for opt in options 
            if str(opt.get('value', opt)) == str(value)),
            ''
        )
        return f'''
        <div class="card-field-item {classes}">
            <div class="card-field-label">{escape(label)}</div>
            <div class="card-field-value">{selected_option}</div>
        </div>
        '''


def checkbox_field(field_id, name, label, required, classes, base_classes, value, form_mode):
    """Чекбокс"""
    checked = 'checked' if value else ''
    if form_mode:
        return f'''
        <div class="form-check {classes}">
            <input type="checkbox" id="{field_id}" name="{name}" 
                   class="form-check-input" {checked} {required}>
            <label class="form-check-label" for="{field_id}">{escape(label)}</label>
        </div>
        '''
    else:
        return f'''
        <div class="card-field-item {classes}">
            <div class="form-check">
                <input type="checkbox" class="form-check-input" {checked} disabled>
                <label class="form-check-label">{escape(label)}</label>
            </div>
        </div>
        '''


def number_field(field_id, name, label, placeholder, required, classes, base_classes, value, form_mode):
    """Числовое поле"""
    if form_mode:
        return f'''
        <div class="form-group {classes}">
            <label for="{field_id}" class="form-label">{escape(label)}</label>
            <input type="number" id="{field_id}" name="{name}" 
                   class="{base_classes}" placeholder="{escape(placeholder)}" 
                   value="{escape(str(value))}" {required}>
        </div>
        '''
    else:
        return f'''
        <div class="card-field-item {classes}">
            <div class="card-field-label">{escape(label)}</div>
            <div class="card-field-value">{escape(str(value) or placeholder)}</div>
        </div>
        '''


def image_field(field_id, name, label, placeholder, required, classes, base_classes, value, form_mode):
    """Поле для изображения"""
    if form_mode:
        return f'''
        <div class="form-group {classes}">
            <label for="{field_id}" class="form-label">{escape(label)}</label>
            <input type="file" id="{field_id}" name="{name}" 
                   class="{base_classes}" accept="image/*" {required}>
        </div>
        '''
    else:
        # Предполагается, что value содержит URL изображения
        return f'''
        <div class="card-field-item {classes}">
            <div class="card-field-label">{escape(label)}</div>
            <div class="card-field-value">
                <img src="{escape(value or placeholder)}" class="card-img">
            </div>
        </div>
        '''