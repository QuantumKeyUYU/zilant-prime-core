#!/usr/bin/env bash
set -euo pipefail

#
# Cross-platform reproducible-build check
#

# 1) Найти python
if   command -v python3 &>/dev/null; then
    PY=python3
elif command -v python   &>/dev/null; then
    PY=python
elif command -v py       &>/dev/null; then
    PY="py -3"
else
    echo "❌ Не найден Python (хотели python3, python или py-3)" >&2
    exit 1
fi

echo "╭─ Using interpreter: $PY"
echo "╰─"

# 2) Очистить прошлые сборки
rm -rf build_a build_b sums_a.txt sums_b.txt

# 3) Первая сборка
echo "→ First build…"
$PY -m build --sdist --wheel --outdir build_a

# 4) Вторая сборка
echo "→ Second build…"
$PY -m build --sdist --wheel --outdir build_b

# 5) Собрать SHA256 и отсортировать
echo "→ Hashing artifacts…"
(
  sha256sum build_a/* | sort
) > sums_a.txt

(
  sha256sum build_b/* | sort
) > sums_b.txt

# 6) Сравнить результаты
echo "→ Comparing…"
if ! diff -u sums_a.txt sums_b.txt; then
  echo "❌ Reproducibility check failed!" >&2
  exit 1
fi

echo "✅ Builds are reproducible"
