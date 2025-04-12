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


const taskTemplate = (testNumber, INPUT_DATA_TRANS, OUTPUT_DATA_TRANS, IS_SAMPLE_TRANS, SAVE_TRANS) =>
    `<div class="task" data-index="${testNumber}">
        <div class="container mt-4">
            <div class="card">
                <div class="card-body">
                    <form method="post" enctype="multipart/form-data">
                            <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie("csrftoken")}">
                              <input type="hidden" name="number" value="${ testNumber + 1 }">
                              <input type="hidden" name="pk">

                              <div class="row">
                                  <div class="col-10">
                                      <div class="mb-3">
                                          <label for="id_input_data" class="form-label">${INPUT_DATA_TRANS}</label>
                                          <input type="text" id="id_input_data" name="input_data" class="form-control">
                                      </div>
                                      <div class="mb-3">
                                          <label for="id_output_data" class="form-label">${OUTPUT_DATA_TRANS}</label>
                                          <input type="text" id="id_output_data" name="output_data" class="form-control">
                                      </div>
                                      <div class="mb-3">
                                          <label for="id_is_sample" class="form-label">${IS_SAMPLE_TRANS}</label>
                                          <input type="checkbox" id="id_is_sample" name="is_sample" class="form-check-input" checked>
                                      </div>
                                  </div>
                                  <div class="col-2 d-flex flex-column justify-content-center">
                                      <button type="button" class="btn btn-danger">
                                        <i class="bi bi-trash"></i> X
                                      </button>
                                      <button type="button" class="btn btn-primary mb-2 move-up-button">↑</button>
                                      <button type="button" class="btn btn-primary move-down-button">↓</button>
                                  </div>
                              </div>
                              <button type="submit" class="btn btn-primary w-100">${ SAVE_TRANS }</button>
                          </form>
                      </div>
                  </div>
              </div>
    </div>
    `
;


function addTask() {
    const tasksContainer = document.getElementById('tasksContainer');
    const childDivs = Array.from(tasksContainer.children).filter(child => child.tagName === 'DIV');
    numberOfElements = childDivs.length;
    tasksContainer.insertAdjacentHTML('beforeend', taskTemplate(numberOfElements, INPUT_DATA_TRANS, OUTPUT_DATA_TRANS, IS_SAMPLE_TRANS, SAVE_TRANS));
}

document.getElementById('addTaskButton').addEventListener('click', addTask);


