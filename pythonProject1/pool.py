from collatz_homework import check_one_chunk
from multiprocessing import Pool
from datetime import datetime
from tqdm import tqdm

chunks = 100000
total_range = 10**9
num_processes = 8

if __name__ == '__main__':
    start_time = datetime.now()

    step = total_range // chunks
    tasks = [(i * step + 1, (i + 1) * step) for i in range(chunks)]

    pool = Pool(processes=num_processes)
    for _ in tqdm(pool.imap_unordered(check_one_chunk, tasks), total=len(tasks)):
        pass

    end_time = datetime.now()
    print("Total time:", end_time - start_time)