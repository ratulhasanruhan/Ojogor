from lark import Lark, Transformer, v_args

# Updated Bengali Grammar
bengali_grammar = """
start: statement+

statement: print_statement
         | assignment
         | if_else_statement
         | loop_statement
         | function_definition
         | function_call
         | return_statement

print_statement: "দেখাও" "(" expression ")"

assignment: variable "=" expression

if_else_statement: "যদি" "(" condition ")" "{" statement+ "}" ("অন্যথায়" "{" statement+ "}")?

loop_statement: "যতক্ষণ" "(" condition ")" "{" statement+ "}"

function_definition: "ফাংশন" variable "(" variable_list? ")" "{" statement+ "}"
function_call: variable "(" argument_list? ")"

return_statement: "রিটার্ন" expression

condition: expression comparison_op expression
comparison_op: "ছোট" | "বড়" | "সমান" | ">" | "<"

?expression: expression "+" term   -> add
           | expression "-" term   -> subtract
           | term

?term: term "/" factor -> divide
     | term "%" factor -> mod
     | term "//" factor -> floor_div
     | term "*" factor -> multiply
     | factor

?factor: NUMBER         -> number
       | STRING         -> string
       | variable       -> var
       | function_call  -> call
       | "(" expression ")"   
       | "[" expression "]"

variable: BENGALI_CNAME
variable_list: variable ("," variable)*
argument_list: expression ("," expression)*

STRING: /"[^"]*"/
BENGALI_CNAME: /[a-zA-Z_ঀ-৾][a-zA-Z0-9_ঀ-৾]*/  // Allow both English and Bengali characters
%import common.NUMBER
%import common.WS
%ignore WS
"""

# Transformer to execute actions based on grammar rules
class BengaliTransformer(Transformer):
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def visit(self, node):
        if node is None:
            return None
        if isinstance(node, int) or isinstance(node, str) or isinstance(node, float):
            return node  # Return the value directly if it's not a Tree object
        method_name = f'visit_{node.data}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{node.data} method")

    def print_statement(self, args):
        print(args[0])

    def assignment(self, args):
        var_name = args[0].children[0].value  # Extract variable name from Tree
        self.variables[var_name] = self.visit(args[1])  # Evaluate the expression and store the value

    def if_else_statement(self, args):
        condition = args[0]
        if_block = args[1]
        else_block = args[2] if len(args) > 2 else []

        if self.visit(condition):
            for statement in if_block.children:
                self.visit(statement)
        else:
            for statement in else_block.children:
                self.visit(statement)

    def loop_statement(self, args):
        condition_expr = args[0]
        while self.visit(condition_expr):  # Evaluate condition at the start of each iteration
            for statement in args[1].children:  # Execute the loop body
                self.visit(statement)
        # Re-evaluate the condition after the loop body (this ensures the condition is checked each time)
            condition_expr = args[0]


    def function_definition(self, args):
        function_name = args[0].children[0].value  # Extract function name from Tree
        parameters = [param.children[0].value for param in args[1].children] if len(args) > 1 else []
        body = args[2]
        self.functions[function_name] = (parameters, body)

    def function_call(self, args):
        function_name = args[0].children[0].value  # Extract function name from Tree
        arguments = args[1] if len(args) > 1 else []

        if function_name in self.functions:
            parameters, body = self.functions[function_name]
            local_variables = dict(zip(parameters, arguments))
            original_variables = self.variables.copy()
            self.variables.update(local_variables)

            return_value = None
            for statement in body.children:
                return_value = self.visit(statement)

            self.variables = original_variables
            return return_value
        else:
            raise Exception(f"Function '{function_name}' not found")

    def return_statement(self, args):
        return args[0]

    def condition(self, args):
        left = args[0]
        right = args[2]
        operator = args[1]

        if operator == "ছোট" or operator == "<":
            return left < right
        elif operator == "বড়" or operator == ">":
            return left > right
        elif operator == "সমান":
            return left == right

    def add(self, args):
        return args[0] + args[1]

    def subtract(self, args):
        return args[0] - args[1]
    
    def multiply(self, args):
        return args[0] * args[1]

    def divide(self, args):
        if args[1] != 0:
            return args[0] / args[1]
        else:
            raise ZeroDivisionError(" Cannot divide by Zero!")

    def mod(self, args):
        if args[1] != 0:
            return args[0] % args[1]
        else:
            raise ZeroDivisionError(" Cannot divide by Zero!")
    
    # rounds down the output
    def floor_div(self, args):
        if args[1] != 0:
            return args[0] // args[1]
        else:
            raise ZeroDivisionError(" Cannot divide by Zero!")


    def var(self, args):
        var_name = args[0].children[0].value  # Extract variable name from Tree
        if var_name in self.variables:
            return self.variables[var_name]
        else:
            raise Exception(f"Variable '{var_name}' not found")

    def number(self, args):
        return int(args[0])

    def string(self, args):
        return args[0][1:-1]  # Remove quotes


# Parse and execute code
def execute_bengali_code(code: str):
    try:
        parser = Lark(bengali_grammar, start='start', parser='lalr', transformer=BengaliTransformer())
        tree = parser.parse(code)
        return tree
    except Exception as e:
        print(f"ভুল: {str(e)}")  # Print error message in Bengali


# Test Cases to verify everything is working properly
if __name__ == "__main__":
    # Function Definition and Call with Return Value
    code = """
    ফাংশন যোগ(x, y) {
        রিটার্ন(x + y)
    }
    z = যোগ(10, 20)
    দেখাও(z)
    """
    execute_bengali_code(code)

    # Variable Assignment and Error Handling
    code = """
    z = 50
    দেখাও(z)
    """
    execute_bengali_code(code)

    # Undefined Variable Error
    code = """
    দেখাও(x)
    """
    execute_bengali_code(code)

    # If-Else Statement
    code = """
    x = 15
    y = 10
    যদি(x > y) {
        দেখাও("x বড় y থেকে")
    } অন্যথায় {
        দেখাও("x ছোট y থেকে")
    }
    """
    execute_bengali_code(code)

    # Loop Statement
    code = """
    x = 0
    যতক্ষণ(x < 5) {
        দেখাও(x)
        x = x + 1
    }
    """
    execute_bengali_code(code)