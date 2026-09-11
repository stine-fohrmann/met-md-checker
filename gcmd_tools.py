from dataclasses import dataclass, field

@dataclass
class Node:
    '''Class for GCMD keyword paths'''
    
    children: dict = field(default_factory=dict)
    uuid: str | None = None
    path: tuple[str, ...] = ()  # corrcet path for the node

class GcmdTree:
    '''Class for GCMD keywords'''

    def __init__(self):
        self.root = Node()

    def add(self, levels: list[str], uuid: str | None = None):
        parts = tuple(l for l in levels if l)          # drop empty cells
        node = self.root
        for i, part in enumerate(parts):
            node = node.children.setdefault(
                part, Node(path=parts[: i + 1])
            )
        if uuid:
            node.uuid = uuid    # deepest level gets UUID
        return node
    
    def get_node(self, *path: str) -> Node | None:
        """Return the node for 'EARTH SCIENCE', 'AGRICULTURE', ... or None."""
        node = self.root
        for part in path:
            node = node.children.get(part)
            if node is None:
                return None
        return node    
    
    def contains(self, *keyword: str) -> bool:
        return self.get_node(*keyword) is not None


def make_gcmd_tree(filepath: str='data/sciencekeywords.csv') -> GcmdTree:
    '''Returns tree of GCMD keywords from CSV file'''
    import csv
    
    LEVEL_COLS = ["Category", "Topic", "Term", "Variable_Level_1", "Variable_Level_2", "Variable_Level_3", "Detailed_Variable"]
    tree = GcmdTree()

    with open(filepath, newline="", encoding="utf-8") as file:
        
        # skip first line
        next(file)
        reader = csv.DictReader(file)
        for row in reader:
            # print(row)
            levels = [row[c].strip() for c in LEVEL_COLS]
            # if levels == ["EARTH SCIENCE"] + [""] * 6:     # bare category root, skip if unwanted
                # continue
            tree.add(levels, uuid=row["UUID"].strip() or None)
    return tree

def keyword_str_to_list(keywords: str) -> list:
    '''Separate comma-separated keyword chains and >-separated keywords'''

    return [[kw.strip() for kw in kwstr.split('>')] for kwstr in keywords.split(',')]