# BasicDataStructure

A Python library of common data structures frequently used in LeetCode problems, including graphs, heaps, stacks, queues, linked lists, tries, and more.

## Features

- 📦 Clean, reusable implementations of essential data structures
- ✅ Designed for LeetCode-style algorithmic problems
- 🐍 Pure Python, no external dependencies
- 🧩 Easy to import and integrate into your solutions

## Installation
- Go to the release page: [Release Page](https://github.com/Coder-ZZY/BasicDataStuctures/releases)
- Download the `basicdatastructure-*.whl`

```bash
pip install /path/to/your/dowload/file/basicdatastructure-*.whl
```

Or install from source:

```bash
git clone https://github.com/Coder-ZZY/BasicDataStuctures.git
# install the package tool
pip install build

# just package the entire project
python -m build

# only generate the wheel file
python -m build --wheel
```

## Data Structures Included

| Category | Structures |
|---|---|
| **Linear** | Stack |
| **ListNode** | Singly Linked List |
| **Tree** | Binary Tree |
| **Heap** | Min Heap, Max Heap |
| **Graph** | Graph |
| **Trie** | Trie (Prefix Tree) |

## Quick Start

```python
# Stack
from BasicDataStructure import Stack

stack = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())   # 2
print(stack.top)  # 1

# Heap (min by default)
from BasicDataStructure import Heap
a = [0, 1, 2]
min_heap = Heap(a)            # min heap by default
max_heap = Heap(a, type="max")  # max heap

min_heap.heappush(3)
min_heap.heappush(1)
min_heap.heappush(2)
print(min_heap.heappop())  # 1

# Graph
from BasicDataStructure import Graph

g = Graph(directed=False)
g.add_edge(0, 1)
g.add_edge(1, 2)
g.add_edge(2, 3)
print(g.neighbors(1))  # [0, 2]

# Trie
from BasicDataStructure import Trie

trie = Trie()
trie.insert("apple")
trie.insert("app")
print(trie.search("apple"))      # True
print(trie.starts_with("app"))   # True
print(trie.search("ap"))         # False
```

## API Reference

### Stack
```python
stack = Stack()
stack.push(val)       # Push element
stack.pop()           # Pop and return top element
stack.top           # Return top element without removing
stack.isEmpty()      # Return True if empty
len(stack)            # Number of elements
```

### Heap
```python
"""
The Heap API is same to the official heap library, which only provides the min-heap: heapq(https://docs.pythonlang.cn/3/library/heapq.html)
"""
heap = Heap(type="min")   # type="min" (default) or type="max"
heap.heappush(val)            # Insert element
heap.heappop()                # Remove and return min or max
heap.heapreplace(val) # Replace the top element of the heap with a new element.
heap.heaptop # Get the top element of heap.
len(heap)                 # Number of elements
```

### Graph
```python
g = Graph(directed=False)   # Undirected by default
g.add_edge(u, v, weight=1)  # Add edge (optional weight)
g.neighbors(u)              # List of neighbor nodes
g.bfs(start)                # BFS traversal from start node
g.dfs(start)                # DFS traversal from start node
```

### Trie
```python
trie = Trie()
trie.insert(word)           # Insert a word
trie.search(word)           # Return True if word exists
trie.startsWith(prefix)    # Return True if any word has this prefix
trie.delete(word)           # Remove a word
```

### TreeNode
```python
a = [1, 2, 3]
root = TreeNode.from_list(a)
root.val                    # Root value
root.left                   # Left child
root.right                  # Right child
```

### ListNode
```python
a = [1 ,2 ,3]
head = ListNode.from_list(a)
head.val                   # Head value
head.next                  # Next node
```

## Use Cases (LeetCode Examples)

- **Stack** — Valid Parentheses (#20), Daily Temperatures (#739), Largest Rectangle in Histogram (#84)
- **Heap** — Kth Largest Element (#215), Merge K Sorted Lists (#23), Task Scheduler (#621)
- **Graph** — Course Schedule (#207), Word Ladder (#127), Network Delay Time (#743)
- **Trie** — Implement Trie (#208), Word Search II (#212), Design Search Autocomplete (#642)

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a Pull Request

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.