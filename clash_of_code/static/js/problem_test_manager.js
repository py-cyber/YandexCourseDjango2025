document.addEventListener('DOMContentLoaded', function () {
    const tasksContainer = document.getElementById('tasksContainer');

    tasksContainer.addEventListener('click', function (event) {
        if (event.target.classList.contains('move-up-button')) {
            const task = event.target.closest('.test-case');
            const previousTask = task.previousElementSibling;

            const movedPk = task.querySelector('input[name="pk"]').value;
            const referencePk = previousTask ? previousTask.querySelector('input[name="pk"]').value : null;

            if (previousTask && movedPk && referencePk) {
                tasksContainer.insertBefore(task, previousTask);
                updateIndices();
                sendUpdateRequest(task, previousTask);
            }
        }

        if (event.target.classList.contains('move-down-button')) {
            const task = event.target.closest('.test-case');
            const nextTask = task.nextElementSibling;

            const movedPk = task.querySelector('input[name="pk"]').value;
            const referencePk = nextTask ? nextTask.querySelector('input[name="pk"]').value : null;

            if (nextTask && movedPk && referencePk) {
                tasksContainer.insertBefore(nextTask, task);
                updateIndices();
                sendUpdateRequest(nextTask, task);
            }
        }
    });

    function updateIndices() {
        const tasks = document.querySelectorAll('.test-case');
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

        fetch(URL, {
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
});

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

const taskTemplate = (testNumber, INPUT_DATA_TRANS, OUTPUT_DATA_TRANS, IS_SAMPLE_TRANS, SAVE_TRANS) => `
<div class="test-case mb-4 border rounded-3 p-3" data-index="${testNumber}">
    <form method="post" enctype="multipart/form-data" class="test-form">
        <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie("csrftoken")}">
        <input type="hidden" name="number" value="${testNumber + 1}">
        <input type="hidden" name="pk">

        <div class="row g-3">
            <div class="col-md-11">
                <div class="mb-3">
                    <label class="form-label fw-bold">${INPUT_DATA_TRANS}</label>
                    <textarea name="input_data" class="form-control code-editor" rows="5"></textarea>
                </div>
                <div class="mb-3">
                    <label class="form-label fw-bold">${OUTPUT_DATA_TRANS}</label>
                    <textarea name="output_data" class="form-control code-editor" rows="5"></textarea>
                </div>
                <div class="form-check form-switch mb-3">
                    <input class="form-check-input" type="checkbox" id="id_is_sample" name="is_sample" checked>
                    <label class="form-check-label" for="id_is_sample">${IS_SAMPLE_TRANS}</label>
                </div>
            </div>
        </div>
        <div class="d-grid mt-2">
            <button type="submit" class="btn btn-primary">
                <i class="bi bi-save me-2"></i>${SAVE_TRANS}
            </button>
        </div>
    </form>
</div>
`;

function addTask() {
    const tasksContainer = document.getElementById('tasksContainer');
    const testCases = tasksContainer.querySelectorAll('.test-case');
    const testNumber = testCases.length;

    tasksContainer.insertAdjacentHTML('beforeend', taskTemplate(testNumber, INPUT_DATA_TRANS, OUTPUT_DATA_TRANS, IS_SAMPLE_TRANS, SAVE_TRANS));

    const newTest = tasksContainer.lastElementChild;
    newTest.scrollIntoView({ behavior: 'smooth', block: 'end' });

    newTest.style.animation = 'highlight 1.5s';
    setTimeout(() => {
        newTest.style.animation = '';
    }, 1500);
}

document.getElementById('addTaskButton').addEventListener('click', addTask);