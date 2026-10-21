for f in maps/*/*.txt; do
    echo "$f: $(python3 main.py "$f" | wc -l) turns"
done