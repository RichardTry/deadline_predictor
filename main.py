from datetime import datetime, timedelta
from yaml import safe_load

from ml import ML, ml_homeworks
#from dl import DL, dl_homeworks

# start = datetime(2024, 7, 15)
# deadline = start + timedelta(days=40)
start = None
deadline = None
works = (
    # {
    #     'title': 'Контест 6',
    #     'start': datetime(2024,6,17,20,30),
    #     'deadline': datetime(2024,6,20,23,59),
    #     'tasks': 4
    # },
    {
        'title': 'Домашка 1 Генеративные Модели',
        'start': datetime(2024,9,25,16,0,0),
        'deadline': datetime(2024,10,1,0,0,0) - timedelta(minutes=10),
        'tasks': [
            'Подготовка данных',
            'Реализация Decoder-сети',
            '-||-',
            '-||-',
            '-||-',
            '-||-',
            '-||-',
            'Обучение модели',
            '-||-',
            'Метрики качества',
            '-||-',
            'Обучение модели',
            'Дополните метод generate...',
            '-||-',
            'Реализуйте стратегию Nucleus Sampling...',
            '-||-',
            'Реализуйте стратегию Beam Search...',
            '-||-'
        ]
    },
)

def iterate_tasks(tasks):
    if type(tasks) in (int, float):
        yield tasks
    elif type(tasks) in (tuple, list):
        yield sum(tasks)
    elif type(tasks) == dict:
        yield sum([iterate_tasks(t) for t in tasks.values()])
    else:
        print('>>>>>>', type(tasks), tasks)

def sum_points(tasks):
    if type(tasks) in (int, float):
        return tasks
    elif type(tasks) in (tuple, list):
        return sum(tasks)
    elif type(tasks) == dict:
        return sum([sum_points(t) for t in tasks.values()])
    else:
        print('>>>>>>', type(tasks), tasks)

f = open('tasks/genmodels/hw_2.yaml')
hw2 = safe_load(f)
hw2['title'] = 'Домашка 2'
works = (hw2,)

print(iterate_tasks)

exit()

now = datetime.now()
for work in works:
    print(f"{work['title']}:")
    start = work['start']
    left = work['deadline'] - start
    tasks = work['tasks']
    delay = left / sum_points(tasks)
    cumulative_sum = 0
    for p, task in enumerate(tasks):
        ndead = start + delay * cumulative_sum
        diff = ndead - now
        if diff.total_seconds() > 0:
            desc = f"осталось {ndead-now}"
        else:
            desc = f"просрочен на {now-ndead}"
        #print(f"  Дедлайн {task}: {ndead} ({desc})")
        print(f"{task}\t{ndead}")
    print()
