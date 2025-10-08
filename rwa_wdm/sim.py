"""RWA simulator main function

"""

# [1] https://la.mathworks.com/matlabcentral/fileexchange/4797-wdm-network-blocking-computation-toolbox

import logging
from timeit import default_timer  # https://stackoverflow.com/a/25823885/3798300
from typing import Callable
from argparse import Namespace


import numpy as np

# normal package-relative import (works when running as a module)
from .io import write_bp_to_disk, write_it_to_disk, plot_bp
from .net import Network


__all__ = (
    'get_net_instance_from_args',
    'get_rwa_algorithm_from_args',
    'simulator'
)

logger = logging.getLogger(__name__)


def get_net_instance_from_args(topname: str, numch: int) -> Network:
    """Instantiates a Network object from CLI string identifiers

    This is useful because rwa_wdm supports multiple network topology
    implementations, so this function acts like the instance is created
    directly.

    Args:
        topname: short identifier for the network topology
        numch: number of wavelength channels per network link

    Returns:
        Network: network topology instance

    Raises:
        ValueError: if `topname` is not a valid network identifier

    """
    if topname == 'nsf':
        from .net import NationalScienceFoundation
        return NationalScienceFoundation(numch)
    elif topname == 'clara':
        from .net import CooperacionLatinoAmericana
        return CooperacionLatinoAmericana(numch)
    elif topname == 'janet':
        from .net import JointAcademicNetwork
        return JointAcademicNetwork(numch)
    elif topname == 'rnp':
        from .net import RedeNacionalPesquisa
        return RedeNacionalPesquisa(numch)
    elif topname == 'pdf':
        from .net import MyTopology
        return MyTopology(numch)
    elif topname == 'auxgraph_demo_net':
        from .net import auxgraph_demo_net
        return auxgraph_demo_net(numch)
    else:
        raise ValueError('No network named "%s"' % topname)


def get_rwa_algorithm_from_args(r_alg: str, wa_alg: str, rwa_alg: str,
                                ga_popsize: int, ga_ngen: int,
                                ga_xrate: float, ga_mrate: float,
                                ) -> Callable:
    """Defines the main function to perform RWA from CLI string args

    Args:
        r_alg: identifier for a sole routing algorithm
        wa_alg: identifier for a sole wavelength assignment algorithm
        rwa_alg: identifier for a routine that performs RWA as one
        ga_popsize: population size for the GA-RWA procedure
        ga_ngen: number of generations for the GA-RWA procedure
        ga_xrate: crossover rate for the GA-RWA procedure
        ga_mrate: mutation rate for the GA-RWA procedure

    Returns:
        callable: a function that combines a routing algorithm and a
            wavelength assignment algorithm if those are provided
            separately, or an all-in-one RWA procedure

    Raises:
        ValueError: if neither `rwa_alg` nor both `r_alg` and `wa_alg`
            are provided

    """

    if r_alg is not None and wa_alg is not None:
        if r_alg == 'dijkstra':
            if wa_alg == 'vertex-coloring':
                from .rwa import dijkstra_vertex_coloring
                return dijkstra_vertex_coloring
            elif wa_alg == 'first-fit':
                from .rwa import dijkstra_first_fit
                return dijkstra_first_fit
            elif wa_alg == 'random-fit':
                from .rwa import dijkstra_random_fit
                return dijkstra_random_fit
            else:
                raise ValueError('Unknown wavelength assignment '
                                 'algorithm "%s"' % wa_alg)
        elif r_alg == 'yen':
            if wa_alg == 'vertex-coloring':
                from .rwa import yen_vertex_coloring
                return yen_vertex_coloring
            elif wa_alg == 'first-fit':
                from .rwa import yen_first_fit
                return yen_first_fit
            elif wa_alg == 'random-fit':
                from .rwa import yen_random_fit
                return yen_random_fit
            else:
                raise ValueError('Unknown wavelength assignment '
                                 'algorithm "%s"' % wa_alg)
        else:
            raise ValueError('Unknown routing algorithm "%s"' % r_alg)
    elif rwa_alg is not None:
        if rwa_alg == 'genetic-algorithm':
            from .rwa import genetic_algorithm
            return genetic_algorithm(ga_popsize, ga_ngen, ga_xrate, ga_mrate)
        else:
            raise ValueError('Unknown RWA algorithm "%s"' % rwa_alg)
    else:
        raise ValueError('RWA algorithm not specified')


