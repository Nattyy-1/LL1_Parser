"""
Module for receiving grammar input from the user.
"""

def receive_grammar():
    """Receives grammar input from the user.

    Returns:
        list (grammar): A list of strings representing the grammar.
    """
    
    number_of_productions = int(input("Enter the number of productions: "))
    grammar = []

    for i in range(number_of_productions):
        current_production = i + 1
        grammar.append(input(f"Enter production number {current_production}: "))

    return grammar
