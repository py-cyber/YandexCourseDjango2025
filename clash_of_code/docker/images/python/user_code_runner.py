import json
import os
from pathlib import Path
import resource
import subprocess


def set_memory_limit(max_memory_mb):
    max_memory_bytes = max_memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (max_memory_bytes, max_memory_bytes))


def run_user_code(user_code, tests, time_limit, memory_limit):
    file = Path('user_code.py')
    file.touch()
    file.write_text(user_code)

    set_memory_limit(memory_limit)

    result = {
        'status': 'AC',
        'test_error': None,
        'message': None,
    }

    for test in tests:
        input_data = test['input_data']
        expected_output = test['output_data']
        test_number = test['number']
        try:
            process = subprocess.run(
                ['python', 'user_code.py'],
                input=input_data,
                check=True,
                text=True,
                capture_output=True,
                timeout=time_limit,
            )

            user_program_output = process.stdout.strip()
            if user_program_output != expected_output.strip():
                result['status'] = 'WA'
                result['test_error'] = test_number
                result['message'] = (
                    f'Wrong answer on test {test_number} '
                    f'received {user_program_output} excepted {expected_output}'
                )
                break

        except subprocess.TimeoutExpired:
            result['status'] = 'TL'
            result['test_error'] = test_number
            result['message'] = f'Time limit exceeded on test {test_number}'
            break

        except Exception as e:
            result['status'] = 'RE'
            result['test_error'] = test_number
            result['message'] = str(e) + ' ' + e.__class__.__name__
            break

    return result


if __name__ == '__main__':
    input_json = os.getenv('input_data')
    data = json.loads(input_json)

    tests = data['tests']
    user_code = data['user_code']
    time_limit = data.get('time_limit', 1)
    memory_limit = data.get('memory_limit', 128)

    result = run_user_code(user_code, tests, time_limit, memory_limit)

    print(json.dumps(result))
