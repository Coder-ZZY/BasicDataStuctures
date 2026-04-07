from typing import Literal
import warnings

class Heap:
    """
    Our implementation of a min-heap or max-heap.
    """

    def __init__(self, arr: list[int | float], type :Literal["min", "max"] = "min"):
        """
        Construct a min or max heap class from a given array.

        Args:
            arr (list[int | float]): Input an array.
            type (Literal["min", "max"], optional): the heap type
        """
        if type not in ("min", "max"):
            raise ValueError("heap type must be min or max!")
        self.type = type
        self.heap_data = arr
        self.heapify()
    
    def __repr__(self) -> str:
        return f"Heap({self.heap_data})"
    
    def __getitem__(self, i):
        return self.heap_data[i]
    
    def __len__(self):
        return len(self.heap_data)
    
    def _compare(self, a: int | float, b: int | float) -> bool:
        """
        Compare two values according to heap type.

        For a min heap, return True if a < b.
        For a max heap, return True if a > b.

        Args:
            a (int | float): First value.
            b (int | float): Second value.

        Returns:
            bool: True if a has higher priority than b 
                  based on heap type, otherwise False.
        """
        if self.type == "min":
            return a < b
        else:
            return a > b

    def sift_down(self, index: int):
        """
        Sift down the heap begins at the specifc index.

        Args:
            index (int): The starting position.
        """
        while True:
            current = index
            left = index * 2 + 1
            right = index * 2 + 2

            if left < len(self.heap_data) and not self._compare(self.heap_data[current], self.heap_data[left]):
                current = left
            if right < len(self.heap_data) and not self._compare(self.heap_data[current], self.heap_data[right]):
                current = right

            if current == index:
                break
            
            self.heap_data[current], self.heap_data[index] = self.heap_data[index], self.heap_data[current]
            index = current

    def sift_up(self, index: int):
        """
        Sift up the heap begins at the specifc index.

        Args:
            index (int): The starting position.
        """
        while True:
            current = index
            father = (index - 1) // 2

            if current > 0 and self._compare(self.heap_data[current], self.heap_data[father]):
                current = father

            if current == index:
                break
            
            self.heap_data[current], self.heap_data[index] = self.heap_data[index], self.heap_data[current]
            index = current

    def heapify(self):
        """
        Init a min or max heap.
        """
        for i in range((len(self.heap_data) - 2)//2, -1, -1):
            self.sift_down(i)
    
    def heappush(self, e: int|float):
        """
        Push an element in the constructed heap.

        Args:
            e (int|float): The element to be pushed.
        """
        self.heap_data.append(e)
        self.sift_up(index = len(self.heap_data) - 1)

    def heappop(self) -> int | float:
        """
        Pop the top element in the constructed heap.

        Returns:
            int | float: The top element of the heap (minimum for min-heap,
            maximum for max-heap
        """
        if len(self.heap_data) == 0:
            warnings.warn(
                "The heap is empty. Cannot pop an item.",
                category=UserWarning,
                stacklevel=2
            )
            return
        if len(self.heap_data) == 1:
            return self.heap_data[0]
        
        val = self.heap_data[0]
        self.heap_data[0] = self.heap_data[-1]
        self.heap_data.pop()
        self.sift_down(0)

        return val
    
    def heapreplace(self, e: int | float):
        """
        Replace the top element of the heap with a new element.

        This operation is more efficient than calling heappop()
        followed by heappush().

        Args:
            e (int | float): The new element to insert.

        Returns:
            int | float: The original top element of the heap.

        Raises:
            IndexError: If the heap is empty.
        """
        if not self.heap_data:
            warnings.warn(
                "The heap is empty. Cannot pop an item before replacing.",
                category=UserWarning,
                stacklevel=2
            )
            self.heap_data.append(e)
            return
        val = self.heap_data[0]
        self.heap_data[0] = e
        self.sift_down(0)
        return val
    
    @property
    def heaptop(self):
        """
        Get the top element of heap.

        Returns:
            int | float: The top element of the heap.

        Raises:
            IndexError: If the heap is empty.
        """
        if not self.heap_data:
            warnings.warn(
                "The heap is empty. Cannot pop an item before replacing.",
                category=UserWarning,
                stacklevel=2
            )
            self.heap_data.append(e)
            return
        return self.heap_data[0]