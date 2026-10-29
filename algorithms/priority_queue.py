"""Reusable Priority Queue Implementation for MediRoute.

This module provides a generic, deterministic Min-Priority Queue backed by Python's
`heapq` module. Equal priorities are handled deterministically using an internal
monotonically increasing counter (stable FIFO tie-breaking), preventing any
direct comparison of stored payload objects.

Theoretical Complexities:
- Insert (push): O(log n)
- Extract Min (pop): O(log n)
- Peek: O(1)
- Length (__len__): O(1)
- Space Complexity: O(n)
"""

from __future__ import annotations
import heapq
from typing import Any, Generic, List, Optional, Tuple, TypeVar

T = TypeVar("T")


class PriorityQueue(Generic[T]):
    """Deterministic Min-Priority Queue using a binary heap.

    Entries are stored as 3-tuples: (priority, entry_count, item).
    The `entry_count` acts as a deterministic tie-breaker when priorities are equal,
    ensuring stability and guaranteeing that the payload item is never evaluated
    by comparison operators (which might not be defined for complex entities).
    """

    def __init__(self) -> None:
        """Initialize an empty priority queue."""
        self._heap: List[Tuple[float, int, T]] = []
        self._counter: int = 0

    def push(self, item: T, priority: float) -> None:
        """Insert an item with a given numeric priority.

        Lower numeric priority values indicate higher urgency / shorter distance.

        Complexity:
            Time: O(log n) where n is the number of elements in the heap.
            Space: O(1) amortized auxiliary.

        Args:
            item: The element to store.
            priority: Numeric weight or priority score (e.g., travel cost, distance).
        """
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self) -> Tuple[T, float]:
        """Remove and return the item with the smallest priority value.

        Complexity:
            Time: O(log n) to re-heapify after extraction.
            Space: O(1) auxiliary.

        Returns:
            A tuple of (item, priority).

        Raises:
            IndexError: If called on an empty queue.
        """
        if self.is_empty():
            raise IndexError("Cannot pop from an empty PriorityQueue")
        priority, _, item = heapq.heappop(self._heap)
        return item, priority

    def pop_item(self) -> T:
        """Convenience method to pop and return only the item payload.

        Returns:
            The highest-priority (minimum value) item.

        Raises:
            IndexError: If called on an empty queue.
        """
        item, _ = self.pop()
        return item

    def peek(self) -> Tuple[T, float]:
        """Inspect the minimum element without removing it.

        Complexity:
            Time: O(1) direct root inspection.
            Space: O(1).

        Returns:
            A tuple of (item, priority).

        Raises:
            IndexError: If called on an empty queue.
        """
        if self.is_empty():
            raise IndexError("Cannot peek into an empty PriorityQueue")
        priority, _, item = self._heap[0]
        return item, priority

    def is_empty(self) -> bool:
        """Check whether the priority queue has no elements.

        Complexity: O(1)
        """
        return len(self._heap) == 0

    def __len__(self) -> int:
        """Return the count of elements currently in the queue.

        Complexity: O(1)
        """
        return len(self._heap)

    def clear(self) -> None:
        """Reset the priority queue to empty state."""
        self._heap.clear()
        self._counter = 0

    def __repr__(self) -> str:
        return f"PriorityQueue(size={len(self._heap)})"
