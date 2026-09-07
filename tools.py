import json
import os
import ast
import operator
from datetime import datetime


NOTES_FILE = "memory/notes.json"


# ==========================
# CALCULATOR TOOL
# ==========================

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_calculate(expression):

    def evaluate(node):

        if isinstance(node, ast.Constant):
            return node.value

        if isinstance(node, ast.BinOp):
            operator_function = ALLOWED_OPERATORS.get(type(node.op))

            if operator_function is None:
                raise ValueError("Operation not allowed")

            return operator_function(
                evaluate(node.left),
                evaluate(node.right)
            )

        if isinstance(node, ast.UnaryOp):
            operator_function = ALLOWED_OPERATORS.get(type(node.op))

            if operator_function is None:
                raise ValueError("Operation not allowed")

            return operator_function(evaluate(node.operand))

        raise ValueError("Invalid expression")

    try:
        tree = ast.parse(expression, mode="eval")
        result = evaluate(tree.body)

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==========================
# TIME TOOL
# ==========================

def get_current_time():

    now = datetime.now()

    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%I:%M:%S %p"),
        "day": now.strftime("%A")
    }


# ==========================
# NOTES MEMORY TOOL
# ==========================

def load_notes():

    if not os.path.exists(NOTES_FILE):
        return []

    try:
        with open(NOTES_FILE, "r") as file:
            return json.load(file)

    except Exception:
        return []


def save_note(note):

    notes = load_notes()

    notes.append({
        "note": note,
        "created_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    })

    os.makedirs("memory", exist_ok=True)

    with open(NOTES_FILE, "w") as file:
        json.dump(notes, file, indent=4)

    return {
        "success": True,
        "message": "Note saved successfully",
        "note": note
    }


def get_notes():

    notes = load_notes()

    return {
        "notes": notes,
        "total_notes": len(notes)
    }