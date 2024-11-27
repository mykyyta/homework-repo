from datetime import datetime
from multiprocessing import Process, Queue, Manager

def check_one_chunk(start_of_chunk, end_of_chunk, shared_checked):
    for candidate in range(start_of_chunk, end_of_chunk+1): # перебираємо числа на обраному відрізку
        collatz_sequence = []
        n = candidate

        if candidate in shared_checked: # якщо число в сеті перевірених чисел, видаляємо та переходимо до наступного числа
            continue

        while True: # генеруємо послідовність поки не дійдемо до числа, що менше за початкове
            if n % 2 == 0:
                n //= 2
            else:
                n = n * 3 + 1

            if n < candidate: #or (n in already_checked):
                break

            collatz_sequence.append(n)

        for number in collatz_sequence:
            shared_checked[number] = True #додаємо послідовність поточного числа в список вже перевірених чисел

def worker(queue, shared_checked):
    while True:
        chunk = queue.get()
        if chunk is None:
            break
        check_one_chunk(*chunk, shared_checked)

if __name__ == '__main__':
    start_time = datetime.now()

    chunks = 1000
    total_range = 10 ** 6
    num_processes = 4

    manager = Manager()
    shared_checked = manager.dict({1: True, 2: True, 4: True})  # Використовуємо dict як заміну множині
    task_queue = Queue()

    task_queue = Queue()
    processes = []
    for _ in range(num_processes):
        p = Process(target=worker, args=(task_queue, shared_checked))
        processes.append(p)
        p.start()

    for i in range(chunks):
        step = total_range // chunks
        start = i * step + 1
        end = i * step + step
        task_queue.put((start, end))

    for _ in range(num_processes):
        task_queue.put(None)

    for p in processes:
        p.join()

    end_time = datetime.now()
    print(end_time - start_time)
