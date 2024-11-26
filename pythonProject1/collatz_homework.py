from datetime import datetime
from multiprocessing import Process, Queue, Pool
from tqdm import tqdm

def check_one_chunk(start_, end_):
    already_checked = {1}
    for number in range(start_, end_+1):
        sequence = []
        x = number
        while (x not in already_checked) and (x >= number):
            sequence.append(x)
            if x % 2 == 0:
                x //= 2
            else:
                x = x * 3 + 1
        already_checked.update(sequence)
        already_checked.remove(number)

chunks = 10000
total_range = 10**9
num_processes = 4

def worker(queue):
    while True:
        chunk = queue.get()
        if chunk is None:
            break
        check_one_chunk(*chunk)

if __name__ == '__main__':
    task_queue = Queue()

    processes = []
    start_time = datetime.now()
    for _ in range(num_processes):
        p = Process(target=worker, args=(task_queue,))
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
