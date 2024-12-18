from datetime import datetime
start_time = datetime.now()

checked = {1}
initial_n = 1
while True:
    if initial_n in checked:
        checked.remove(initial_n)
        initial_n += 1
        continue
    n = initial_n
    while True:
        if n % 2 == 0:
            n //= 2
        else:
            n = n * 3 + 1
        if n < initial_n:
            break
        if n < 10000000:
            checked.add(n)

    initial_n += 1
    if initial_n == 10000000:
        break

end_time = datetime.now()
print("Execution Time:", end_time - start_time, len(checked))

