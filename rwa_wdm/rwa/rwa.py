from typing import Callable, Union

from ..net import Lightpath, Network
from .routing import dijkstra, yen
from .wlassignment import vertex_coloring, first_fit, random_fit
from .ga import GeneticAlgorithm

__all__ = (
    'dijkstra_vertex_coloring',
    'dijkstra_first_fit',
    'yen_vertex_coloring',
    'yen_first_fit',
    'genetic_algorithm',
)


# genetic algorithm object (global)
# FIXME this looks bad. perhaps this whole script should be a class
ga: Union[GeneticAlgorithm, None] = None


def dijkstra_vertex_coloring(net: Network, k: int, debug: bool = False) -> Union[Lightpath, None]:
    """Dijkstra and vertex coloring combination as RWA algorithm

    Args:
        net: Network topology instance
        k: number of alternate paths (ignored)

    Returns:
        Lightpath: if successful, returns both route and wavelength index as a
            lightpath

    """
    route = dijkstra(net.a, net.s, net.d, debug=debug)
    wavelength = vertex_coloring(net, Lightpath(route, None))
    if wavelength is not None and wavelength < net.nchannels:
        return Lightpath(route, wavelength)
    return None

#temporarily just modified this, because only this is used
def dijkstra_first_fit(net: Network, s: int, d: int, k: int, debug: bool = False,
                       aux_graph_mode: bool = False, enable_new_ff: bool = False) -> Union[Lightpath, None]:
    """Dijkstra and first-fit combination as RWA algorithm

    Args:
        net: Network topology instance
        k: number of alternate paths (ignored)

    Returns:
        Lightpath: if successful, returns both route and wavelength index as a
            lightpath

    """
    route = dijkstra(net.a, s, d, debug=debug)
    # expand any auxiliary hops in the returned route to their stored
    # physical paths before wavelength assignment
    def _expand_aux_route(route):
        """Expand auxiliary/virtual hops into their physical subpaths.

        Always returns a 3-tuple: (route_nodes, contains_virtual_path, mapped_virtual_route)
        where `mapped_virtual_route` is a list of physical subpaths (each a list
        of nodes) corresponding to virtual hops found in the route.
        """
        contains_virtual_path = False
        # normalized return even for trivial routes
        if not route or len(route) < 2:
            return route, contains_virtual_path, []

        try:
            mapping = net.virtual_adjacency2physical_path()
        except Exception:
            mapping = {}

        expanded = []
        mapped_virtual_route = []
        for i in range(len(route) - 1):
            u, v = route[i], route[i + 1]
            key = (u, v)
            if key in mapping:
                contains_virtual_path = True
                phys = mapping[key]
                mapped_virtual_route.append(phys)
                # append the physical path, but avoid duplicating the
                # intermediate node when joining segments
                if expanded and expanded[-1] == phys[0]:
                    expanded.extend(phys[1:])
                else:
                    expanded.extend(phys)
            else:
                # no mapping: append the single hop (u) and let next
                # iteration append v (or append both here for final)
                if not expanded:
                    expanded.append(u)
                expanded.append(v)

        # ensure route is a proper node sequence; if expansion failed,
        # fall back to original route
        if len(expanded) == 0:
            return route, contains_virtual_path, mapped_virtual_route
        return expanded, contains_virtual_path, mapped_virtual_route
    
    # default values when not using auxiliary graph expansion
    contains_virtual_path = False
    mapped_virtual_route = []
    if aux_graph_mode:
        route, contains_virtual_path, mapped_virtual_route = _expand_aux_route(route)

    # call first_fit. It returns Optional[List[int]] where the list may
    # contain a single wavelength applied across the whole route or a
    # per-link wavelength assignment. The caller controls the new behavior
    # via enable_new_ff.
    w_list = first_fit(net, route, contains_virtual_path, enable_new_ff=enable_new_ff)

    if w_list is not None and len(w_list) > 0 and all(0 <= w < net.nchannels for w in w_list):
        lp = Lightpath(route, w_list[0])
        try:
            lp.w_list = list(w_list)
        except Exception:
            pass
        try:
            lp.contains_virtual = contains_virtual_path
            lp.mapped_virtual_route = mapped_virtual_route
        except Exception:
            # backwards compatibility: ignore if properties not supported
            pass
        return lp
    return None


