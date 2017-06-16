assignments = []


def cross(a, b):
    """
    Cross product of elements in A and elements in B.
    """
    return [s+t for s in a for t in b]


def unit_list():
    """
    :return: The units list as a 2d array [[box,box,box...], [box, box, box]]
    """
    row_units = [cross(r, cols) for r in rows]
    column_units = [cross(rows, c) for c in cols]
    square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
    diagonal1 = [a[0] + a[1] for a in zip(rows, cols)]
    diagonal2 = [a[0] + a[1] for a in zip(rows, cols[::-1])]
    diagonal_units = [diagonal1, diagonal2]

    return row_units + column_units + square_units + diagonal_units


cols = '123456789'
rows = 'ABCDEFGHI'
boxes = cross(rows, cols)
unit_list = unit_list()	
units = dict((s, [u for u in unit_list if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """
    Within each unit we search for boxes that hold the same digits and for which said digits are equal to the number 
    of boxes that hold them and eliminate said digits from the rest of boxes in the unit.
    :param values:  values(dict): The sudoku in dictionary form
    :return: Returns values 
    """
    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    # We create a 2d array that holds the amount of times each combination of digits appear in each unit if the amount
    # of times they appear is equal to the number of boxes that contain them
    twin_list = []
    for unit in unit_list:
        twins = dict()
        for box in unit:
            digits = values[box]
            if digits in twins:
                twins[digits] += 1
            else:
                twins[digits] = 1

        twin_list.append([digits for digits, times in twins.items() if times != 1 and times != 9 and len(digits) == times])

    # We check each unit and eliminate the digits from the twin boxes of each of their peers
    for unit, twins in zip(unit_list, twin_list):
        if len(twins) > 0:
            for box in unit:
                for digits in twins:
                    if values[box] != digits:
                        for digit in digits:
                            assign_value(values, box, values[box].replace(digit, ''))

    return values


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """
    Checks for solved boxes and eliminates their digit from its peers
    :param values:  values(dict): The sudoku in dictionary form
    :return: Returns values 
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values


def only_choice(values):
    """
    Checks each unit and if there there is any value that can only be assigned to one box it assigns it to said box
    :param values:  values(dict): The sudoku in dictionary form
    :return: Returns values 
    """
    for unit in unit_list:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    It tries to to resolve the sudoku by using eliminate, naked twins and only choice
    :param values:  values(dict): The sudoku in dictionary form
    :return: False if there is no solution and values if it finds a solution or there is no more improvement
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = naked_twins(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """
    Recursively tries to solve the solution by applying reduce_puzzle and branching over the possible values not 
    resolved by reduce_puzzle
    :param values:  values(dict): The sudoku in dictionary form
    :return: Returns false if there is no solution (reduce_puzzle returns false) and values if it finds the solution
    """
    values = reduce_puzzle(values)
    if values is False:
        return False
    if all(len(value) == 1 for value in values.values()):
        return values
    number, box = min((len(values[box]), box) for box in boxes if len(values[box]) > 1)

    for digit in values[box]:
        nValues = values.copy()
        assign_value(nValues, box, digit)
        finished = search(nValues)
        if finished:
            return finished


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)


    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
