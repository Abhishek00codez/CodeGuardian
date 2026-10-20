import ast

def _calculate_complexity(node: ast.AST) -> int:
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler,
                              ast.With, ast.Assert, ast.ListComp, ast.SetComp,
                              ast.DictComp, ast.GeneratorExp)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
        elif hasattr(ast, 'Match') and isinstance(child, getattr(ast, 'MatchCase', tuple())):
            complexity += 1
    return complexity

def parse_code(source_code: str) -> dict:
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {
            "status": "error",
            "syntax_error": {
                "msg": e.msg,
                "lineno": e.lineno,
                "offset": e.offset,
                "text": e.text.strip() if e.text else ""
            }
        }

    classes = []
    functions = []
    calls = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "bases": [b.id for b in node.bases if isinstance(b, ast.Name)],
            })
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
            functions.append({
                "name": node.name,
                "args": args,
                "complexity": _calculate_complexity(node),
                "returns": ast.unparse(node.returns) if node.returns else None
            })
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)

    return {
        "status": "success",
        "ast_context": {
            "classes": classes,
            "functions": functions,
            "calls": list(calls),
        }
    }
