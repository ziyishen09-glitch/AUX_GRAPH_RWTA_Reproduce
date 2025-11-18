"""Small helper script to run the simulator with an embedded config.

This script builds an argparse.Namespace containing the parameters the
simulator expects, validates them using `validate_args`, then calls
`simulator(args)`. Edit DEFAULT_CONFIG to change parameters.
"""
from argparse import Namespace
import traceback
import sys

from rwa_wdm.BASE_NO_UPD import simulator as base_simulator
from rwa_wdm.FB_NO_UPD import simulator as fb_simulator
from rwa_wdm.util import validate_args

# Ensure logging is configured so simulator info messages (QKP logs) are visible.
import logging as _logging
if not _logging.getLogger().handlers:
    _logging.basicConfig(level=_logging.INFO, format='[%(levelname)s] %(message)s')

# Default quick-run config — edit as needed
DEFAULT_CONFIG = {
    'topology': 'auxgraph_aux_d2',  # 'nsf', 'clara', 'janet', 'rnp', 'pdf', 'auxgraph_aux_d2'
    'channels': 4,  #according to the paper
    'r': 'dijkstra',
    'w': 'first-fit',
    'rwa': None,
    'load': 190,
    'load_min': 30,
    'load_step': 20,
    'calls': 100000,
    'result_dir': './results',
    'num_sim': 1,
    'plot': True,
    'debug_adjacency':False,  #是否显示邻接矩阵
    'debug_dijkstra':False, #是否显示dijkstra调试信息
    'debug_lightpath':False, #是否显示lightpath调试信息
    'plot_topo':True,
    'runner': 'fb_passive_qkp',  # 'base_no_upd' or 'fb_no_upd' 
    'write_qkp_log': True,
    'write_qkp_usage_log': True,
     # or 'base_upd_rearrange' or 'base_upd_no_rearrange' or
     #'fb_upd_rearrange' or 'pb_upd_rearrange' or 'pb_modified'
     #or 'fb_passive_qkp'
     #  rearrange的意思是允许在update里面重新安排波长，no_rearrange是不允许
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
            debug_lightpath=cfg['debug_lightpath'],
            plot_topo=cfg['plot_topo'],
            runner=cfg['runner'],
            write_qkp_log=cfg.get('write_qkp_log', False),
            write_qkp_usage_log=cfg.get('write_qkp_usage_log', False),
        )

        # Validate and run
        validate_args(args)
        if args.runner == 'base_no_upd':
            simulator = base_simulator
        elif args.runner == 'fb_no_upd':
            simulator = fb_simulator
        elif args.runner == 'base_upd_no_rearrange':
            from rwa_wdm.BASE_UPD_NO_REARRANGE import simulator as base_updt_simulator
            simulator = base_updt_simulator
        elif args.runner == 'base_upd_rearrange':
            from rwa_wdm.BASE_UPD_REARRANGE import simulator as base_updt_original_simulator
            simulator = base_updt_original_simulator
        elif args.runner == 'fb_upd_rearrange':
            from rwa_wdm.FB_UPD_REARRANGE import simulator as fb_updt_simulator
            simulator = fb_updt_simulator
        elif args.runner == 'pb_upd_rearrange':
            from rwa_wdm.PB_UPD_REARRANGE import simulator as pb_updt_simulator    
            simulator = pb_updt_simulator
        elif args.runner == 'pb_modified':
            from rwa_wdm.PB_Modified import simulator as pb_Modified_simulator    
            simulator = pb_Modified_simulator
        elif args.runner == 'fb_passive_qkp':
            from rwa_wdm.FB_passive_QKP import simulator as fb_passive_simulator    
            simulator = fb_passive_simulator
        else:
            raise ValueError('Invalid runner specified: %s' % args.runner)
        simulator(args)
        return 0
    
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
 