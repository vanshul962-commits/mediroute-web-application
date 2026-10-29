"""Unit tests for the PriorityQueue implementation."""

import pytest
from algorithms.priority_queue import PriorityQueue


class NonComparableItem:
    """An object without comparison operators defined, to test tie-breaker stability."""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"Item({self.name})"


def test_priority_queue_basic_ordering():
    """Verify that items are popped in increasing order of priority."""
    pq = PriorityQueue[str]()
    pq.push("medium", 5.0)
    pq.push("highest", 1.0)
    pq.push("lowest", 10.0)
    pq.push("second", 2.5)

    assert len(pq) == 4
    item, prio = pq.pop()
    assert item == "highest"
    assert prio == 1.0

    item, prio = pq.pop()
    assert item == "second"
    assert prio == 2.5

    assert pq.pop_item() == "medium"
    assert pq.pop_item() == "lowest"
    assert pq.is_empty()


def test_priority_queue_equal_priority_tie_breaking():
    """Verify deterministic FIFO ordering for equal priority without comparing items."""
    pq = PriorityQueue[NonComparableItem]()
    item1 = NonComparableItem("first")
    item2 = NonComparableItem("second")
    item3 = NonComparableItem("third")

    # All pushed with identical priority 3.0
    pq.push(item1, 3.0)
    pq.push(item2, 3.0)
    pq.push(item3, 3.0)

    # Must pop in insertion order without raising comparison errors
    popped1, p1 = pq.pop()
    popped2, p2 = pq.pop()
    popped3, p3 = pq.pop()

    assert popped1.name == "first"
    assert popped2.name == "second"
    assert popped3.name == "third"
    assert p1 == p2 == p3 == 3.0


def test_priority_queue_peek():
    """Verify peek retrieves the minimum element without removing it."""
    pq = PriorityQueue[str]()
    pq.push("apple", 4.0)
    pq.push("banana", 2.0)

    item, prio = pq.peek()
    assert item == "banana"
    assert prio == 2.0
    assert len(pq) == 2  # Length unchanged


def test_priority_queue_empty_behavior():
    """Verify appropriate IndexError when popping or peeking into an empty queue."""
    pq = PriorityQueue[str]()
    assert pq.is_empty()
    assert len(pq) == 0

    with pytest.raises(IndexError):
        pq.pop()

    with pytest.raises(IndexError):
        pq.peek()
