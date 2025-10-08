# RWA Simulator over WDM Optical Networks

This repo contains a simulator that covers the routing and
wavelength assignment (RWA) problem over wavelength-division multiplexing
(WDM)-based all-optical networks with static traffic (SLE, for static lightpath
establishment).

:pencil: Documentation: https://rwa-wdm.readthedocs.io/en/latest/index.html

The following algorithms are implemented:

- Routing     
    - Dijkstra's algorithm    
    - Yen's algorithm (also known as K-shortest path algorithm)    
- Wavelength Assignment     
    - First-fit algorithm    
    - Random-fit algorithm    
    - Vertex coloring algorithm    
- RWA as one    
   - General Objective Function    
   - Genetic algorithm (ours)    

The traffic is modelled according to exponential distrubutions of times
(namely, the time between consecutive call arrivals and the time a successfully
allocated call remains in the network occupying resources) that follow the
Poisson distribution. This model was ported from a [Matlab toolbox written by 
Przemyslaw Pawelcza](https://la.mathworks.com/matlabcentral/fileexchange/4797-wdm-network-blocking-computation-toolbox).


## Installation

Directly from PyPI via pip:

```bash
$ pip install rwa-wdm
```

Or, from source:

```bash
$ git clone htps://github.com/cassiobatista/rwa-wdm-sim.git
$ cd rwa-wdm-sim/
$ python setup.py install --skip-build
```


## Usage

As a module from CLI:

```bash
$ python -m rwa_wdm -t rnp -c 8 -r dijkstra -w first-fit -d /tmp/results -p
```

![Installation and dummy simulation](./docs/sim.gif)

Alternatively, as a lib:

```python
from rwa_wdm import simulator
# TBD
```


## Requirements

:warning: Manual installation of required packages is necessary only if you're
debugging the source without properly installing the package via either PyPI or
`setuptools`.

We recommend the use of [Anaconda](https://www.anaconda.com/):

```bash
$ conda create --name rwa python=3.8 argcomplete networkx numpy matplotlib
$ conda activate rwa
```
<!--
Note: the following block is the original modification history and notes
from `README_aux_graph.txt`. This repository continues development from that
project; the original file `README_aux_graph.txt` is retained in the repo.
-->

## Aux-graph modification history (from README_aux_graph.txt)

```plaintext
Modification history:

stage 1: adapt the library to an RWTA algorithm
for QKD secured optical network

1. created parameters loading scripts
  （run_quick_sim）

2. added auxgraph_demo_net network topo

3. added weight to the adjacency matrix
    to achieve this:
    changed the adjacency matrix data type
    from bool to np.float32;
    added a third parameter in get_edges
    for the auxgraph network;
    changed logics in matrix filling-in
    so that the weight can be stored;
    changed some plotting strategies;

4. added a debug function for the dijkstra
   convenient for inspecting if dijkstra is 
   working alright.
   As well helpful for auxgraph construction

5. no time-sliding window is used in this paper
   it means if a time slot is occupied, then
   find another time slot using first fit
   There are 4 wavelenghts for Qchs according 
   to the paper.
   According to this strategy and possion arrival-
   settings in the article (leave rate = 0.004/deta-t)
   holding time = 10 delta-t (temporarily not considering update),
   modified the possion arrival formula.
   
   (bugs remaining for below)
   Adaption for network initialzation, currently initalised 
   initial holding time to rand int 0-10.(To avoid uneven distribution)

6. originally, source and destination nodes are network attributes,
   and are static. Here, the network attribute s and d is abandoned,
   and changed to dynamic attribute attached to each request, so as 
   to stay in line with the paper(and the reality). 
```

> This repository continues development from the project documented above
> (see `README_aux_graph.txt` for the original file). The remainder of this
> README contains the standard documentation for the simulator.

````markdown
# RWA Simulator over WDM Optical Networks

This repo contains a simulator that covers the routing and
wavelength assignment (RWA) problem over wavelength-division multiplexing
(WDM)-based all-optical networks with static traffic (SLE, for static lightpath
establishment).
    acmid     = {3277126},
