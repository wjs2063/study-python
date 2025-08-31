"""
다익스트라 알고리즘

한 정점에서 다른모든 노드까지의 최단거리를 구하는 알고리즘

V : Vertext
E : Edge

G(V,E)가 정의되어있을때 start에서 다른 모든노드까지가는 최단 경로

O(V * Log E)



"""

import heapq


def dijkstra(graph: dict, start: int, destination: int) -> list:
    distance = [float('inf')] * len(graph)
    # start 지점 초기화
    distance[start] = 0

    h = [(0, start)]

    while h:
        cost, node = heapq.heappop(h)

        for next_node, next_cost in graph[node]:
            if distance[next_node] < cost + next_cost: continue
            heapq.heappush(h, (cost + next_cost, next_node))
    return distance
