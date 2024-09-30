from datetime import datetime, timedelta

from ml import ML, ml_homeworks
#from dl import DL, dl_homeworks

start = datetime(2024, 7, 15)
deadline = start + timedelta(days=40)
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
now = datetime.now()
for work in works:
    print(f"{work['title']}:")
    start = work['start']
    left = work['deadline'] - start
    tasks = work['tasks']
    delay = left / len(tasks)
    for p, task in enumerate(tasks):
        ndead = start + delay*(p+1)
        diff = ndead - now
        if diff.total_seconds() > 0:
            desc = f"осталось {ndead-now}"
        else:
            desc = f"просрочен на {now-ndead}"
        #print(f"  Дедлайн {task}: {ndead} ({desc})")
        print(f"{task}\t{ndead}")
    print()
