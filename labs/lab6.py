import datetime
import math
import matplotlib.pyplot as plt

# Рекурсия
def F_rec(n):
    if n == 1:
        return 1
    else:
        G_n = G_rec(n - 1)
        sign = -1 if n % 2 == 0 else 1
        return sign * (F_rec(n - 1) - 2 * G_n)

def G_rec(n):
    if n == 1:
        return 1
    else:
        F_n = F_rec(n - 1)
        return -F_n + math.factorial(2 * n - 1)

# Итерация
def F_it(n):
    if n == 1:
        return 1

    prev_F = 1
    prev_G = 1
    sign = -1
    # Факториал (2*i - 1)!
    fact_val = 1

    for i in range(2, n + 1):
        for k in range(2 * (i - 1) + 1, 2 * i):
            fact_val *= k

        sign *= -1
        curr_G = -prev_F + fact_val
        curr_F = sign * (prev_F - 2 * prev_G)

        prev_F, prev_G = curr_F, curr_G

    return prev_F

# Измерение времени
n_values_rec = range(1, 11)
n_values_it = range(1, 21)

rec_time = []
it_time = []

# Замер рекурсии
for n in n_values_rec:
    start = datetime.datetime.now()
    F_rec(n)
    duration = (datetime.datetime.now() - start).total_seconds()
    rec_time.append(duration)

# Замер итерации
for n in n_values_it:
    start = datetime.datetime.now()
    F_it(n)
    duration = (datetime.datetime.now() - start).total_seconds()
    it_time.append(duration)

# Таблица результатов
print(f"{'n':<5} {'Рекурсия (с)':<15} {'Итерация (с)':<15}")
for n, rt, it in zip(n_values_rec, rec_time, it_time[:len(n_values_rec)]):
    print(f"{n:<5} {rt:<15.6f} {it:<15.6f}")

plt.figure(figsize=(10, 6))
plt.plot(n_values_rec, rec_time, label='Рекурсия', marker='o')
plt.plot(n_values_it, it_time, label='Итерация', marker='x')

plt.title('Сравнение времени выполнения рекурсии и итерации')
plt.xlabel('n')
plt.ylabel('Время (секунды)')
plt.legend()
plt.grid(True)
plt.ylim(0, max(it_time) * 1.1)
plt.tight_layout()
plt.show()