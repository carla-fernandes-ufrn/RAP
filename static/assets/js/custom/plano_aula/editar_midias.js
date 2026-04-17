document.addEventListener('DOMContentLoaded', function () {
    const modalMidia = document.getElementById('modalMidia');
    const modalDelete = document.getElementById('modalConfirmDelete');

    if (modalMidia) {
        modalMidia.addEventListener('show.bs.modal', function (event) {
            const trigger = event.relatedTarget;
            if (!trigger) return;

            const url = trigger.getAttribute('data-url');
            const tipo = trigger.getAttribute('data-tipo');
            const deleteUrl = trigger.getAttribute('data-delete');

            const img = document.getElementById('modalImg');
            const video = document.getElementById('modalVideo');
            const deleteBtn = document.getElementById('btnDeleteModal');

            if (!img || !video || !deleteBtn) return;

            img.style.display = 'none';
            video.style.display = 'none';

            img.src = '';
            video.pause();
            video.src = '';

            if (tipo === 'imagem') {
                img.src = url;
                img.style.display = 'block';
            } else if (tipo === 'video') {
                video.src = url;
                video.style.display = 'block';
            }

            deleteBtn.setAttribute('data-url', deleteUrl);
        });

        modalMidia.addEventListener('hidden.bs.modal', function () {
            const video = document.getElementById('modalVideo');
            if (!video) return;

            video.pause();
            video.src = '';
        });
    }

    if (modalDelete) {
        modalDelete.addEventListener('show.bs.modal', function (event) {
            const trigger = event.relatedTarget;
            if (!trigger) return;

            const url = trigger.getAttribute('data-url');
            const btn = document.getElementById('confirmDeleteBtn');

            if (btn) {
                btn.href = url;
            }
        });
    }
});