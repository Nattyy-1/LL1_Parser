def first(grammar):
    FIRST = {}

    for i in grammar:
        values = i.split("->")
        FIRST[values[0].strip()] = []

    has_changed = True
    while has_changed:
        has_changed = False

        for i in grammar:
            left, right = i.split("->")
            right = right.strip()
            left = left.strip()

            symbols = right.split()
            expand_epsilon = True
            j = 0

            while j < len(symbols) and expand_epsilon:
                symbol = symbols[j]

                if not symbol.isupper():
                    if symbol not in FIRST[left]:
                        FIRST[left].append(symbol)
                        has_changed = True

                    expand_epsilon = False
                else:
                    for k in FIRST[symbol]:
                        if k != 'e' and k not in FIRST[left]:
                            FIRST[left].append(k)
                            has_changed = True

                    if 'e' in FIRST[symbol]:
                        expand_epsilon = True
                    else:
                        expand_epsilon = False

                j += 1

            if expand_epsilon and 'e' not in FIRST[left]:
                FIRST[left].append('e')
                has_changed = True

    return FIRST

