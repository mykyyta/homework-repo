from datetime import datetime
from multiprocessing import Process, Queue
from tqdm import tqdm

def check_one_chunk(range_):
    """
    перевірка чисел на відрізку (start_of_chunk, end_of_chunk) за правилом Collatza
    припускається що всі числа менше start_of_chunk вже перевірено

    якщо функція завершує роботу перевірку пройдено
    """
    already_checked = {1, 2, 4} # створюємо початковий сет вже перевірених чисел
    start_of_chunk, end_of_chunk = range_
    for initial_n in tqdm(range(start_of_chunk, end_of_chunk+1)): # перебираємо числа на обранному відрізку
        collatz_sequence = []
        n = initial_n



        if initial_n  in already_checked: # якщо число в сеті перевірених чисел, видаляємо та переходимо до наступного числа
            already_checked.remove(initial_n )
            continue

        while True: # генеруємо послідовність поки не дійдемо до числа, що менше за початкове
            if n % 2 == 0:
                n //= 2
            else:
                n = n * 3 + 1

            if n < initial_n:
                break

            collatz_sequence.append(n)

        already_checked.update(collatz_sequence) #додаємо послідовність поточного числа в список вже перевірених чисел

def worker(queue):
    while True:
        chunk = queue.get()  # отримуємо наступний відрізок із черги
        if chunk is None: # якщо отримано маркер завершення (None), припиняємо роботу
            break
        check_one_chunk(chunk) # викликаємо функцію перевірки для заданого відрізка

if __name__ == '__main__':
    start_time = datetime.now()

    chunks = 30000 # кількість відрізків для перевірки
    total_range = 10**6 # ліміт чисел
    num_processes = 4 # кількість процесів

    task_queue = Queue() #cтворюємо чергу задач

    step = total_range // chunks
    for i in range(chunks): # ділимо на відрізки створюємо задачі для кожного відрізка
        start = i * step + 1
        end = (i + 1) * step
        task_queue.put((start, end))

    processes = []
    for _ in range(num_processes): # створюємо задану кількість процесів
        p = Process(target=worker, args=(task_queue,))
        processes.append(p)
        p.start()

    for _ in range(num_processes): # додаємо маркери завершення (None) для кожного процесу
        task_queue.put(None)

    for p in processes:
        p.join()

    end_time = datetime.now()
    print(end_time - start_time) # виводимо тривалість виконання
