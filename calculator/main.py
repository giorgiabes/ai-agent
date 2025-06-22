import sys
from pkg.calculator import Calculator
from pkg.render import render


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <expression>")
        return

    expression = sys.argv[1]
    calculator = Calculator()

    try:
        result = calculator.evaluate(expression)
        print(render(expression, result))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
