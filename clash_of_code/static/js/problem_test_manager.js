document.addEventListener('DOMContentLoaded', function () {
    const tasksContainer = document.querySelector('.tasks');

    tasksContainer.addEventListener('click', function (event) {
        if (event.target.classList.contains('move-up-button')) {
            const task = event.target.closest('.task');
            const previousTask = task.previousElementSibling;

            if (previousTask) {
                tasksContainer.insertBefore(task, previousTask);
                updateIndices();
                sendUpdateRequest(task, previousTask);
            }
        }

        if (event.target.classList.contains('move-down-button')) {
            const task = event.target.closest('.task');
            const nextTask = task.nextElementSibling;

            if (nextTask) {
                tasksContainer.insertBefore(nextTask, task);
                updateIndices();
                sendUpdateRequest(nextTask, task);
            }
        }
    });

    function updateIndices() {
        const tasks = document.querySelectorAll('.task');
        tasks.forEach((task, index) => {
            task.setAttribute('data-index', index);
            const numberInput = task.querySelector('input[name="number"]');
            if (numberInput) {
                numberInput.value = index;
            }
        });
    }

    function sendUpdateRequest(movedTask, referenceTask) {
        const movedPk = movedTask.querySelector('input[name="pk"]').value;
        const referencePk = referenceTask.querySelector('input[name="pk"]').value;

        fetch(URL, { // при изменении url заменить его тут
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({
                moved_pk: movedPk,
                reference_pk: referencePk,
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});


