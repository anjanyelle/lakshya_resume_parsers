with open('main.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'quality' in line.lower():
            print(f"{i}: {line.strip()}")
