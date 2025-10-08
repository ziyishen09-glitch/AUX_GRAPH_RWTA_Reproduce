
````markdown
# Auxiliary Graph Based RWTA for QKD secured optical network(Reproduction)

```plaintext
Modification history:

stage 1: adapt the library to an RWTA algorithm
for QKD secured optical network


# Auxiliary Graph Based RWTA for QKD-secured optical network (Reproduction)

## Modification history (short)

```
stage 1: adapt the library to an RWTA algorithm for QKD-secured optical network

1. created parameters loading scripts (run_quick_sim)
2. added auxgraph_demo_net network topology
3. added weight to the adjacency matrix:
   - changed adjacency matrix dtype from bool to np.float32
   - added a third parameter in `get_edges` for auxgraph
   - adjusted matrix fill logic to store weights
   - updated some plotting strategies
4. added a debug helper for Dijkstra to make it easier to inspect correctness
5. adapted arrival/holding-time logic to match the paper's model (Poisson arrivals)
   - holding time and arrival-rate handling adapted for experiments
6. moved source/destination selection from static network attributes to per-request
   attributes (now set dynamically per request in `sim.py`/`rwa.py`)
7. added `load_min` and `load_step` attributes in `io` to allow experiments over
   specific load ranges
```

> This repository continues development from the project documented in
> `README_aux_graph.txt` (kept in the repo). The remainder of this README
> contains the standard documentation for the simulator.


## RWA Simulator over WDM Optical Networks

This repository contains a simulator for the routing and wavelength assignment
(RWA) problem over wavelength-division multiplexing (WDM) optical networks. The
simulator supports static traffic (SLE — static lightpath establishment) and
implements common routing and wavelength-assignment strategies.

Documentation: https://rwa-wdm.readthedocs.io/en/latest/index.html

Implemented algorithms

- Routing
  - Dijkstra's algorithm
  - Yen's algorithm (K-shortest paths)
- Wavelength assignment
  - First-fit
  - Random-fit
  - Vertex coloring
- RWA frameworks
  - General objective function
  - Genetic algorithm (experimental)

Traffic model

Traffic is modelled using exponential distributions for inter-arrival and
holding times (Poisson process). The implementation is adapted from a Matlab
toolbox by Przemyslaw Pawelcza:
https://la.mathworks.com/matlabcentral/fileexchange/4797-wdm-network-blocking-computation-toolbox


## Installation

Install from PyPI:

```bash
pip install rwa-wdm
```

Or install from source:

```bash
git clone https://github.com/cassiobatista/rwa-wdm-sim.git
cd rwa-wdm-sim/
python setup.py install --skip-build
```


## Usage

Run from the command line as a module:

```bash
python -m rwa_wdm -t rnp -c 8 -r dijkstra -w first-fit -d /tmp/results -p
```

![Installation and dummy simulation](./docs/sim.gif)

Or use the library programmatically:

```python
from rwa_wdm import simulator
# TODO: add example usage
```


## Requirements

If you are working from source (not using pip/installed package), install the
dependencies manually. We recommend using Anaconda:

```bash
conda create --name rwa python=3.8 argcomplete networkx numpy matplotlib
conda activate rwa
```

<!--
Note: the original modification history and notes are retained in
`README_aux_graph.txt`.
-->


```python
