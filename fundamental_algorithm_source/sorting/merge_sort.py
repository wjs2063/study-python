"""

병합정렬

분할정복

항상 절반으로 나누어서 좌,우측 정렬

2씩 반틈 나눠지기 떄문에 log2

O(NlogN)


"""


def merge_sort(arr):
    n = len(arr)

    if n <= 1:
        return arr

    left = merge_sort(arr[:n // 2])
    right = merge_sort(arr[n // 2:])

    ans = []
    i, j, k = 0, 0, 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            ans.append(left[i])
            i += 1
            k += 1
        elif left[i] >= right[j]:
            ans.append(right[j])
            j += 1
            k += 1
    while i < len(left):
        ans.append(left[i])
        i += 1
        k += 1
    while j < len(right):
        ans.append(right[j])
        j += 1
        k += 1
    return ans

arr = [0,0,0,-3,100,-2,-1.5,-2.1,-2,-2,50,50,30,20]

print(merge_sort(arr))