def dijkstra_random_fit(net: Network, k: int, debug: bool = False) -> Union[Lightpath, None]:
    """Dijkstra and random-fit combination as RWA algorithm

    Args:
        net: Network topology instance
        k: number of alternate paths (ignored)

    Returns:
        Lightpath: if successful, returns both route and wavelength index as a
            lightpath

    """
    route = dijkstra(net.a, net.s, net.d, debug=debug)
    wavelength = random_fit(net, route)
    if wavelength is not None and wavelength < net.nchannels:
        return Lightpath(route, wavelength)
    return None


def yen_vertex_coloring(net: Network, k: int) -> Union[Lightpath, None]:
    """Yen and vertex coloring combination as RWA algorithm

    Args:
        net: Network topology instance
        k: number of alternate paths (ignored)

    Returns:
        Lightpath: if successful, returns both route and wavelength index as a
            lightpath

    """
    routes = yen(net.a, net.s, net.d, k)
    for route in routes:
        wavelength = vertex_coloring(net, Lightpath(route, None))
        if wavelength is not None and wavelength < net.nchannels:
            return Lightpath(route, wavelength)
    return None


def yen_first_fit(net: Network, k: int, enable_new_ff: bool = False) -> Union[Lightpath, None]:
    """Yen and first-fit combination as RWA algorithm

    Args:
        net: Network topology instance
        k: number of alternate paths (ignored)

    Returns:
        Lightpath: if successful, returns both route and wavelength index as a
            lightpath

    """
    routes = yen(net.a, net.s, net.d, k)
    for route in routes:
        w_list = first_fit(net, route, enable_new_ff=enable_new_ff)
        if w_list is not None and len(w_list) > 0 and all(0 <= w < net.nchannels for w in w_list):
            # keep backward compatibility: set Lightpath.w to first wavelength
            lp = Lightpath(route, w_list[0])
            try:
                lp.w_list = list(w_list)
            except Exception:
                pass
            return lp
    return None


def yen_random_fit(net: Network, k: int) -> Union[Lightpath, None]:
    """Yen and random-fit combination as RWA algorithm

    Args:
        net: Network topology instance
        k: number of alternate paths (ignored)

    Returns:
        Lightpath: if successful, returns both route and wavelength index as a
            lightpath

    """
    routes = yen(net.a, net.s, net.d, k)
    for route in routes:
        wavelength = random_fit(net, route)
        if wavelength is not None and wavelength < net.nchannels:
            return Lightpath(route, wavelength)
    return None


def genetic_algorithm_callback(net: Network, k: int) -> Union[Lightpath, None]:
    """Callback function to perform RWA via genetic algorithm

    Args:
        net: Network topology instance
        k: number of alternate paths (ignored)

    Returns:
        Lightpath: if successful, returns both route and wavelength index as a
            lightpath

    """
    route, wavelength = ga.run(net, k)
    if wavelength is not None and wavelength < net.nchannels:
        return Lightpath(route, wavelength)
    return None


def genetic_algorithm(pop_size: int, num_gen: int,
                      cross_rate: float, mut_rate: float) -> Callable:
    """Genetic algorithm as both routing and wavelength assignment algorithm

    This function just sets the parameters to the GA, so it acts as if it were
    a class constructor, setting a global variable as instance to the
    `GeneticAlgorithm` object in order to be further used by a callback
    function, which in turn returns the lightpath itself upon RWA success. This
    split into two classes is due to the fact that the class instance needs to
    be executed only once, while the callback may be called multiple times
    during simulation, namely one time per number of arriving call times number
    of load in Erlags (calls * loads)

    Note:
        Maybe this entire script should be a class and `ga` instance could be
        an attribute. Not sure I'm a good programmer.

    Args:
        pop_size: number of chromosomes in the population
        num_gen: number of generations towards evolve
        cross_rate: percentage of individuals to perform crossover
        mut_rate: percentage of individuals to undergo mutation

    Returns:
        callable: a callback function that calls the `GeneticAlgorithm` runner
            class, which finally and properly performs the RWA procedure

    """
    global ga
    ga = GeneticAlgorithm(pop_size, num_gen, cross_rate, mut_rate)
    return genetic_algorithm_callback