def simulator(args: Namespace) -> None:
    """Main RWA simulation routine over WDM networks

    The loop levels of the simulator iterate over the number of repetitions,
    (simulations), the number of Erlangs (load), and the number of connection
    requests (calls) to be either allocated on the network or blocked if no
    resources happen to be available.

    Args:
        args: set of arguments provided via CLI to argparse module

    """
    debug_counter = 5 #dijkstra debug counter
    # print header for pretty stdout console logging
    print('Load:   ', end='')
    for i in range(1, args.load + 1):
        print('%4d' % i, end=' ')
    print()

    time_per_simulation = []
    for simulation in range(args.num_sim):
        sim_time = default_timer()
        net = get_net_instance_from_args(args.topology, args.channels)

        # Configure dijkstra debug logger to a per-simulation file if
        # requested. We do this here so the logger doesn't intermingle with
        # simulator's interactive stdout prints.
        dij_logger_handler = None
        if getattr(args, 'debug_dijkstra', False):
            import logging
            from pathlib import Path
            dij_log = logging.getLogger('rwa_dijkstra_debug')
            dij_log.setLevel(logging.DEBUG)
            # ensure results dir exists
            Path(getattr(args, 'result_dir', '.')).mkdir(parents=True, exist_ok=True)
            logfile = Path(getattr(args, 'result_dir', '.')) / f'dijkstra_debug.log'
            dij_logger_handler = logging.FileHandler(logfile, mode='w')
            dij_logger_handler.setLevel(logging.DEBUG)
            dij_logger_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            dij_log.addHandler(dij_logger_handler)

        # Debug: if args has attribute `debug` truthy, print adjacency matrix
        if getattr(args, 'debug_adjacency', False):
            try:
                import numpy as _np
                print('\n[debug] adjacency dtype:', net.a.dtype)
                # print matrix with integer formatting when values are integral
                if _np.all(_np.mod(net.a, 1) == 0):
                    print('[debug] adjacency matrix (int):\n', net.a.astype(int))
                else:
                    print('[debug] adjacency matrix (float):\n', net.a)
            except Exception as _e:
                print('[debug] failed to print adjacency matrix:', _e)

        if getattr(args, 'plot_topo', False): #get attr默认false
            net.plot_topology() #plot net topology (optional)

        rwa = get_rwa_algorithm_from_args(
            args.r, args.w, args.rwa,
            getattr(args, 'pop_size', None),
            getattr(args, 'num_gen', None),
            getattr(args, 'cross_rate', None),
            getattr(args, 'mut_rate', None),
        )
        blocklist = []
        blocks_per_erlang = []

        # ascending loop through Erlangs
        for load in range(1, args.load + 1):
            blocks = 0
            for call in range(args.calls):
                print('\rBlocks: ', end='', flush=True)
                for b in blocklist:
                    print('%04d ' % b, end='', flush=True)
                print(' %04d' % call, end='')

                # discrete-slot sampling normalized to 250 Erlangs
                # "暴力归一化": 当 load >= 250 时视为最稠密情况——每个时隙都有到达（scale=1）
                # 否则按比例 scale = 250 / load 缩放 Exp(1) 连续采样并四舍五入到整数时隙
                # 原始连续 Poisson/Exponential 采样（保留为注释，便于回溯）：
                # until_next = -np.log(1 - np.random.rand()) / load
                # holding_time = -np.log(1 - np.random.rand())

                if load >= 250:
                    scale = 1.0
                else:
                    # load is at least 1 in loop; guard for safety
                    scale = 250.0 / float(load) if load != 0 else 250.0

                # draw exponential(1) continuous samples via inverse-transform
                # (keeps the original implementation style and is numerically
                # identical to np.random.exponential(1.0))
                until_next_cont = -np.log(1.0 - np.random.rand())
                #holding_time_cont = -np.log(1.0 - np.random.rand())

                # map to integer slots using scale; make sure at least 1 slot
                until_next = int(round(until_next_cont * scale))
                # holding_time = int(round(holding_time_cont * scale))
                holding_time = 10 #not considering update, then holding time is fixed to 10
                if until_next < 1:
                    until_next = 1
                # Call RWA algorithm, which returns a lightpath if successful
                # or None if no λ can be found available at the route's first
                # link
                # prefer passing debug flag when available
                debug_dij=getattr(args, 'debug_dijkstra', False)
                if debug_dij:
                    debug_counter -= 1
                    if debug_counter < 0:
                        lightpath = rwa(net, args.y, debug=False)
                    else:
                        lightpath = rwa(net, args.y, debug=debug_dij)
                else:
                    lightpath = rwa(net, args.y, debug=debug_dij)

                # If lightpath is non None, the first link between the source
                # node and one of its neighbours has a wavelength available,
                # and the RWA algorithm running at that node thinks it can
                # allocate on that λ. However, we still need to check whether
                # that same wavelength is available on the remaining links
                # along the path in order to reach the destination node. In
                # other words, despite the RWA was successful at the first
                # node, the connection can still be blocked on further links
                # in the future hops to come, nevertheless.
                if lightpath is not None:
                    # check if the color chosen at the first link is available
                    # on all remaining links of the route
                    for (i, j) in lightpath.links:
                        if not net.n[i][j][lightpath.w]:
                            lightpath = None
                            break

                # Check if λ was not available either at the first link from
                # the source or at any other further link along the route.
                # Otherwise, allocate resources on the network for the
                # lightpath.
                if lightpath is None:
                    blocks += 1
                else:
                    lightpath.holding_time = holding_time
                    net.t.add_lightpath(lightpath)
                    for (i, j) in lightpath.links:
                        net.n[i][j][lightpath.w] = 0  # lock channel
                        net.t[i][j][lightpath.w] = holding_time

                        # make it symmetric
                        net.n[j][i][lightpath.w] = net.n[i][j][lightpath.w]
                        net.t[j][i][lightpath.w] = net.t[i][j][lightpath.w]

                # FIXME The following two routines below are part of the same
                # one: decreasing the time network resources remain allocated
                # to connections, and removing finished connections from the
                # traffic matrix. This, however, should be a single routine
                # iterating over lightpaths links instead of all edges, so when
                # the time is up on all links of a lightpath, the lightpath
                # might be popped from the matrix's list. I guess the problem
                # is the random initialisation of the traffic matrix's holding
                # times during network object instantiation, but if this is
                # indeed the fact it needs some consistent testing.
                for lightpath in net.t.lightpaths:
                    if lightpath.holding_time > until_next:
                        lightpath.holding_time -= until_next
                    else:
                        # time's up: remove conn from traffic matrix's list
                        net.t.remove_lightpath_by_id(lightpath.id)

                # Update *all* channels that are still in use
                for edge in net.get_edges():
                    # support (i,j) or (i,j,weight)
                    if len(edge) == 2:
                        i, j = edge
                    else:
                        i, j = edge[0], edge[1]
                    for w in range(net.nchannels):
                        if net.t[i][j][w] > until_next:
                            net.t[i][j][w] -= until_next
                        else:
                            # time's up: free channel
                            net.t[i][j][w] = 0
                            if not net.n[i][j][w]:
                                net.n[i][j][w] = 1  # free channel

                        # make matrices symmetric
                        net.t[j][i][w] = net.t[i][j][w]
                        net.n[j][i][w] = net.n[j][i][w]

            blocklist.append(blocks)
            blocks_per_erlang.append(100.0 * blocks / args.calls)

        sim_time = default_timer() - sim_time
        time_per_simulation.append(sim_time)

        print('\rBlocks: ', end='', flush=True)
        for b in blocklist:
            print('%04d ' % b, end='', flush=True)
        print('\n%-7s ' % 'BP (%):', end='')
        print(' '.join(['%4.1f' % b for b in blocks_per_erlang]), end=' ')
        print('[sim %d: %.2f secs]' % (simulation + 1, sim_time))
        fbase = '%s_%dch' % (
            args.rwa if args.rwa is not None else '%s_%s' % (args.r, args.w),
            int(args.channels))

        #derniere 
        # fbase = '%s_%dch_%dreq_%s' % (
        #     args.rwa if args.rwa is not None else '%s_%s' % (args.r, args.w),
        #     args.channels, args.calls, net.name)

    write_bp_to_disk(args.result_dir, fbase + '.bp', blocks_per_erlang)

    write_it_to_disk(args.result_dir, fbase + '.it', time_per_simulation)

    # cleanup dij logger handler if it was configured
    if dij_logger_handler is not None:
        dij_log = __import__('logging').getLogger('rwa_dijkstra_debug')
        dij_log.removeHandler(dij_logger_handler)
        dij_logger_handler.close()

    if args.plot:
        plot_bp(args.result_dir)
    
