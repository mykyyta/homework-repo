from datetime import datetime
from multiprocessing import Process, Queue

def check_one_number(initial_n): # Перевіряє одне числа
    if initial_n == 1:
        return
    n = initial_n
    while True:
        if n % 2 == 0:
            n //= 2
        else:
            n = n * 3 + 1
        if n < initial_n: # припускається, що попередні числа вже перевірено
            break

def check_one_chunk(chunk_range): # Перевіряє діапазон чисел
    for initial_n in range(*chunk_range):
        check_one_number(initial_n)

def worker(queue): # отримує задачу (діапазон чисел) з черги і передає її функції перевірки
    while True:
        chunk = queue.get()
        if chunk is None:
            break
        check_one_chunk(chunk)

if __name__ == '__main__':
    start_time = datetime.now()

    chunks = 1000 # кількість відрізків, задач
    total_range = 10**8 # ліміт всього діапазону
    num_processes = 4 # кількість процесів

    task_queue = Queue()

    step = total_range // chunks # розбиваємо загальний діапазон на частини (chunks) та додаємо в чергу
    for i in range(chunks):
        start = i * step + 1
        end = (i + 1) * step
        task_queue.put((start, end))

    processes = []
    for _ in range(num_processes): # створюємо і запускаємо задану кількість процесів
        p = Process(target=worker, args=(task_queue,))
        processes.append(p)
        p.start()

    for _ in range(num_processes): # маркери завершення
        task_queue.put(None)

    for p in processes:
        p.join()

    end_time = datetime.now()
    print("Execution Time:", end_time - start_time, "\nNumber of processes:", num_processes)
