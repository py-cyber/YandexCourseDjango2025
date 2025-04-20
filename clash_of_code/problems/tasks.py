import json

from clash_of_code.celery import app
import problems.models
import core.core


@app.task
def check_auther_solution(pk_task):
    problem = problems.models.Problem.objects.get(pk=pk_task)
    problem.status = problems.models.VerdictChoice.In_processing
    problem.save()

    code = problem.author_solution
    lang = problem.author_language
    tests = problem.tests.all()
    max_time = problem.time_limit
    max_memory = problem.memory_limit

    tests_json = list()
    for test in tests:
        test_json = {
            'input_data': test.input_data,
            'output_data': test.output_data,
            'number': test.number,
        }
        tests_json.append(test_json)

    data = {
        'input_data': json.dumps(
            {
                'tests': tests_json,
                'user_code': code,
                'time_limit': max_time,
                'memory_limit': max_memory,
            },
        ),
    }

    result = core.core.check_tests(data, lang)
    status = result['status']
    test_error = result.get('test_error', None)
    message = result['message']

    if status == problems.models.VerdictChoice.Accept:
        problem.status = status
        problem.test_error = None
        problem.is_correct = True
        problem.save()

    else:
        problem.status = status
        problem.test_error = test_error
        problem.logs = message
        problem.save()
