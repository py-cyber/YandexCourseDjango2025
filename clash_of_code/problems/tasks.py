import json

import docker

from clash_of_code.celery import app
import problems.models
import submissions.models


@app.task
def check_solution(pk_solution):
    solution = submissions.models.Submission.objects.get_full_submit(pk=pk_solution)
    solution.status = problems.models.VerdictChoice.In_processing
    solution.save()

    code = solution.code
    lang = solution.language
    tests = solution.problem.tests
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
            }
        )
    }

    result = check_tests(data, lang)
    status = result['status']
    test_error = result['test_error']
    message = result['message']

    if status == problems.models.VerdictChoice.Accept:
        solution.status = status

    else:
        solution.status = status
        solution.test_error = problems.models.TestCase.objects.get(
            problem=solution.problem,
            number=test_error,
        )
        solution.logs = message

    solution.save()


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
            }
        )
    }

    result = check_tests(data, lang)
    print(result)
    status = result['status']
    test_error = result.get('test_error', None)
    message = result['message']

    if status == problems.models.VerdictChoice.Accept:
        problem.status = status
        problem.test_error = None
        problem.is_correct = True

    else:
        problem.status = status
        problem.test_error = test_error
        problem.logs = message

    problem.save()


def check_tests(data, lang):
    client = docker.from_env()
    if lang == problems.models.LanguageChoices.Python_3_11:
        try:
            container = client.containers.run(
                'python3_11_image',
                environment=data,
                remove=True,
                stdout=True,
                stderr=True,
                detach=False,
            )

            logs = container.decode('utf-8')
            return json.loads(logs)
        except Exception as e:
            return {
                'status': 'CE',
                'message': str(e),
            }

    return {
        'status': 'CE',
        'message': 'Language is not found in test system',
        'test_error': None,
    }
