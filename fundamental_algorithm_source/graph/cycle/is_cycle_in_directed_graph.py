"""
방향 그래프에서 사이클 판별 알고리즘
"""



graph = {}
n = len(graph)
state = [0] * n


def is_cycle(node, graph: dict, state: list[int]) -> bool:
    # 현재 노드로부터 출발할때 사이클이 존재하는가?
    n = len(graph)
    """
    state[node] 
    0 : 미방문 
    1 : 방문중 
    2 : 방문완료
    
    graph[node] = [a,b,c] -> node 에서 a,b,c로 나가는 방향 
    
    """

    # 방문중 체크
    state[node] = 1

    for next_node in graph[node]:
        if state[next_node] == 0:
            if is_cycle(next_node, graph, state):
                return True
        elif state[next_node] == 1:
            return True
    # 방문 완료
    state[node] = 2
    return False

def has_cycle(graph: dict[int, list[int]]) -> bool:
    """
    방향 그래프 전체에 대해 사이클 존재 여부를 반환
    """
    n = len(graph)
    state = [0] * n
    for node in range(n):
        if state[node] == 0:
            if is_cycle(node, graph, state):
                return True
    return False