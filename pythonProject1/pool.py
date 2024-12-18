from base_collatz import check_one_chunk
from multiprocessing import Pool, cpu_count
from datetime import datetime
from tqdm import tqdm

chunks = 1000
total_range = 10**8
num_processes = 4

if __name__ == '__main__':
    start_time = datetime.now()

    step = total_range // chunks
    tasks = [(i * step + 1, (i + 1) * step) for i in range(chunks)]

    pool = Pool(processes=num_processes)
    for _ in tqdm(pool.imap_unordered(check_one_chunk, tasks), total=chunks):
        pass

    pool.close()
    pool.join()

    end_time = datetime.now()
    print("Execution Time:", end_time - start_time, "\nNumber of processes:", num_processes)