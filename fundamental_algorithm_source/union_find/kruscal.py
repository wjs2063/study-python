def find_parent(parent, x):
    if parent[x] != x:
        parent[x] = find_parent(parent, parent[x])
        return parent[x]
    return parent[x]


def union_find(parent, a, b):
    x1 = find_parent(parent, a)
    x2 = find_parent(parent, b)
    parent[x1] = x2


parent = []
edges = []
# sort by 가중치
edges.sort()
ans = 0
for w, (u, v) in enumerate(edges):
    _u, _v = find_parent(u), find_parent(v)
    if _u == _v: continue
    ans += w
    union_find(parent, _u, _v)

