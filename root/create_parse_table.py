from first import first
from follow import follow

def create_parse_table(grammar):
    FIRST = first(grammar)
    FOLLOW = follow(grammar)

    row = []
    column = []
    for i in grammar:
        values = i.split("->")
        row.append(values[0].strip())

        symbols = values[1].split()
        for j in symbols:
            if not j.isupper() and j not in column and j != 'e':
                column.append(j.strip())

    LL1_table = {}
    for r in row:
        LL1_table[r] = {}
        for c in column:
            LL1_table[r][c] = None
        if '$' not in LL1_table[r]:
            LL1_table[r]['$'] = None

    def first_of_rhs(symbols):
        result = set()
        for sym in symbols:
            if not sym.isupper():
                result.add(sym)
                return result
            else:
                result.update(s for s in FIRST[sym] if s != 'e')
                if 'e' not in FIRST[sym]:
                    return result
        result.add('e')
        return result

    for non_terminal in row:
        for terminal in FIRST[non_terminal]:
            if terminal != 'e':
                for prod in grammar:
                    lhs, rhs = prod.split("->")
                    lhs = lhs.strip()
                    rhs_symbols = rhs.strip().split()

                    if lhs == non_terminal:
                        if terminal in first_of_rhs(rhs_symbols):
                            LL1_table[non_terminal][terminal] = prod
                            break

        if 'e' in FIRST[non_terminal]:
            for terminal in FOLLOW[non_terminal]:
                LL1_table[non_terminal][terminal] = f"{non_terminal} -> e"

    return LL1_table

