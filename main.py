# Calculates the amount of moles in the specified chemical compound and weight.

import json
import re

periodic_table = json.load(open("periodic_table/PeriodicTableJSON.json"))


def get_processed_formula_mass(formula):
    """
    Takes in a fully pre-processed formula without any parentheses and iteratively obtains the number of moles using the periodic table. Returns the total number of moles.
    """
    total_mass = 0
    while len(formula) > 0:
        element = re.search(r".*?\d", formula)
        element = element.group(0)

        symbol, subscript = element[:-1], int(element[-1])

        # this is quite slow and cumbersome. A better way would be to put this into a database, which could be done for the final product.
        for elem in periodic_table["elements"]:
            if elem["symbol"] == symbol:
                total_mass += (subscript * elem["atomic_mass"])
                break

        startidx = formula.index(element)
        endidx = startidx + len(element)

        formula = formula[endidx:]

    return total_mass

def normalize_formula(formula):
    """
    Insert ones after elements where the subscript is omitted. Streamlines the process of parsing the formula. Returns a copy of :formula: with ones inserted in it.
    """
    previous_was_number = None
    previous_index = 0
    parts = []
    for idx, item in enumerate(formula):
        if previous_was_number == False and (str.isupper(item) or item in ["(", ")"]):
            part = formula[previous_index:idx]
            part += "1"
            parts.append(part)
            previous_index = idx

        if str.isdigit(item) == False and len(formula) == (idx + 1):
            part = formula[previous_index:] + "1"
            parts.append(part)
            # ensure that the last part of "capturing the rest of the equation" doesn't duplicate the last character.
            previous_index = idx + 1

        # the parenthesis checking ensures that numbers aren't added in front of an element that comes right after a parenthesis
        if str.isdigit(item) or item == "(":
            previous_was_number = True
        else:
            previous_was_number = False

    # no modifying was needed, return formula as is.
    if len(parts) == 0:
        return formula

    # ensure whole formula is captured if the last part of the formula did not need modifying
    parts.append(formula[previous_index:])
    # return modified formula
    return "".join(parts)

def get_formula_mass(formula):
    """
    Takes in a raw :formula:, normalizes and parses it, and calculates its formula mass. Returns the total formula mass.
    """

    # list of tuples containing the formula inside the parentheses, and the multiplier associated with it.
    parentheses = []

    form = normalize_formula(formula)

    # after this loop, "form" becomes the formula with all parentheses removed. The parentheses all reside in the parentheses list of tuples, which contains the formulas inside the parentheses and the multiplier associated with them.
    while True:
        p = re.search(r"\(.*\)\d", form)
        if p is None:
            break

        # get string of matched thing
        p = p.group(0)
        # remove whole parenthesis from form
        startidx = form.index(p)
        endidx = startidx + len(p)
        form = form[:startidx] + form[endidx:]

        # get multiplier and content, and add to parentheses list
        multiplier = int(p[-1])
        content = p[1:-2]
        parentheses.append((content, multiplier))

    formula_mass = 0
    formula_mass += get_processed_formula_mass(form)
    for f, mult in parentheses:
        formula_mass += (get_processed_formula_mass(f) * mult)

    return formula_mass

if __name__ == '__main__':


    print "Enter the mass of the substance (in grams) and chemical formula to determine the number of moles."
    print "You can enter 'q' instead to quit the program."

    while True:

        formula = raw_input("Chemical formula: ")
        if formula == 'q': break
        
        mass = raw_input("Mass (g): ")

        moles = float(mass) / get_formula_mass(formula)
        print moles, "mol"
