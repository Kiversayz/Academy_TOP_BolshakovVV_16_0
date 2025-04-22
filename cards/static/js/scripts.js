document.addEventListener('DOMContentLoaded', () => {
  // ⭐ Избранное (звезда)
  document.querySelectorAll('.favorite-toggle').forEach(button => {
    button.addEventListener('click', async () => {
      const templateId = button.dataset.templateId;
      const url = `/cards/${templateId}/toggle-favorite/`;

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({}) // Добавлено
        });

        const data = await response.json();
        if (data.is_favorite !== undefined) {
          button.classList.toggle('active');
          const icon = button.querySelector('i');
          icon.className = data.is_favorite ? 'bi bi-star-fill' : 'bi bi-star';
        } else {
          showToast('Ошибка', 'Не удалось изменить избранное', 'danger');
        }
      } catch (error) {
        console.error(error);
        showToast('Ошибка', 'Ошибка соединения', 'danger');
      }
    });
  });

  // Модальное удаление
  const deleteConfirmModal = document.getElementById('deleteConfirmModal');
  const deleteForm = document.getElementById('deleteForm');

  window.showDeleteModal = function(templateId) {
      deleteForm.action = `/cards/${templateId}/delete/`;
      const modal = new bootstrap.Modal(deleteConfirmModal);
      modal.show();
  };

  deleteForm.addEventListener('submit', async (e) => {
      e.preventDefault(); // Предотвращаем стандартную отправку формы

      try {
          const templateId = deleteForm.action.split('/').pop(); // Получаем pk из URL
          const response = await fetch(deleteForm.action, {
              method: 'POST',
              headers: {
                  'X-CSRFToken': getCookie('csrftoken'),
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({}) // Пустой тело, если не нужны данные
          });

          const data = await response.json();

          if (response.ok && data.success) {
              // Закрываем модальное окно
              deleteConfirmModal.modal('hide');
              // Удалить карточку из DOM
              const cardToRemove = document.querySelector(`[data-template-id="${templateId}"]`);
              if (cardToRemove) {
                  cardToRemove.remove();
              }
              // Показываем уведомление
              showToast('Успех!', 'Шаблон успешно удален', 'success');

              // Обновляем список шаблонов (например, перезагружаем страницу)
              // location.reload();
          } else {
              showToast('Ошибка', data.error || 'Не удалось удалить', 'danger');
          }
      } catch (error) {
          showToast('Ошибка', 'Ошибка соединения', 'danger');
      }
  });
});

// 🔒 Получение CSRF токена
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(trimmed.slice(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// 🃏 Обработка формы создания карточки
const cardForm = document.getElementById('cardCreateForm');
const cardPreview = document.getElementById('cardPreview');

if (cardForm && cardPreview) {
  // Новая функция для обработки файлов
  function handleFileUpload(fieldName, file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const preview = document.querySelector(`#preview-${fieldName}`);
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

    // Обработка файловых полей
    if (target.type === 'file') {
      handleFileUpload(fieldName, target.files[0]);
      return;
    }

    const value = target.type === 'checkbox' ? target.checked : target.value;
    
    const previewField = cardPreview.querySelector(`[data-field="${fieldName}"]`);
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
    const submitBtn = this.querySelector('button[type="submit"]');
    const formData = new FormData(this);

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status"></span>
        Сохранение...
      `;

      // Преобразуем FormData в JSON, если сервер ожидает это
      const data = Object.fromEntries(formData.entries());

      const response = await fetch(this.action, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', // Указываем формат данных
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data) // Отправляем JSON
      });

      const result = await response.json();
      
      if (response.ok && result.status === 'success') {
        showToast('Успех!', 'Карточка успешно создана', 'success');
        this.reset();
        cardPreview.querySelectorAll('[data-field]').forEach(field => {
          field.textContent = '';
          if (field.tagName === 'INPUT' && field.type === 'checkbox') {
            field.checked = false;
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