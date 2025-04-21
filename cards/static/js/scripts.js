// cards/static/js/scripts.js

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
            }
          });
  
          const data = await response.json();
          if (data.is_favorite !== undefined) {
            button.classList.toggle('active');
            const icon = button.querySelector('i');
            icon.className = data.is_favorite ? 'bi bi-star-fill' : 'bi bi-star';
          } else {
            alert('Ошибка: не удалось изменить избранное');
          }
        } catch (error) {
          console.error(error);
        }
      });
    });
  
    // 🗑️ Модальное удаление
    const deleteConfirmModal = document.getElementById('deleteConfirmModal');
    const deleteForm = document.getElementById('deleteForm');
  
    window.showDeleteModal = function(templateId) {
      deleteForm.action = `/cards/${templateId}/delete/`;
      const modal = new bootstrap.Modal(deleteConfirmModal);
      modal.show();
    };
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
