import docker
import json

import problems.models


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
