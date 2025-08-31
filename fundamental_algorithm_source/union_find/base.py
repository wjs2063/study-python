"""
서로소 집합을 구하는 알고리즘
유니온 파인드

보통 무방향 그래프에서 많이 씀


"""


def find_parent(parent, x):
    if parent[x] == x:
        return x
    return find_parent(parent, parent[x])


def union(parent, a, b):
    xa = find_parent(parent, a)
    xb = find_parent(parent, b)

    parent[xa] = xb
