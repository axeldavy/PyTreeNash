
import copy
import numpy as np
from itertools import product


class Tree(object): 
    """
    Non-oriented tree built from a graph description
    """
    def __init__(self, links_list):
        # links_list[i] = list of i neighbors
        # We choose node 0 to be the root. There may be better choices
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
        # check everyone has connections
        for i in range(n):
            assert(len(links[i]) > 0)
        # check now it is a tree by checking number of connections
        num_conn = sum([len(links[node]) for node in range(n)])
        assert (num_conn % 2 == 0) # this is granted by first step
        assert (num_conn / 2 == n - 1)
        
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
        self.depths = depth
        
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

def merge_building_configs(building_configs_nodes):
    res = []
    nodes = len(building_configs_nodes)
    num_child_configs = [len(configs) for configs in building_configs_nodes]
    for combination in product(*[range(num_child_configs[n]) for n in range(nodes)]):
        merged = [-1 for i in building_configs_nodes[0][combination[0]]]
        for c_i in range(nodes):
            c_comb_num = combination[c_i]
            sub_config = building_configs_nodes[c_i][c_comb_num]
            old_merged = merged
            merged = [ max(a,b) for (a,b) in zip(old_merged, sub_config)]
        res.append(merged)
    return merged

class TreeNashBase(object):
    def __init__(self, tree):
        self.tree = tree;
        self.T_mats = [[] for i in range(len(tree.nodes))]
        self.U_lists = [[] for i in range(len(tree.nodes))]

    def downstream_pass(self):
        self.T_mats = [[] for i in self.tree.bottom_to_top]
        self.U_lists = [[] for i in self.tree.bottom_to_top]
        self.nactions = [[] for i in self.tree.bottom_to_top]
        self.nparentactions = [[] for i in self.tree.bottom_to_top]
        for i in self.tree.bottom_to_top:
            parents = self.tree.links_bottom_top[i];
            children =  self.tree.links_top_bottom[i];
            if (len(parents) == 0):
                nparentactions = 1
                nactions = self.T_mats[children[0]].shape[0]
            else:
                LReward = self.get_reward_mat(i, parents[0])
                nparentactions = LReward.shape[0]
                nactions = LReward.shape[1]
            for pa in range(nparentactions):
                self.U_lists[i].append([[] for na in range(nactions)])
            self.T_mats[i] = np.zeros((nparentactions, nactions))
            self.nactions[i] = nactions
            self.nparentactions[i] = nparentactions
        
        for node in self.tree.bottom_to_top:
            parents = self.tree.links_bottom_top[node];
            assert (len(parents) <= 1); # we are in a tree
            children =  self.tree.links_top_bottom[node];
            if (len(children) == 0): # leaf
                p = parents[0]; # we can assume we don't have an isolated node
                LReward = self.get_reward_mat(node, p)
                for i in range(self.nparentactions[node]):
                    self.T_mats[node][i, :] = (LReward[i, :] == max(LReward[i, :]))
                # LReward: rewards for node given parent action.
                # axis: p actions x node actions
                # -> T is argmax per line
            else:
                if (len(parents) == 0):
                    LRewards_p = np.zeros((1, self.nactions[node]), dtype = np.float)
                else:
                    p = parents[0];
                    LRewards_p = self.get_reward_mat(node, p)
                LRewards_c = [self.get_reward_mat(c, node) for c in children]
                for u in product(*[range(self.nactions[c]) for c in children]):
                    sum_LRewards_c_u = np.zeros(self.nactions[node], dtype = np.float)
                    for (cn, u_i) in zip(range(len(u)), u):
                        sum_LRewards_c_u += LRewards_c[cn][u_i, :]
                    LReward = LRewards_p + sum_LRewards_c_u[np.newaxis, :]
                    for i in range(self.nparentactions[node]):
                        max_indices = (LReward[i, :] == max(LReward[i, :]))
                        for k in max_indices.nonzero()[0]:
                            valid_choice = True
                            for (cn, u_i) in zip(range(len(u)), u):
                                if not(self.T_mats[children[cn]][k, u_i]):
                                    valid_choice = False
                                    break;
                            if valid_choice:
                                self.T_mats[node][i, k] = 1
                                self.U_lists[node][i][k].append(u)


    def upstream_pass_internal(self, node, node_indice, parent_indice):
        children =  self.tree.links_top_bottom[node];
        if (len(children) == 0):
            building_config = [-1 for i in self.tree.top_to_bottom]
            building_config[node] = node_indice
            return [building_config]
        building_configs = []
        children_combinations = self.U_lists[node][parent_indice][node_indice]
        assert (len(children_combinations) > 0)
        for combination in children_combinations:
            building_configs_children = []
            for cn in range(len(children)):
                c = children[cn]
                c_i = combination[cn] 
                building_configs_children.append(self.upstream_pass_internal(c, c_i, node_indice))
            for i in range(len(building_configs_children)):
                for j in range(len(building_configs_children[i])):
                    building_configs_children[i][j][node] = node_indice
            building_configs.append(merge_building_configs(building_configs_children))
        return building_configs
            

    def upstream_pass(self):
        self.configs = []
        self.building_config = [-1 for i in self.tree.top_to_bottom] 

        node_indices = self.T_mats[0].nonzero()[1]
        for i in node_indices:
            self.configs.append(self.upstream_pass_internal(0, i, 0))
        print self.configs

    def resolve(self):
        self.downstream_pass()
        self.upstream_pass()
        return


class MerchantProblem(TreeNashBase):
     def __init__(self, marchands_links, steps=20):
        tree = Tree(marchands_links)
        self.marchands_links = marchands_links
        TreeNashBase.__init__(self, tree)
        self.reward_mat = np.zeros((steps, steps), dtype = np.float)
        for i in range(steps):
            for j in range(steps):
                # area nearer to j in [0,1], ie area side j, delimited (i+j/2) / steps
                if i < j:
                    self.reward_mat[i,j] = 1 - ((i+j) / (2. * steps))
                elif i > j:
                    self.reward_mat[i,j] = ((i+j) / (2. * steps))
                else: # i = j is forbidden
                    self.reward_mat[i,j] = -100.

     def get_reward_mat(self, i, j):
         return self.reward_mat