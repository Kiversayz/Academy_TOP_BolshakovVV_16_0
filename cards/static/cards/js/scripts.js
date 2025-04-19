document.addEventListener("DOMContentLoaded", function() {
    // Модальное окно для удаления шаблона
    const deleteModal = document.getElementById('delete-modal');
    const cancelDeleteBtn = document.getElementById('cancel-delete');
    const deleteForm = document.getElementById('delete-form');

    // Открытие модального окна при нажатии на кнопку "Удалить"
    document.querySelectorAll('.delete-template-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            const templateId = this.dataset.templateId; // Получаем ID шаблона из data-атрибута
            deleteForm.action = `/cards/${templateId}/delete/`; // Устанавливаем действие формы
            deleteModal.classList.remove('hidden');
        });
    });

    // Закрытие модального окна
    cancelDeleteBtn.addEventListener('click', function() {
        deleteModal.classList.add('hidden');
    });

    // Загрузка нового изображения
    const imageUploadModal = document.getElementById('image-upload-modal');
    const cancelUploadBtn = document.getElementById('cancel-upload');
    const uploadForm = document.getElementById('upload-form');

    // Открытие модального окна для загрузки изображения
    document.querySelectorAll('.upload-image-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            const templateId = this.dataset.templateId; // Получаем ID шаблона
            uploadForm.action = `/cards/${templateId}/update/`; // Устанавливаем действие формы для загрузки
            imageUploadModal.classList.remove('hidden');
        });
    });

    // Закрытие модального окна
    cancelUploadBtn.addEventListener('click', function() {
        imageUploadModal.classList.add('hidden');
    });

    // Отправка формы для загрузки изображения
    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Предотвратить стандартное отправление формы

        const formData = new FormData(uploadForm);

        fetch(uploadForm.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Обновить страницу или изменить превью изображения на странице
                document.getElementById('template-image-preview').src = data.image_url;
                imageUploadModal.classList.add('hidden');
            } else {
                alert('Произошла ошибка при загрузке изображения');
            }
        })
        .catch(error => {
            console.error('Ошибка загрузки изображения:', error);
            alert('Произошла ошибка. Попробуйте позже.');
        });
    });
});

