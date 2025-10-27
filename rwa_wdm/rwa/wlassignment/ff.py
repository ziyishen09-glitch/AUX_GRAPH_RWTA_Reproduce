"""First-fit wavelength assignment strategy

"""
from typing import List, Optional

# FIXME https://mypy.readthedocs.io/en/latest/common_issues.html#import-cycles
from ...net import Network


def first_fit(net: Network, route: List[int], contains_virtual: bool = False, enable_new_ff: bool = False) -> Optional[List[int]]:
    """First-fit algorithm

    Select the wavelength with the lowest index available at the first link of
    the path, starting of course from the source node.

    Args:
        net: Network object
        route: path encoded as a sequence of router indices

    Returns:
        :obj:`list[int]` or ``None``: upon wavelength assignment success, return
            a list of wavelength indices to be used on the lightpath. The list
            contains one wavelength index per link in the route (for the
            per-link first-fit mode) or a single-element list when a single
            wavelength is used across the whole route. Returns ``None`` on
            failure.

    """
    w_list = []
    # Sanity: route must contain at least one hop
    if not route or len(route) < 2:
        return None
    
    if not enable_new_ff:
        for w in range(net.nchannels):
            ok = True
            # iterate pairwise over route to get links
            for idx in range(len(route) - 1):
                i, j = route[idx], route[idx + 1]
                if not net.n[i][j][w]:
                    ok = False
                    break
                else:
                    w_list.append(w)
            if ok:
                return w_list
        return None
    
    else:
        if contains_virtual:
            # in aux graph mode, we may have to assign different wavelengths
            # on different links
            for w in range(net.nchannels):
                ok = True
                for idx in range(len(route) - 1):
                    i, j = route[idx], route[idx + 1]
                    if not net.n[i][j][w]:
                        ok = False
                        break
                    else:
                        w_list.append(w)
                if ok:
                    return w_list
            return None
        
        else:
            for idx in range(len(route) - 1):
                i, j = route[idx], route[idx + 1]
                ok = False
                for w in range(net.nchannels):
                    if net.n[i][j][w]:
                        ok = True
                        w_list.append(w)
                        break
                if not ok:
                    return None
            return w_list