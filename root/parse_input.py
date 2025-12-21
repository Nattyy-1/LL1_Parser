from create_parse_table import create_parse_table
from anytree import Node, RenderTree, PreOrderIter

def parse_input(grammar, input_str):
    parse_table = create_parse_table(grammar)

    input_buffer = input_str.split()
    input_buffer.append('$')

    stack = ['$']
    steps = []

    start_symbol = grammar[0].split("->")[0].strip()
    stack.append(start_symbol)

    tree = Node(start_symbol)

    look_ahead = input_buffer[0]
    index_ptr = 0

    while stack:
        top = stack[-1]

        if top == look_ahead:
            steps.append({
                'stack': stack.copy(),
                'input': input_buffer.copy(),
                'lookahead_index': index_ptr,
                'action': 'match',
                'production': None
            })
            
            stack.pop()
            if top != '$':
                index_ptr += 1
                look_ahead = input_buffer[index_ptr]

        else:
            entry = parse_table[top][look_ahead]

            if entry is not None:
                steps.append({
                    'stack': stack.copy(),
                    'input': input_buffer.copy(),
                    'lookahead_index': index_ptr,
                    'action': 'expand',
                    'production': entry
                })
                
                lhs, rhs = entry.split("->")
                lhs = lhs.strip()
                rhs = rhs.strip()
                rhs = rhs.split()

                parent_node = find_node_in_tree(tree, lhs)

                if 'e' in rhs:
                    Node('e', parent=parent_node)
                    stack.pop()
                else:
                    rhs.reverse()
                    stack.pop()
                    for terminal in rhs:
                        stack.append(terminal)

                    rhs.reverse()
                    for terminal in rhs:
                        Node(terminal, parent=parent_node)

            else:
                return None, steps
    
    steps.append({
        'stack': stack.copy(),
        'input': input_buffer.copy(),
        'lookahead_index': index_ptr,
        'action': 'match',
        'production': None
    })
    
    return tree, steps


def find_node_in_tree(tree, symbol):
    for node in PreOrderIter(tree):
        if node.name == symbol and not node.children:
            return node
    return None
