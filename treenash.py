
import copy


class Tree(object): 
    """
    Non-oriented tree built from a graph description
    """
    def __init__(self, links_list):
        # links_list[i] = list of i neighbors
        # We choose node 1 to be the root. There may be better choices
        n = len(links_list);
        self.nodes = range(n); # 0..n-1
        self.links = links_list
        links = copy.deepcopy(links_list);
        # first step: add links from child to parent (undirected graph)
        for i in range(n):
            for j in range(len(links[i])):
                child = links[i][j];
                assert (child != i);
                # check if we are already filled as parent
                has_parent = False;
                for p in range(len(links[child])):
                    if links[child][p] == i:
                        has_parent = True;
                        break;
                if not(has_parent):
                    links[child].append(i);
        # second step: change node ordering so that they are ordered by depth.
        depth = [-1 for i in range(n)]; #oui, il y a surement mieux pour initialiser
        to_propagate = [0]
        depth[0] = 0;
        explored = [0]
        while len(to_propagate) > 0:
            for i in to_propagate:
                for j in links[i]:
                    if not (j in explored):
                        depth[j] = depth[i] + 1
                        explored.append(j)
                        to_propagate.append(j)
                to_propagate.remove(i)
        explored.sort()
        assert (explored == range(n))
        depth_sorted = depth[:] #copy table
        depth_sorted.sort()
        depth_sorted_copy = depth_sorted[:]
        node_order = [-1 for i in range(n)]
        for i in range(n):
            depth_value = depth[i];
            order = depth_sorted.index(depth_value)
            depth_sorted[order] = -1; #two nodes should get different num
            node_order[i] = order;
        depth_sorted = depth_sorted_copy
        # TODO check now it is a tree by checking leaves are really leaves
        
        # third step: create two ordered tree for depth traversal and opposite
        self.top_to_bottom = node_order;
        node_order_reverse = node_order[:];
        node_order_reverse.reverse();
        self.bottom_to_top = node_order_reverse;
        links_top_bottom = copy.deepcopy(links);
        links_bottom_top = copy.deepcopy(links);
        for i in range(n):
            ref_order = node_order[i];
            t = range(len(links[i]));
            t.reverse() # to remove things safely
            for j in t:
                order = links[i][j];
                assert (order != ref_order);
                if order < ref_order:
                    links_top_bottom[i].pop(j)
                else :
                    links_bottom_top[i].pop(j)
        self.links_top_bottom = links_top_bottom;
        self.links_bottom_top = links_bottom_top;
                    
        
    # TODO: add iterators to go down the tree and go back from leaves to root.

class TreeNash(object):
    def __init__(self, tree):
        self.tree = tree