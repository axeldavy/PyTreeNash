
from treenash import Tree

if __name__ == "__main__":
    tree = Tree([[1,2],[0],[]])
    print tree.nodes
    print tree.links
    print tree.top_to_bottom
    print tree.bottom_to_top
    print tree.links_top_bottom
    print tree.links_bottom_top
