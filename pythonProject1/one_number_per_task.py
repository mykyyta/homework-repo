from multiprocessing import Pool
from datetime import datetime
from tqdm import tqdm
from base_collatz import check_one_number

if __name__ == '__main__':
    start_time = datetime.now()

    total_range = 10**6
    num_processes = 4

    # Завантажуємо по одному числу за раз в кожен процес, замість діапазонів. В цьому випадку виконання займає значно більше часу

    pool = Pool(processes=num_processes)
    for _ in tqdm(pool.imap_unordered(check_one_number, range(1, total_range + 1)), total=total_range):
        pass

    pool.close()
    pool.join()

    end_time = datetime.now()
    print("Execution Time:", end_time - start_time, "\nNumber of processes:", num_processes)