"""

누적합


"""

def prefix_sum_1d(arr):
    """
    핵심 dp[x] := 0 ~ x 까지의 누적합을 의미
    :param arr:
    :return:
    """
    n = len(arr)
    prefix = [0] * (n + 1)  # 0번째는 항상 0으로 시작
    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]
    return prefix

# 사용 예시
arr = [3, 2, 1, 5, 4]
prefix = prefix_sum_1d(arr)

# 구간 [1, 3] (2번째부터 4번째까지)의 합 구하기
left, right = 1, 3
range_sum = prefix[right + 1] - prefix[left]
print(range_sum)  # 출력: 8 (2 + 1 + 5)


def prefix_sum_2d(grid):
    """
    핵심 dp[i][j] -> 0,0 과 i,j 까지 직사각형까지의 누적합을 의미
    :param grid:
    :return:
    """

    n, m = len(grid), len(grid[0])
    prefix = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n):
        for j in range(m):
            prefix[i + 1][j + 1] = (
                    grid[i][j]
                    + prefix[i][j + 1]
                    + prefix[i + 1][j]
                    - prefix[i][j]
            )
    return prefix


# 사용 예시
grid = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
prefix = prefix_sum_2d(grid)

# 구간 [(1,1) ~ (2,2)] 합 구하기 (2x2 중앙)
x1, y1, x2, y2 = 1, 1, 2, 2
range_sum = (
        prefix[x2 + 1][y2 + 1]
        - prefix[x1][y2 + 1]
        - prefix[x2 + 1][y1]
        + prefix[x1][y1]
)
print(range_sum)  # 출력: 28 (5 + 6 + 8 + 9)
