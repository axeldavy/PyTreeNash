
from treenash import Tree, MerchantProblem

if __name__ == "__main__":
    """
    tree = Tree([[1,2],[0],[]])
    print tree.nodes
    print tree.links
    print tree.top_to_bottom
    print tree.bottom_to_top
    print tree.links_top_bottom
    print tree.links_bottom_top
    """
    """
    problem with a graph. Should fail
    type A: 0, 1, 2
    type B: 0, 3
    type C: 1, 6
    type D: 3, 4
    type E: 3, 5
    """
    #links = [[1, 2, 3], [2, 6], [], [4, 5], [], [], []]
    #treenashMerchant = MerchantProblem(links, steps = 10)
    #treenashMerchant.resolve()
    """
    problem without a graph.
    type A: 0, 1
    type B: 0, 3
    type C: 1, 6
    type D: 3, 4
    type E: 3, 5
    type F: 0, 2
    """
    links = [[1, 2, 3], [6], [], [4, 5], [], [], []]
    treenashMerchant = MerchantProblem(links, steps = 10)
    treenashMerchant.resolve()
    """
    type A: 0, 1
    type B: 0, 2
    """
    #links = [[1,2],[],[]]
    #treenashMerchant = MerchantProblem(links, steps = 10)
    #treenashMerchant.resolve()
    """
    type A: 0, 1
    """
    #links = [[1],[]]
    #treenashMerchant = MerchantProblem(links, steps = 10)
    #treenashMerchant.resolve()
    
