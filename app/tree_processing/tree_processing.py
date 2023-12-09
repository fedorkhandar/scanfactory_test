"""
extract_patterns() function is the main function of the module. 
It creates a tree of urls, analyzes it, 
detects garbage urls and generates regexps for them.
"""
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class PosDesc:
    """Design a simple regexp by characters set from [0-9], [a-z], [A-Z] and other symbols. We can add a character, the regexp would be recalculated in __repr__()."""
    small_letters: bool = False
    capital_letters: bool = False
    digits: bool = False
    other_symbols: Set[str] = None
    
    def add(self, c):
        if c.isalpha():
            if c.islower():
                self.small_letters = True
            elif c.isupper():
                self.capital_letters = True
        elif c.isdigit():
            self.digits = True
        else:
            if self.other_symbols is None:
                self.other_symbols = set()
            self.other_symbols.add(c)
            
    def __repr__(self):
        res = ''
        if self.small_letters:
            res += 'a-z'
        if self.capital_letters:
            res += 'A-Z'
        if self.digits:
            res += '0-9'
        
        if self.other_symbols is not None:
            for x in self.other_symbols:
                res += x
    
        res = f"[{res}]"  
        return res

class TreeNode:
    """
    Tree for a set of urls (reversed view):
    
    EXAMPLE:
    Set of urls: {'aaa.xxx.com', 'bbb.xxx.com','yyy.com', 'ttt.yyy.com'}
    
    The tree:
    com
        [yyy]
            [ttt]
        xxx
            [aaa]
            [bbb]
    
    """
    text: str           # the text of the url's part, e.g. 'aaa' in 'xxx.aaa.com' 
    length: int         # length of the text, e.g. 3 for 'aaa' 
    children = []       # list of links to chilren
    parent: str         # route to parent node

    def __init__(self, *, text = None, children = None, parent = None):
        self.text = text
        self.length = len(text) if text is not None else 0
        self.children = children
        if parent is None:
            parent = ''
        self.parent = parent
        
    def add_child(self, parts:List[str]):
        """
        Adds a whole sequence of Nodes as a child
        
        parts: parts of an url (in reversed order)
        """
        
        start = self
        while len(parts) > 0:
            p = parts[-1]
            
            flag = False
            if start.children is not None:
                # START already has some children
                for c in start.children:
                    if c.text == p:
                        # if START already has the same child -- go down one level (START = c)
                        parts = parts[:-1]
                        start = c
                        flag = True
                        start.add_child(parts)
                        parts = []
                        
                if not flag:
                    # START has no the same children -- add new child and go to this child (START = child)
                    parent = start.parent
                    if start.text is not None and start.text != '': parent = ".".join([parent, start.text])
                    child = TreeNode(text=p, parent = parent)
                    parts = parts[:-1]
                    start.children.append(child)
                    start = child
                        
            else:
                # START has no children -- add new child and go to this child (START = child)
                parent = start.parent
                if start.text is not None and start.text != '': parent = ".".join([parent, start.text])
                child = TreeNode(text=p, parent = parent)
                parts = parts[:-1]
                start.children = [child]
                start = child       



def generate_regexp(examples: List[str])-> str:
    """designing the regexp for the group of strings"""
    
    # Define subgroups
    patterns = {}
    for e in examples:
        m = len(e)
        if m not in patterns:
            patterns[m] = []
        patterns[m].append(e)     
    
    # Define regexps for every subgroup
    result = []
    for num, subset in patterns.items():
        seq = []
        for i in range(num):
            pd = PosDesc()
            for e in subset:
                pd.add(e[i])
            seq.append(pd)
        
        stack = []
        for c in seq:
            if len(stack) == 0:
                stack.append([c, 1])
            else:
                if stack[-1][0] == c:
                    stack[-1][1] += 1
                else:
                    stack.append([c, 1])
        
        res = ''
        for s in stack:
            if s[1] == 1:
                res += str(s[0])
            else:
                res += f"{str(s[0])}{{{s[1]}}}"
        result.append(res)

    return result


def analyze_group(group: List[TreeNode])-> Dict[int, int]:
    """
    Detect subgroups of a group of nodes, that are:
        1) every node in the subgroup has no descendants (every node is a leaf)
        2) subgroup size > 1
    """
    has_children = False
    sizes = {}
    for node in group:
        if node.length not in sizes:
            sizes[node.length] = 0
        sizes[node.length] += 1
        if node.children is not None and len(node.children)>0:
            has_children = True
            
    subgroups = {}
    for s, num in sizes.items():
        if num !=1 and not has_children:
            subgroups[s] = num
    
    return subgroups

def print_tree(root_node, indent=4)-> None:
    """
    Print a tree.
    """
    if root_node.text is not None:
        print("    "*indent, f"{root_node.text} [{root_node.length}]")
    if root_node.children is not None and len(root_node.children) > 0:
        for c in root_node.children:
            if c is not None:
                print_tree(c, indent+1)


def analyze_tree(root_node: TreeNode) -> List[str]:
    """ tree traversal 
    Analyze every group of children:
    Define patterns if a group is garbage
    """
    queue = [root_node]
    result = []
    while len(queue)> 0:
        x = queue.pop(0)
        if x is not None:
            if x.children is not None and len(x.children)>0:
                
                #check if children are leaves
                # TODO: REFACTOR: garbage_subsets() and generate_regexp() do the same calculation sizes for subgroups
                garbage_subsets = analyze_group(x.children)
                if len(garbage_subsets)>0:
                    # construct patterns: regexp + self text + parent path 
                    parent_part = '.'.join(x.parent.split('.')[::-1][:-1])
                    self_part = x.text
                    regexp_part = generate_regexp([z.text for z in x.children])
                    for t in regexp_part:
                        result.append(f"{t}.{self_part}.{parent_part}")
                        
                for c in x.children:
                    queue.append(c)
    return result


def extract_patterns(urls: List[str])-> List[str]:  
    """create the tree and generate patterns" """
    
    # create the tree by urls
    root = TreeNode()
    
    for url in urls:
        url_parts = url.split('.')
        root.add_child(url_parts)
    
    # analyze created tree
    patterns = analyze_tree(root)
    
    return patterns