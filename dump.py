import sys, json
data = json.load(open('../zomato (1).ipynb', encoding='utf-8'))
with open('notebook_cells.txt', 'w', encoding='utf-8') as f:
    for i, c in enumerate(data['cells']):
        f.write(f'\n--- Cell {i} ({c.get("cell_type", "")}) ---\n')
        f.write(''.join(c.get('source', [])))
