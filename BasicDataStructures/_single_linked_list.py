class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    @staticmethod
    def from_list(arr: list[int]):
        if not arr:
            return None
        head = ListNode(arr[0])
        cur = head
        for x in arr[1:]:
            cur.next = ListNode(x)
            cur = cur.next
        return head
    
    def __repr__(self):
        current = self
        val_list = []
        while current:
            val_list.append(current.val)
            current = current.next
        return repr(val_list)