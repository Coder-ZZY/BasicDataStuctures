import warnings


class Stack:
    def __init__(self):
        self._stack = []
    
    def __repr__(self):
        """Return a representation of the stack."""
        return repr(self._stack)
    
    def __len__(self):
        """Return the number of items in the stack."""
        return len(self._stack)
    
    def __getitem__(self, i):
        """Get the item at the specified index."""
        return self._stack[i]
    
    def batch_push(self, items: list[int|float|str|dict|object]):
        """
        Push multiple items into the stack.
        
        Args:
            items (list[int|float|str|dict|object]): A list of items to be pushed into the stack.
        """
        for item in items:
            self.push(item)
    
    def push(self, item: int|float|str|dict|object):
        """
        push an item into the stack.
        
        Args:
            item(int|float|str|dict|object): the item to be pushed into the stack.
        """
        if item is None:
            return
        self._stack.append(item)
    

    def pop(self):
        """
        pop an item from the stack and return it.
        If the stack is empty, a warning will be raised and None will be returned.
        
        Returns:
            int | float | str | dict | object: The item popped from the stack, or None if the stack is empty.
        """
        
        if len(self._stack) == 0:
            warnings.warn(
                "The stack is empty. Cannot pop an item.",
                category=UserWarning,
                stacklevel=2
            )
            return
        return self._stack.pop()
    
    def clear(self):
        """Clear all items from the stack."""
        self._stack.clear()
        return
    
    @property
    def top(self):
        """
        Get the top element of the stack.
        
        Returns:
            int | float | str | dict | object: The top element of the stack, or None if the stack is empty.
        """
        if len(self._stack) == 0:
            return
        return self._stack[-1]
    
    def index(self, query: int|float|str|dict):
        """
        Get the index of the first occurrence of a query item in the stack.
        Args:
            query (int | float | str | dict): The item to search for in the stack.
        Returns:
            int: The index of the first occurrence of the query item in the stack, or None
            if the item is not found or if the query is None.
        """
        if query is None:
            return
        return self._stack.index(query)
    
    def isEmpty(self):
        """Check if the stack is empty."""
        return len(self._stack) == 0
    
    def to_list(self) -> list:
        """Get a list representation of the stack."""
        return self._stack.copy()
    
    @property
    def data(self):
        """Get the underlying list representing the stack."""
        return self._stack