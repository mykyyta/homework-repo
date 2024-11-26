from collatz_homework import check_one_chunk
from multiprocessing import Process, Queue, Pool
from datetime import datetime

chunks = 10000
total_range = 10**6
num_processes = 4

if __name__ == '__main__':
    start_time = datetime.now()

    step = total_range // chunks
    tasks = [(i * step + 1, (i + 1) * step) for i in range(chunks)]

    with Pool(processes=num_processes) as pool:
        pool.starmap(check_one_chunk, tasks)

    end_time = datetime.now()
    print("Total time:", end_time - start_time)