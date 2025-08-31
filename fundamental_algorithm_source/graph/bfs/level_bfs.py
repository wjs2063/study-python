
"""
https://leetcode.com/submissions/detail/1697358452/

"""

class Solution:
    def connect(self, root: 'Optional[Node]') -> 'Optional[Node]':
        # L V R
        from collections import deque

        if not root: return root
        q = deque([root])  # (level,root)

        while q:
            size = len(q)
            # 트리의 같은 레벨의 노드 개수만큼만 돌아감
            # O(최대 너비 개수)
            for idx in range(size):
                node = q.popleft()

                # 끝점 제외
                if idx < size - 1:
                    node.next = q[0]

                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
        return root