from clash_of_code.celery import app


@app.task
def check_solution(pk_solution):
    pass