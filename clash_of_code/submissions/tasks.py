import json

from clash_of_code.celery import app
import core.core
import problems.models
import submissions.models


@app.task
def check_solution(pk_solution):
    solution = submissions.models.Submission.objects.get_full_submit(pk=pk_solution)
    solution.verdict = problems.models.VerdictChoice.In_processing
    solution.save()

    code = solution.code
    lang = solution.language
    tests = solution.problem.tests.all()
    max_time = solution.problem.time_limit
    max_memory = solution.problem.memory_limit

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
    message = result.get('message', '')

    if status == problems.models.VerdictChoice.Accept:
        solution.verdict = status
        solution.test_error = None
        solution.logs = None
    else:
        solution.verdict = status
        if test_error is not None:
            solution.test_error = problems.models.TestCase.objects.get(
                problem=solution.problem,
                number=test_error,
            )

        solution.logs = message

    solution.save()
