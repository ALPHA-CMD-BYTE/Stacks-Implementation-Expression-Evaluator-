
import re
import sys


# --------------------------------------------------------------------------
# 1. Stack class (LIFO)
# --------------------------------------------------------------------------
class Stack:
    """A simple LIFO stack backed by a Python list."""

    def __init__(self):
        self._items = []

    def push(self, item):
        """Add an item to the top of the stack."""
        self._items.append(item)

    def pop(self):
        """Remove and return the top item. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        """Return the top item without removing it. Raises IndexError if empty."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def size(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack({self._items})"


# --------------------------------------------------------------------------
# 2. Expression parsing and evaluation
# --------------------------------------------------------------------------
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2}
TOKEN_RE = re.compile(r"\s*(\d+\.\d+|\d+|\.\d+|[+\-*/()])")


def tokenize(expression):
    """Split an expression string into numbers, operators and parentheses."""
    tokens, pos = [], 0
    expression = expression.rstrip()
    while pos < len(expression):
        match = TOKEN_RE.match(expression, pos)
        if not match:
            raise ValueError(f"invalid character '{expression[pos:].strip()[0]}'")
        tokens.append(match.group(1))
        pos = match.end()
    return tokens


def apply_operator(operators, values):
    """Pop one operator and two operands, compute, push the result."""
    op = operators.pop()
    if values.size() < 2:
        raise ValueError("malformed expression")
    right = values.pop()
    left = values.pop()
    if op == "+":
        values.push(left + right)
    elif op == "-":
        values.push(left - right)
    elif op == "*":
        values.push(left * right)
    elif op == "/":
        if right == 0:
            raise ZeroDivisionError("division by zero")
        values.push(left / right)


def evaluate_expression(expression):
    """
    Evaluate an infix expression using two stacks:
      - `values`    holds numbers (operands)
      - `operators` holds operators and '('
    Handles + - * /, parentheses, precedence, left-to-right associativity,
    decimals and unary minus (e.g. -5 + 3 or 2 * (-3)).
    """
    tokens = tokenize(expression)
    if not tokens:
        raise ValueError("empty expression")

    values, operators = Stack(), Stack()
    expect_operand = True          # True when a number, '(' or unary '-' may come next

    for token in tokens:
        if token[0].isdigit() or token[0] == ".":          # number
            if not expect_operand:
                raise ValueError("missing operator")
            values.push(float(token))
            expect_operand = False

        elif token == "(":
            if not expect_operand:
                raise ValueError("missing operator before '('")
            operators.push(token)

        elif token == ")":
            if expect_operand:
                raise ValueError("unexpected ')'")
            while not operators.is_empty() and operators.peek() != "(":
                apply_operator(operators, values)
            if operators.is_empty():
                raise ValueError("mismatched parentheses")
            operators.pop()                                # discard '('

        else:                                              # + - * /
            if expect_operand:
                if token == "-":                           # unary minus -> 0 - x
                    values.push(0.0)
                elif token == "+":                         # unary plus -> ignore
                    continue
                else:
                    raise ValueError(f"unexpected operator '{token}'")
            while (not operators.is_empty()
                   and operators.peek() != "("
                   and PRECEDENCE[operators.peek()] >= PRECEDENCE[token]
                   and not (expect_operand and token == "-")):
                apply_operator(operators, values)
            operators.push(token)
            expect_operand = True

    if expect_operand:
        raise ValueError("expression ends with an operator")

    while not operators.is_empty():
        if operators.peek() == "(":
            raise ValueError("mismatched parentheses")
        apply_operator(operators, values)

    if values.size() != 1:
        raise ValueError("malformed expression")
    return values.pop()


def format_result(value):
    """Show whole numbers without a decimal point (13 not 13.0)."""
    if value == int(value):
        return str(int(value))
    return str(round(value, 6)).rstrip("0").rstrip(".")


# --------------------------------------------------------------------------
# 3. File processing
# --------------------------------------------------------------------------
SEPARATOR_RE = re.compile(r"^\s*([-=_*~#])\1{2,}\s*$")   # e.g. -----


def process_file(input_path, output_path):
    """Read expressions, evaluate each, write results in the same layout."""
    with open(input_path, "r", encoding="utf-8") as infile:
        lines = infile.read().splitlines()

    output_lines = []
    for line in lines:
        if SEPARATOR_RE.match(line):                       # keep separators as-is
            output_lines.append(line.strip())
        elif line.strip() == "":                           # skip blank lines
            continue
        else:
            try:
                output_lines.append(format_result(evaluate_expression(line)))
            except ZeroDivisionError:
                output_lines.append("Error: division by zero")
            except (ValueError, IndexError) as err:
                output_lines.append(f"Error: {err}")

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(output_lines) + "\n")
    return output_lines


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.txt"
    try:
        results = process_file(input_path, output_path)
    except FileNotFoundError:
        print(f"Error: could not find '{input_path}'.")
        sys.exit(1)
    print(f"Processed '{input_path}' -> '{output_path}'")
    print("\n".join(results))


if __name__ == "__main__":
    main()
