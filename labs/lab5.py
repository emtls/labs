from itertools import product
from datetime import datetime


# Часть 1: Распределение предметов
def recursive_distribution(T, K):
    def generate(current, remaining, results):
        if len(current) == K:
            if remaining == 0:
                results.append(tuple(current))
            return
        for items in range(remaining + 1):
            generate(current + [items], remaining - items, results)

    results = []
    generate([], T, results)
    return results


def functional_distribution(T, K):
    return [p for p in product(range(T + 1), repeat=K) if sum(p) == T]


# Часть 2: Оптимальное распределение предметов
def assign_items_to_people(item_ids, distribution):
    num_people = max(distribution) + 1
    people = [[] for _ in range(num_people)]
    for item_id, person_idx in zip(item_ids, distribution):
        people[person_idx].append(item_id)
    return [sorted(group) for group in people]


def find_optimal_distribution(total_items, total_people, min_items=1, max_items=2):
    distributions = set()
    roughness_values = []

    item_ids = list(range(1, total_items + 1))

    for pattern in product(range(total_people), repeat=total_items):
        used_people = set(pattern)
        if len(used_people) < total_people:
            continue

        distribution = assign_items_to_people(item_ids, pattern)

        counts = [len(group) for group in distribution]
        if min(counts) < min_items or max(counts) > max_items:
            continue

        key = tuple(tuple(group) for group in distribution)
        if key in distributions:
            continue
        distributions.add(key)

        roughness = max(counts) - min(counts)
        roughness_values.append((distribution, roughness))

    if not roughness_values:
        print("Не найдено допустимых распределений.")
        return [], 0

    min_roughness = min(r[1] for r in roughness_values)
    best_options = [r for r in roughness_values if r[1] == min_roughness]

    return best_options[0], len(distributions)


def print_execution_time(label, start, end):
    print(f"{label}: время выполнения = {(end - start).total_seconds():.6f} сек")


# Тестирование первой части
print("Часть 1: Сравнение методов распределения предметов")
T, K = 3, 3

all_items = list(range(1, T + 1))
all_combinations = list(product(all_items, repeat=K))
unique_distributions = [c for c in all_combinations if sorted(c) == all_items]

# Рекурсивный метод
start = datetime.now()
rec_dist = recursive_distribution(T, K)
print_execution_time("Рекурсивный метод", start, datetime.now())

print(f"Рекурсивный метод ({len(unique_distributions)} вариантов):")
for dist in unique_distributions:
    print(dist)

#Функциональный метод
start = datetime.now()
func_dist = functional_distribution(T, K)
print_execution_time("Функциональный метод", start, datetime.now())

print(f"\nФункциональный метод ({len(unique_distributions)} вариантов):")
for dist in unique_distributions:
    print(dist)

#Тестирование второй части
print("\nЧасть 2: Оптимальное распределение предметов")
total_items = 7
total_people = 4

start = datetime.now()
result = find_optimal_distribution(total_items, total_people, min_items=1, max_items=2)
print_execution_time("Оптимальное распределение", start, datetime.now())

if result == ([], 0):
    print("Невозможно распределить предметы в рамках заданных ограничений.")
else:
    (best_dist, roughness), total_dists = result
    print(f"\nОптимальное распределение:", best_dist)
    print("Разница в количестве предметов:", roughness)