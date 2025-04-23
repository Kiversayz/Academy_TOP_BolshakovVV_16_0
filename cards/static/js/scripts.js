document.addEventListener('DOMContentLoaded', () => {
  // Делегирование кликов для избранного (звезда)
  document.body.addEventListener('click', async (e) => {
    const button = e.target.closest('.favorite-toggle');
    if (!button) return;
      const templateId = button.dataset.templateId;
      const url = `/cards/${templateId}/toggle-favorite/`;
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
          'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({}) // Добавлено
        });
        const data = await response.json();
        if (data.is_favorite !== undefined) {
          button.classList.toggle('active');
          const icon = button.querySelector('i');
        if (icon) {
          icon.className = data.is_favorite ? 'bi bi-star-fill' : 'bi bi-star';
        }
        } else {
          showToast('Ошибка', 'Не удалось изменить избранное', 'danger');
        }
      } catch (error) {
        console.error(error);
        showToast('Ошибка', 'Ошибка соединения', 'danger');
      }
    });
// Модальное удаление
const deleteConfirmModal = document.getElementById('deleteConfirmModal');
const deleteForm = document.getElementById('deleteForm');
window.showDeleteModal = function(templateId) {
    deleteForm.action = `/cards/${templateId}/delete/`;
    const modal = bootstrap.Modal.getOrCreateInstance(deleteConfirmModal);
    modal.show();
};
// Обработчик формы удаления
deleteForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Блокировка кнопки отправки для предотвращения повторных запросов
    const submitButton = deleteForm.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
    }
    try {
      const templateIdMatches = deleteForm.action.match(/\/cards\/(\d+)\/delete\//);
      if (!templateIdMatches) {
        console.error('Некорректный URL для удаления');
            showToast('Ошибка', 'Некорректный идентификатор шаблона', 'danger');
        return;
      }
      const templateId = templateIdMatches[1];
        const response = await fetch(deleteForm.action, {
            method: 'POST',
            headers: {
          'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json'
            }
        });
        // Обработка ответа
            const data = await response.json();
        if (response.ok) {
            if (data.success) {
                // Закрываем модальное окно
                const modalInstance = bootstrap.Modal.getInstance(deleteConfirmModal);
                modalInstance?.hide();
                // Удаляем карточку из DOM
                const cardElement = document.querySelector(`[data-template-id="${templateId}"]`);
                    if (cardElement) {
                        const colElement = cardElement.closest('.col');
                        if (colElement) {
                            colElement.remove();
                        } else {
                            console.error('Родительская колонка не найдена');
                        showToast('Ошибка', 'Ошибка обновления интерфейса', 'warning');
                        }
                } else {
                    console.error('Карточка не найдена в списке', templateId);
                    showToast('Ошибка', 'Карточка не найдена на странице', 'warning');
                    // Перенаправляем на список карточек при ошибке
                    window.location.href = '/cards/';
                    return;
                }
                showToast('Успешно!', 'Шаблон успешно удален', 'success');
                // Проверяем, остались ли карточки
                const remainingCards = document.querySelectorAll('[data-template-id]');
                if (remainingCards.length === 0) {
                    window.location.href = '/cards/';
                }
            } else {
                showToast('Ошибка', data.message || 'Неизвестная ошибка', 'danger');
            }
        } else {
            // Обработка статусов ошибок
            switch (response.status) {
                case 403:
                    showToast('Ошибка', 'У вас нет прав на удаление этого шаблона', 'danger');
                    break;
                case 404:
                    showToast('Ошибка', 'Шаблон не найден', 'danger');
                    // Перенаправляем при отсутствии карточки
                    window.location.href = '/cards/';
                    break;
                default:
                    showToast('Ошибка', data.message || 'Неизвестная ошибка сервера', 'danger');
            }
        }
    } catch (error) {
        console.error('Ошибка при удалении:', error);
        showToast('Ошибка', 'Ошибка соединения с сервером', 'danger');
    } finally {
        if (submitButton) {
            submitButton.disabled = false;
        }
    }
});
  // Обработка формы создания карточки
const cardForm = document.getElementById('cardCreateForm');
const cardPreview = document.getElementById('cardPreview');
if (cardForm && cardPreview) {
    // Кэшируем элементы превью по data-field
    const previewFields = {};
    cardPreview.querySelectorAll('[data-field]').forEach(field => {
      const fieldName = field.dataset.field;
      previewFields[fieldName] = field;
    });
    // Функция для обработки файловых полей
  function handleFileUpload(fieldName, file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = previewFields[fieldName];
      if (preview) {
        preview.src = e.target.result;
      } else {
        console.error(`Превью для поля ${fieldName} не найдено`);
      }
    };
    reader.readAsDataURL(file);
  }
  // Динамическое обновление превью
  cardForm.addEventListener('input', function(e) {
    const target = e.target;
    const fieldName = target.name;
    if (target.type === 'file') {
        if (target.files && target.files[0]) {
      handleFileUpload(fieldName, target.files[0]);
        }
      return;
    }
    const value = target.type === 'checkbox' ? target.checked : target.value;
      const previewField = previewFields[fieldName];
    if (previewField) {
      if (previewField.tagName === 'INPUT' && previewField.type === 'checkbox') {
        previewField.checked = value;
      } else {
        previewField.textContent = value;
      }
    }
  });
  // Отправка формы
  cardForm.addEventListener('submit', async function(e) {
    e.preventDefault();
      const submitBtn = cardForm.querySelector('button[type="submit"]');
      const formData = new FormData(cardForm);
    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status"></span>
        Сохранение...
      `;
      const data = Object.fromEntries(formData.entries());
        const response = await fetch(cardForm.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
          body: JSON.stringify(data)
      });
      const result = await response.json();
      if (response.ok && result.status === 'success') {
        showToast('Успех!', 'Карточка успешно создана', 'success');
          cardForm.reset();
          Object.values(previewFields).forEach(field => {
          if (field.tagName === 'INPUT' && field.type === 'checkbox') {
            field.checked = false;
            } else {
              field.textContent = '';
          }
        });
      } else {
        const errorMsg = result.errors 
          ? Object.values(result.errors).join(', ') 
          : result.message || 'Неизвестная ошибка';
        showToast('Ошибка!', errorMsg, 'danger');
      }
    } catch (error) {
      showToast('Ошибка!', 'Ошибка соединения', 'danger');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<i class="bi bi-save"></i> Сохранить карточку';
    }
  });
}
});
// Функция для получения CSRF токена с кэшированием
let cachedCSRFToken = null;
function getCSRFToken() {
  if (cachedCSRFToken) return cachedCSRFToken;
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith('csrftoken=')) {
        cookieValue = decodeURIComponent(trimmed.slice('csrftoken'.length + 1));
        break;
      }
    }
  }
  cachedCSRFToken = cookieValue;
  return cookieValue;
}
// Функция Toast-уведомлений (объединена и переработана)
function showToast(title, message, type) {
  const toastContainer = document.getElementById('toastContainer') || createToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast fade show bg-${type}`;
  toast.style.position = 'relative';
  toast.innerHTML = `
    <div class="toast-header">
      <strong class="me-auto">${title}</strong>
      <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
    </div>
    <div class="toast-body">${message}</div>
  `;
  toastContainer.appendChild(toast);
  new bootstrap.Toast(toast).show();
}
function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toastContainer';
  container.style.position = 'fixed';
  container.style.top = '20px';
  container.style.right = '20px';
  container.style.zIndex = '9999';
  document.body.appendChild(container);
  return container;
}