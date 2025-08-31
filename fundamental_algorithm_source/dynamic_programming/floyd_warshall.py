"""

모든 정점쌍의 최단거리를 구하는 알고리즘

시간복잡도 O(V^3)

핵심 아이디어 := dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])



"""

def floyd_warshall(graph, n):
    dist = [[float('inf')] * n for _ in range(n)]
    for u in range(n):
        dist[u][u] = 0
    for u in graph:
        for v, w in graph[u]:
            dist[u][v] = w

    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    return dist
