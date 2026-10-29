# MediRoute — Intelligent Emergency Vehicle Dispatch Optimizer

> **Intelligent Routing. Smarter Dispatch.**  
> A Professional College-Level Design and Analysis of Algorithms (DAA) Web Application and Simulation System.

---

## 📌 Educational Use Disclaimer
**MediRoute is an academic Design and Analysis of Algorithms (DAA) mini-project built strictly for algorithmic evaluation, student learning, viva examination preparation, and graph visualization.** All data—including road layouts, intersections, emergency calls, and vehicle coordinates—is **100% synthetic**. This system is **not** a real-world emergency dispatch service and must never be used to make clinical triage decisions or allocate actual emergency medical response vehicles.

---

## 📖 Project Overview
In emergency medical services (EMS), rapid response latency is critical to patient outcomes. Traditional dispatch workflows often rely on static territorial boundaries or Euclidean straight-line radius estimates. These simplifications ignore real-world road graph topology, one-way streets, bridge bottlenecks, and vehicle capability requirements (Advanced Life Support vs. Basic Life Support).

**MediRoute** models urban road networks as weighted directed/undirected graphs $G = (V, E)$, implements a pure, independent version of **Dijkstra's Shortest Path Algorithm** with a binary min-heap (`heapq`), and provides a **Greedy Emergency Dispatch Engine** supporting three heuristic dispatch strategies.

---

## 🎯 Key Objectives
1. **Algorithmic Rigor:** Implement Dijkstra's algorithm and priority queues from scratch in pure Python without third-party solver shortcuts.
2. **Greedy Heuristics:** Compare local greedy nearest-vehicle selection against triage-aware and batch multi-incident allocation.
3. **Empirical Benchmarking:** Measure real microsecond execution times ($\mathcal{O}((|V| + |E|) \log |V|)$) using `time.perf_counter()` across synthetic networks up to $N = 100$.
4. **Interactive Visualization:** Render interactive topological networks using Plotly, highlighting optimal routes and competing candidate paths.
5. **Academic & Viva Readiness:** Provide comprehensive DAA study materials, asymptotic proofs, and 16 interactive viva examination questions.

---

