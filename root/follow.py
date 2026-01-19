from first import first

def follow(grammar):
    FIRST = first(grammar)
    FOLLOW = {}

    for i in grammar:
        values = i.split("->")
        FOLLOW[values[0].strip()] = []

    start_symbol = grammar[0].split("->")[0].strip()
    FOLLOW[start_symbol].append('$')

    has_changed = True
    while has_changed:
        has_changed = False

        for i in grammar:
            left, right = i.split("->")
            left = left.strip()
            right = right.strip()

            for j in grammar:
                j_left, j_right = j.split("->")
                j_left = j_left.strip()
                j_right = j_right.strip()

                symbols = j_right.split()

                if left in symbols:
                    location = symbols.index(left)

                    if location + 1 < len(symbols):
                        next_symbol = symbols[location + 1]

                        if not next_symbol.isupper():
                            if next_symbol not in FOLLOW[left]:
                                FOLLOW[left].append(next_symbol)
                                has_changed = True

                        else:
                            for k in FIRST[next_symbol]:
                                if k != 'e' and k not in FOLLOW[left]:
                                    FOLLOW[left].append(k)
                                    has_changed = True

                            if 'e' in FIRST[next_symbol]:
                                k = location + 1
                                while k < len(symbols):
                                    sym = symbols[k]

                                    if not sym.isupper():
                                        if sym not in FOLLOW[left]:
                                            FOLLOW[left].append(sym)
                                            has_changed = True
                                        break
                                    else:
                                        for f in FIRST.get(sym, []):
                                            if f != 'e' and f not in FOLLOW[left]:
                                                FOLLOW[left].append(f)
                                                has_changed = True

                                        if 'e' not in FIRST.get(sym, []):
                                            break
                                        else:
                                            k += 1

                                if k >= len(symbols):
                                    for f in FOLLOW[j_left]:
                                        if f not in FOLLOW[left]:
                                            FOLLOW[left].append(f)
                                            has_changed = True

                    else:
                        if left != j_left:
                            for f in FOLLOW[j_left]:
                                if f not in FOLLOW[left]:
                                    FOLLOW[left].append(f)
                                    has_changed = True

    return FOLLOW
