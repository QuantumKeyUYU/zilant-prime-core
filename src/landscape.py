import random

def create_landscape(width, height):
    """
    Генерирует матрицу размера width×height со случайными float [0.0, 1.0).
    """
    return [
        [random.random()  # nosec B311
         for _ in range(width)]
        for _ in range(height)
    ]

def save_landscape(landscape, path):
    """
    Сохраняет ландшафт в текстовый файл, строки разделяются новой строкой,
    значения в строке — через запятую.
    """
    with open(path, 'w', encoding='utf-8') as f:
        for row in landscape:
            f.write(','.join(f"{v:.6f}" for v in row) + "\n")
