"""Small helper script to run the simulator with an embedded config.

This script builds an argparse.Namespace containing the parameters the
simulator expects, validates them using `validate_args`, then calls
`simulator(args)`. Edit DEFAULT_CONFIG to change parameters.
"""
from argparse import Namespace
import traceback
import sys

from rwa_wdm.sim import simulator
from rwa_wdm.util import validate_args

# Default quick-run config — edit as needed
DEFAULT_CONFIG = {
    'topology': 'auxgraph_demo_net',
    'channels': 4,  #according to the paper
    'r': 'dijkstra',
    'w': 'first-fit',
    'rwa': None,
    'load': 250,
    'load_min':30,
    'load_step':20,
    'calls': 10000,
    'result_dir': './results',
    'num_sim': 10,
    'plot': True,
    'debug_adjacency':False,  #是否显示邻接矩阵
    'debug_dijkstra':False, #是否显示dijkstra调试信息
    'plot_topo':False
}


def main(config: dict | None = None) -> int:
    try:
        cfg = DEFAULT_CONFIG.copy()
        if config:
            cfg.update(config)

        # Construct Namespace with keys expected by simulator
        args = Namespace(
            topology=cfg['topology'],
            channels=cfg['channels'],
            r=cfg.get('r'),
            w=cfg.get('w'),
            rwa=cfg.get('rwa'),
            y=cfg.get('y'),
            load=cfg['load'],
            load_min=cfg['load_min'],
            load_step=cfg['load_step'],
            calls=cfg['calls'],
            result_dir=cfg['result_dir'],
            num_sim=cfg['num_sim'],
            plot=cfg['plot'],
            debug_adjacency=cfg['debug_adjacency'],
            debug_dijkstra=cfg['debug_dijkstra'],
            plot_topo=cfg['plot_topo']
        )

        # Validate and run
        validate_args(args)
        simulator(args)
        return 0
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
 