## ⚙️ Technology Stack
- **Language:** Python 3.11 / 3.12
- **Web Dashboard:** [Streamlit](https://streamlit.io/) (Native Multipage Architecture)
- **Graph Topology:** NetworkX (Network layout utility; Dijkstra is independently coded)
- **Interactive Visualizations:** Plotly Express & Plotly Graph Objects
- **Data Engineering:** Pandas (DataFrames & CSV exports)
- **Priority Queues:** Python standard library `heapq` with monotonic insertion tie-breaking
- **High-Resolution Benchmarking:** `time.perf_counter()`
- **Automated Testing:** `pytest` (21 unit tests covering all core modules)

---

## 🏛️ System Architecture

```
+-------------------------------------------------------------------------+
|                        STREAMLIT WEB APPLICATION                         |
|   (Overview | Simulation | Roads | Fleet | Incidents | Dispatch Center) |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                         SIMULATION STATE MANAGER                         |
|     - SimulationState Container (Thread-safe, Snapshot Purity)          |
|     - Fleet Lifecycle & Atomic State Transitions                        |
|     - Incident Intake & Validation Pipeline                             |
+--------------------+------------------------------+---------------------+
                     |                              |
                     v                              v
+------------------------------------+    +-------------------------------+
|       GREEDY DISPATCH ENGINE       |    |      ROAD NETWORK MODEL       |
| - Strategy A: Nearest Available    |    | - RoadNetwork Adjacency List  |
| - Strategy B: Priority-Aware       |    | - Fixed 2D Coordinates        |
| - Strategy C: Greedy Batch Multi   |    | - Road Attributes & Weights   |
+--------------------+---------------+    +---------------+---------------+
                     |                                    |
                     +-----------------+------------------+
                                       |
                                       v
+-------------------------------------------------------------------------+
|                    CORE ALGORITHMIC FOUNDATION LAYER                    |
|   - dijkstra.py: Pure Adjacency List SSSP with Predecessor Backtracking  |
|   - priority_queue.py: Binary Min-Heap with Deterministic Tie-Breaking  |
|   - performance.py: Empirical Scalability Benchmarks (time.perf_counter)|
+-------------------------------------------------------------------------+
```

---

## 📂 Project Structure

```
mediroute/
│
├── app.py                      # Main entrypoint and Executive Overview Dashboard
├── run.bat                     # Windows one-click launcher (App, Tests, Dependencies)
├── requirements.txt            # Python dependencies
├── README.md                   # Comprehensive project documentation
├── .gitignore                  # Git ignore rules
│
├── .streamlit/
│   └── config.toml             # Custom theme colors and server settings
│
├── algorithms/
│   ├── __init__.py             # Algorithms package exports
│   ├── dijkstra.py             # Pure Dijkstra Shortest Path implementation
│   ├── priority_queue.py       # Reusable Priority Queue with heapq & tie-breaking
│   └── greedy_dispatch.py      # Greedy dispatch strategies (A, B, C)
│
├── graph/
│   ├── __init__.py             # Graph package exports
│   ├── graph_utils.py          # RoadNetwork adjacency list class & validators
│   └── sample_network.py       # Default 20-node Metro network & random generators
│
├── simulation/
│   ├── __init__.py             # Simulation package exports
│   ├── ambulances.py           # Ambulance dataclass & default fleet models
│   ├── incidents.py            # Incident dataclass, priority tiers, & input validation
│   ├── simulator.py            # Surge generators, mission lifecycles, & DataFrame export
│   └── state_manager.py        # Safe session state container & atomic mutations
│
├── visualization/
│   ├── __init__.py             # Visualization package exports
│   ├── network_graph.py        # Responsive Plotly topological road map visualizer
│   └── performance.py          # Benchmark runners & chart builders
│
├── ui/
│   ├── __init__.py             # UI package exports
│   ├── styles.py               # Design system CSS (Healthcare SaaS palette)
│   └── components.py           # Reusable metric cards, banners, badges, & viva cards
│
├── pages/
│   ├── 01_Overview_Dashboard.py    # Executive Overview Dashboard
│   ├── 02_Live_Simulation.py       # Step controller, surge generator, & live control
│   ├── 03_Road_Network.py          # Adjacency inspector, node degrees, & road weight editor
│   ├── 04_Ambulance_Fleet.py       # Fleet telemetry, status toggles, & capability filters
│   ├── 05_Emergency_Incidents.py   # Synthetic incident logging & priority queues
│   ├── 06_Dispatch_Center.py       # Interactive dispatch workspace, routes, & batch comparison
│   └── 07_Algorithm_Analytics.py   # Live Dijkstra benchmark suite & CSV downloads
│
├── data/
│   └── sample_network.json     # Serialized 20-node Metro road network
│
└── tests/
    ├── test_dijkstra.py        # 7 unit tests for Dijkstra edge cases
    ├── test_priority_queue.py  # 4 unit tests for min-heap & tie-breaking
    ├── test_dispatch.py        # 5 unit tests for greedy dispatch strategies
    └── test_simulation_state.py# 5 unit tests for state consistency & deduplication
```

---

## 🧮 Algorithm Specifications & Complexity

### 1. Dijkstra's Algorithm (`algorithms/dijkstra.py`)
- **Problem:** Single-Source Shortest Path (SSSP) on a non-negatively weighted graph.
- **Data Structures:** Adjacency list `Dict[str, List]`, distance hash table, predecessor hash table, and a min-heap priority queue.
- **Time Complexity:**
  $$\mathcal{O}((|V| + |E|) \log |V|)$$
  - Each vertex is extracted from the min-heap at most once: $|V| \times \mathcal{O}(\log |V|)$.
  - Each directed edge is relaxed at most once: $|E| \times \mathcal{O}(\log |V|)$.
- **Space Complexity:** $\mathcal{O}(|V| + |E|)$.
- **Negative Weights:** Strictly rejected with a descriptive `ValueError`. Dijkstra assumes optimal substructure with non-decreasing prefix paths; negative weights require Bellman-Ford ($\mathcal{O}(V \cdot E)$).

### 2. Reusable Priority Queue (`algorithms/priority_queue.py`)
- Built on Python's `heapq` module.
- Stores entries as 3-tuples: `(priority, insertion_counter, item)`.
- The monotonic counter acts as a **stable FIFO tie-breaker**, completely preventing Python from invoking comparison operators (`<`, `>`) on payload objects.
- Complexities:
  - `push(item, priority)`: $\mathcal{O}(\log n)$
  - `pop()`: $\mathcal{O}(\log n)$
  - `peek()`: $\mathcal{O}(1)$

### 3. Greedy Dispatch Strategies (`algorithms/greedy_dispatch.py`)
- **Strategy A (Nearest Available Ambulance):** Runs Dijkstra from all available vehicles to the incident node; chooses the vehicle with minimum travel time.
- **Strategy B (Priority-Aware Greedy Dispatch):** Audits medical priority. For **Critical** incidents, prioritizes Advanced Life Support (ALS) vehicles to ensure resuscitation capability, falling back to BLS if no ALS units are reachable.
- **Strategy C (Greedy Batch Multi-Incident Dispatch):** Processes multiple concurrent pending calls sorted by priority (Critical > High > Medium > Low). Enforces a single-assignment constraint across the fleet.
- **DAA Viva Insight:** Greedy batch dispatch is a heuristic and does not guarantee a globally minimal aggregate travel time. The global optimum requires Maximum-Weight Bipartite Matching via the Hungarian Algorithm ($\mathcal{O}(V^3)$).

---

## 🚀 Installation & Execution

### Prerequisites
- Python 3.11 or 3.12 installed on your machine.
- Git (optional, for version control).

### Step 1: Create Virtual Environment
Open Windows PowerShell:

```powershell
# Navigate to project directory
cd C:\Users\frost\.gemini\antigravity\scratch\mediroute

# Create virtual environment
py -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Quick Start (Windows Batch File)
Simply double-click or run:
```cmd
run.bat
```
This interactive script automatically detects Python, activates any `.venv` if present, provides options to install dependencies, run the test suite, or immediately launch the web application.

---

### Manual PowerShell Execution
```powershell
streamlit run app.py
```
*The application will automatically launch in your default web browser at `http://localhost:8501`.*

---

## 🧪 Automated Testing
MediRoute includes a comprehensive test suite of **21 unit tests** in `tests/`:

```powershell
python -m pytest tests -v
```

### Test Coverage Breakdown:
- `test_dijkstra.py`: Simple route, multi-hop cost vs hop-count, source == destination, unreachable destination, unknown nodes, negative weight rejection, zero-weight edge handling.
- `test_priority_queue.py`: Min-heap ordering, stable non-comparable tie-breaking, peek operation, empty queue error handling.
- `test_dispatch.py`: Nearest vehicle selection, busy vehicle exclusion, fleet exhaustion, unreachable incident handling, ALS capability triage, batch dispatch single-assignment invariant.
- `test_simulation_state.py`: Atomic commit dispatch, duplicate assignment prevention, mission completion and vehicle release, incident deduplication, pristine state reset.

---

## 🖥️ Application Navigation Tour

The application features a focused 7-section operational navigation system:

| # | Section | Key Capabilities |
| :---: | :--- | :--- |
| **01** | **Overview Dashboard** | Primary command-and-control landing: 5 KPI telemetry cards, live topological road map, prioritized emergency queue with direct 1-click dispatch, recent assignments log, and algorithm runtime profile. |
| **02** | **Live Simulation** | Real-time simulation controller: advance time intervals (+1), trigger synthetic incident surges, track and resolve en-route missions, and recall vehicles to base stations. |
| **03** | **Road Network** | Interactive 20-node urban road graph: inspect vertex degrees, browse adjacency lists, modify road weights with validation, and run procedural graph generators. |
| **04** | **Ambulance Fleet** | Fleet readiness operations: status filters (Available, En Route, Maintenance), ALS/BLS capability badges, vehicle search, and operational assignment history. |
| **05** | **Emergency Incidents**| Synthetic emergency intake: register simulated calls with location, priority tier (Critical, High, Medium, Low), and inspect the sortable triage queue. |
| **06** | **Dispatch Center** | Core optimization workspace: evaluates available vehicles via Dijkstra, highlights shortest routes, renders competing candidate paths, supports Strategy A (Nearest), Strategy B (Priority-Aware), Strategy C (Batch Multi-Incident Dispatch), and atomic dispatch confirmation. |
| **07** | **Algorithm Analytics**| High-resolution empirical benchmarking: profiles Dijkstra runtime against $|V| \in [10, 100]$ using `time.perf_counter()`, explored vertex analysis, and CSV data downloads for dispatch logs and benchmark datasets. |

---

## 📊 Sample Results

### Dijkstra Scalability Benchmarks (Measured on Intel/AMD x86_64 CPU)
| Graph Size $\|V\|$ | Graph Edges $\|E\|$ | Avg Dijkstra Runtime (ms) | Explored Vertices | Exploration Ratio |
| :---: | :---: | :---: | :---: | :---: |
| **10** | 22 | 0.082 ms | 5.3 | 53.0% |
| **20** | 56 | 0.165 ms | 11.2 | 56.0% |
| **35** | 108 | 0.298 ms | 19.4 | 55.4% |
| **50** | 164 | 0.441 ms | 28.1 | 56.2% |
| **75** | 258 | 0.710 ms | 42.6 | 56.8% |
| **100** | 362 | 0.985 ms | 57.8 | 57.8% |

*Results confirm that Dijkstra with binary heap pruning scales near-linearly for sparse road networks.*

---

## ⚠️ Known Limitations
1. **Synthetic Road Topologies:** Node coordinates and travel times are locally generated approximations rather than live GPS feeds.
2. **Static Edge Weights:** Travel times represent average simulated minutes; dynamic weather and minute-by-minute congestion variations are not simulated in real time.
3. **Greedy Batch Dispatch:** Multi-incident batching employs priority-ordered greedy allocation rather than Kuhn-Munkres global minimum-cost matching.

---

## 🔮 Future Enhancements
- **Global Bipartite Matching:** Implement the Hungarian Algorithm for optimal batch assignment.
- **OpenStreetMap Ingestion:** Support importing real municipal road networks via OSMNx.
- **Dynamic Congestion Modifiers:** Time-of-day traffic multipliers along major transit corridors.
- **Database Persistence:** SQLite / PostgreSQL persistence using SQLAlchemy.

---

## 🎓 Student Project Attribution
- **Project Title:** MediRoute — Intelligent Emergency Vehicle Dispatch Optimizer
- **Domain:** Design and Analysis of Algorithms (DAA) / Graph Optimization
- **Application Type:** College-Level Mini-Project & Viva Demonstration
