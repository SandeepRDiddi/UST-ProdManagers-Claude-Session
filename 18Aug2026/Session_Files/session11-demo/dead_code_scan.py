#!/usr/bin/env python3
"""
dead_code_scan.py -- a real static-analysis dead-code detector, not a simulation.

Parses Python file(s) with the ast module, finds every function/method DEFINED
in src/ files, finds every name CALLED anywhere across ALL given files (src/
and tests/), and reports which src/ functions are never called anywhere in
the scanned set. This is genuinely how tools like `vulture` work at a basic
level -- name-based reachability, not a full call graph.

Two real, honest limitations this session cares about:
  1. Scope matters: scanning one file vs. the whole repo changes the answer --
     send() looks dead scanning notification_service.py alone, but is called
     from tests/test_notification_service.py.
  2. Indirect calls are invisible: `send_fn = self._provider_send` then
     `send_fn(...)` calls _provider_send indirectly. Simple name-matching
     cannot see through that -- a real limitation of this class of tool.

Usage:
    python3 dead_code_scan.py src/notification_service.py                  # single file (naive)
    python3 dead_code_scan.py src/*.py tests/*.py                          # whole repo (better)
"""
import ast
import sys
import glob


def collect(paths):
    defined = {}   # name -> (file, lineno) -- only from src/ files, since that's what we're diagnosing
    called = set()

    for path in paths:
        with open(path) as f:
            source = f.read()
        tree = ast.parse(source, filename=path)

        class Visitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                if "/src/" in path.replace("\\", "/") or path.startswith("src/"):
                    defined[node.name] = (path, node.lineno)
                self.generic_visit(node)

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    called.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called.add(node.func.attr)
                self.generic_visit(node)

        Visitor().visit(tree)

    return defined, called


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 dead_code_scan.py <file1.py> [file2.py ...]")
        sys.exit(1)

    paths = []
    for arg in sys.argv[1:]:
        paths.extend(glob.glob(arg))

    defined, called = collect(paths)
    dunder_and_entrypoints = {"__init__", "main"}
    dead = {
        name: loc for name, loc in defined.items()
        if name not in called and name not in dunder_and_entrypoints
    }

    print(f"Scanned {len(paths)} file(s): {', '.join(paths)}")
    print(f"src/ functions/methods defined: {len(defined)}")
    print(f"Names called anywhere in scanned set: {len(called)}\n")

    if dead:
        print(f"DEAD CODE -- {len(dead)} function(s) defined in src/ but never called anywhere scanned:")
        for name, (path, lineno) in sorted(dead.items(), key=lambda x: x[1][1]):
            print(f"  {path}:{lineno}  {name}()")
    else:
        print("No dead code found by name-based reachability.")

    print("\nCaveat: name-based reachability cannot see calls from outside the scanned files")
    print("(e.g. an external REST client), and cannot see indirect calls through a variable")
    print("(e.g. send_fn = self._provider_send, then send_fn(...)). Treat every result here")
    print("as a hypothesis to verify against the Functional and System context layers, not a verdict.")


if __name__ == "__main__":
    main()
