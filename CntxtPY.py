# CntxtPY.py - Python codebase analyzer that generates comprehensive knowledge graphs optimized for LLM context windows

import os
import re
import sys
import json
import ast
import networkx as nx
from networkx.readwrite import json_graph
from typing import Dict, List, Set, Any


class PythonCodeKnowledgeGraph:
    def __init__(self, directory: str):
        """Initialize the knowledge graph generator.

        Args:
            directory: Root directory of the Python codebase.
        """
        self.directory = directory
        self.graph = nx.DiGraph()
        self.class_methods: Dict[str, Set[str]] = {}
        self.function_params: Dict[str, List[Dict[str, Any]]] = {}
        self.function_returns: Dict[str, str] = {}
        self.files_processed = 0
        self.total_files = 0
        self.dirs_processed = 0

        # Directories to ignore during analysis.
        self.ignored_directories = set([
            '__pycache__', 'venv', 'env', '.env', '.git', '.idea', '.vscode', 'build', 'dist',
            '.eggs', '.pytest_cache', '.mypy_cache', '.tox', '.cache', '.coverage', 'node_modules',
            'tests', 'docs', 'examples', 'data', 'migrations', 'scripts', 'static', 'media', 'logs',
        ])

        # Files to ignore during analysis.
        self.ignored_files = set([
            '.gitignore',
            '.env',
            'README.md',
            'LICENSE',
            'MANIFEST.in',
            'pyproject.toml',
            'setup.py',
            'setup.cfg',
        ])

        # For processing dependencies
        self.dependencies: Set[str] = set()

        # Counters for statistics
        self.total_classes = 0
        self.total_functions = 0
        self.total_imports = 0
        self.total_dependencies_count = 0
        self.total_modules = 0
        self.total_methods = 0
        self.total_decorators = 0

        # Track analyzed files to prevent circular dependencies.
        self.analyzed_files = set()

    def analyze_codebase(self):
        """Analyze the Python codebase to extract files, imports,
        classes, methods, functions, and their relationships."""
        # First pass to count total files
        print("\nCounting files...")
        for root, dirs, files in os.walk(self.directory):
            # Remove ignored directories from dirs in-place to prevent walking into them
            dirs[:] = [d for d in dirs if d not in self.ignored_directories]

            # Skip if current directory is in ignored directories
            if any(ignored in root.split(os.sep) for ignored in self.ignored_directories):
                continue
            self.total_files += sum(1 for f in files if f not in self.ignored_files and f.endswith(".py"))

        print(f"Found {self.total_files} Python files to process")
        print("\nProcessing files...")

        # Second pass to process files
        for root, dirs, files in os.walk(self.directory):
            # Remove ignored directories from dirs in-place to prevent walking into them
            dirs[:] = [d for d in dirs if d not in self.ignored_directories]

            # Skip if current directory is in ignored directories
            if any(ignored in root.split(os.sep) for ignored in self.ignored_directories):
                continue

            # Display current directory
            rel_path = os.path.relpath(root, self.directory)
            self.dirs_processed += 1
            print(f"\rProcessing directory [{self.dirs_processed}]: {rel_path}", end="")

            for file in files:
                if file in self.ignored_files:
                    continue
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self._process_file(file_path)
                elif file in ["requirements.txt", "Pipfile", "Pipfile.lock", "setup.py", "pyproject.toml"]:
                    file_path = os.path.join(root, file)
                    self._process_dependency_file(file_path)

        print(f"\n\nCompleted processing {self.files_processed} files across {self.dirs_processed} directories")

    def _process_file(self, file_path: str):
        """Process a Python file to detect imports, classes, methods, functions, and dependencies."""
        if file_path in self.analyzed_files:
            return

        try:
            self.files_processed += 1
            relative_path = os.path.relpath(file_path, self.directory)
            print(f"\rProcessing file [{self.files_processed}/{self.total_files}]: {relative_path}", end="", flush=True)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            file_node = f"File: {relative_path}"

            # Add to analyzed files set.
            self.analyzed_files.add(file_path)

            # Add file node if it doesn't exist.
            if not self.graph.has_node(file_node):
                self.graph.add_node(file_node, type="file", path=relative_path)

            # Parse the AST of the file.
            tree = ast.parse(content, filename=relative_path)

            # Process the AST nodes.
            self._process_ast_nodes(tree, file_node)

        except Exception as e:
            print(f"\nError processing {file_path}: {str(e)}", file=sys.stderr)

    def _process_ast_nodes(self, tree: ast.AST, file_node: str):
        """Process the AST nodes to extract imports, classes, functions, and their relationships."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self._process_import(node, file_node)
            elif isinstance(node, ast.ImportFrom):
                self._process_import_from(node, file_node)
            elif isinstance(node, ast.ClassDef):
                self._process_class(node, file_node)
            elif isinstance(node, ast.FunctionDef):
                self._process_function(node, file_node)
            elif isinstance(node, ast.AsyncFunctionDef):
                self._process_function(node, file_node, is_async=True)

    def _process_import(self, node: ast.Import, file_node: str):
        """Process 'import' statements."""
        for alias in node.names:
            module_name = alias.name
            asname = alias.asname or module_name
            module_node = f"Module: {module_name}"

            if not self.graph.has_node(module_node):
                self.graph.add_node(module_node, type="module", name=module_name)
                self.total_modules += 1

            self.graph.add_edge(file_node, module_node, relation="IMPORTS_MODULE")
            self.total_imports += 1

    def _process_import_from(self, node: ast.ImportFrom, file_node: str):
        """Process 'from ... import ...' statements."""
        module_name = node.module if node.module else ""
        level = node.level
        if level > 0:
            module_name = "." * level + module_name if module_name else "." * level
        module_node = f"Module: {module_name}"

        if not self.graph.has_node(module_node):
            self.graph.add_node(module_node, type="module", name=module_name)
            self.total_modules += 1

        for alias in node.names:
            name = alias.name
            asname = alias.asname or name
            entity_node = f"Entity: {module_name}.{name}"

            if not self.graph.has_node(entity_node):
                self.graph.add_node(entity_node, type="entity", name=name)

            self.graph.add_edge(file_node, entity_node, relation="IMPORTS_ENTITY")
            self.total_imports += 1

    def _process_class(self, node: ast.ClassDef, file_node: str):
        """Process class definitions."""
        class_name = node.name
        class_node = f"Class: {class_name} ({file_node})"

        if not self.graph.has_node(class_node):
            base_classes = [self._get_name(base) for base in node.bases]
            self.graph.add_node(
                class_node,
                type="class",
                name=class_name,
                bases=base_classes,
            )
            self.total_classes += 1

        self.graph.add_edge(file_node, class_node, relation="DEFINES_CLASS")

        # Process methods inside the class
        for body_item in node.body:
            if isinstance(body_item, ast.FunctionDef):
                self._process_method(body_item, class_node)
            elif isinstance(body_item, ast.AsyncFunctionDef):
                self._process_method(body_item, class_node, is_async=True)

    def _process_method(self, node: ast.FunctionDef, class_node: str, is_async: bool = False):
        """Process methods within a class."""
        method_name = node.name
        method_node = f"Method: {method_name} ({class_node})"

        decorators = [self._get_name(d) for d in node.decorator_list]
        if not self.graph.has_node(method_node):
            params = [arg.arg for arg in node.args.args]
            self.graph.add_node(
                method_node,
                type="method",
                name=method_name,
                parameters=params,
                is_async=is_async,
                decorators=decorators,
            )
            self.total_methods += 1
            if decorators:
                self.total_decorators += len(decorators)

        self.graph.add_edge(class_node, method_node, relation="HAS_METHOD")

        # Track class methods.
        if class_node not in self.class_methods:
            self.class_methods[class_node] = set()
        self.class_methods[class_node].add(method_name)

        # Track function parameters.
        self.function_params[method_node] = self._parse_parameters(node.args)

        # Process decorators
        for decorator in node.decorator_list:
            decorator_name = self._get_name(decorator)
            decorator_node = f"Decorator: {decorator_name}"
            if not self.graph.has_node(decorator_node):
                self.graph.add_node(decorator_node, type="decorator", name=decorator_name)
            self.graph.add_edge(method_node, decorator_node, relation="USES_DECORATOR")

    def _process_function(self, node: ast.FunctionDef, file_node: str, is_async: bool = False):
        """Process function definitions."""
        func_name = node.name
        func_node = f"Function: {func_name} ({file_node})"

        decorators = [self._get_name(d) for d in node.decorator_list]
        if not self.graph.has_node(func_node):
            params = [arg.arg for arg in node.args.args]
            self.graph.add_node(
                func_node,
                type="function",
                name=func_name,
                parameters=params,
                is_async=is_async,
                decorators=decorators,
            )
            self.total_functions += 1
            if decorators:
                self.total_decorators += len(decorators)

        self.graph.add_edge(file_node, func_node, relation="DEFINES_FUNCTION")

        # Track function parameters.
        self.function_params[func_node] = self._parse_parameters(node.args)

        # Process decorators
        for decorator in node.decorator_list:
            decorator_name = self._get_name(decorator)
            decorator_node = f"Decorator: {decorator_name}"
            if not self.graph.has_node(decorator_node):
                self.graph.add_node(decorator_node, type="decorator", name=decorator_name)
            self.graph.add_edge(func_node, decorator_node, relation="USES_DECORATOR")

    def _get_name(self, node):
        """Get the name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_name(node.value) + '.' + node.attr
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        elif isinstance(node, ast.Subscript):
            return self._get_name(node.value)
        elif isinstance(node, ast.Index):
            return self._get_name(node.value)
        elif isinstance(node, ast.Str):
            return node.s
        else:
            return ""

    def _parse_parameters(self, args: ast.arguments) -> List[Dict[str, Any]]:
        """Parse function parameters."""
        params = []

        for arg in args.args:
            param_dict = {"name": arg.arg}
            if arg.annotation:
                param_dict["type"] = self._get_annotation(arg.annotation)
            params.append(param_dict)

        # Handle *args
        if args.vararg:
            param_dict = {"name": '*' + args.vararg.arg}
            if args.vararg.annotation:
                param_dict["type"] = self._get_annotation(args.vararg.annotation)
            params.append(param_dict)

        # Handle **kwargs
        if args.kwarg:
            param_dict = {"name": '**' + args.kwarg.arg}
            if args.kwarg.annotation:
                param_dict["type"] = self._get_annotation(args.kwarg.annotation)
            params.append(param_dict)

        return params

    def _get_annotation(self, node):
        """Get the annotation type from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            return self._get_annotation(node.value) + '[' + self._get_annotation(node.slice) + ']'
        elif isinstance(node, ast.Index):
            return self._get_annotation(node.value)
        elif isinstance(node, ast.Attribute):
            return self._get_annotation(node.value) + '.' + node.attr
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Tuple):
            return '(' + ', '.join(self._get_annotation(elt) for elt in node.elts) + ')'
        else:
            return ""

    def _process_dependency_file(self, file_path: str):
        """Process dependency files like requirements.txt, setup.py, pyproject.toml, Pipfile, Pipfile.lock."""
        try:
            if file_path in self.analyzed_files:
                return

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            relative_path = os.path.relpath(file_path, self.directory)
            file_node = f"Dependency File: {relative_path}"

            # Add to analyzed files set.
            self.analyzed_files.add(file_path)

            # Add file node if it doesn't exist.
            if not self.graph.has_node(file_node):
                self.graph.add_node(file_node, type="dependency_file", path=relative_path)

            # Process dependencies
            if file_path.endswith("requirements.txt"):
                dependencies = self._parse_requirements_txt(content)
            elif file_path.endswith("Pipfile"):
                dependencies = self._parse_pipfile(content)
            elif file_path.endswith("Pipfile.lock"):
                dependencies = self._parse_pipfile_lock(content)
            elif file_path.endswith("setup.py"):
                dependencies = self._parse_setup_py(content)
            elif file_path.endswith("pyproject.toml"):
                dependencies = self._parse_pyproject_toml(content)
            else:
                dependencies = set()

            for dep in dependencies:
                dep_node = f"Dependency: {dep}"
                if not self.graph.has_node(dep_node):
                    self.graph.add_node(dep_node, type="dependency", name=dep)
                self.graph.add_edge(file_node, dep_node, relation="HAS_DEPENDENCY")

                self.dependencies.add(dep)

            self.total_dependencies_count = len(self.dependencies)

        except Exception as e:
            print(f"\nError processing dependency file {file_path}: {str(e)}", file=sys.stderr)

    def _parse_requirements_txt(self, content: str) -> Set[str]:
        """Parse requirements.txt content."""
        dependencies = set()
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                dep = re.split('[<>=!~]', line)[0].strip()
                dependencies.add(dep)
        return dependencies

    def _parse_pipfile(self, content: str) -> Set[str]:
        """Parse Pipfile content."""
        dependencies = set()
        pattern = r'^\s*"(.*?)"\s*='
        for line in content.splitlines():
            match = re.match(pattern, line)
            if match:
                dep = match.group(1)
                dependencies.add(dep)
        return dependencies

    def _parse_pipfile_lock(self, content: str) -> Set[str]:
        """Parse Pipfile.lock content."""
        dependencies = set()
        data = json.loads(content)
        for dep in data.get('default', {}):
            dependencies.add(dep)
        for dep in data.get('develop', {}):
            dependencies.add(dep)
        return dependencies

    def _parse_setup_py(self, content: str) -> Set[str]:
        """Parse setup.py content."""
        dependencies = set()
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'setup':
                    for keyword in node.keywords:
                        if keyword.arg == 'install_requires':
                            if isinstance(keyword.value, (ast.List, ast.Tuple)):
                                for elt in keyword.value.elts:
                                    dep = elt.s if isinstance(elt, ast.Str) else ''
                                    dep = re.split('[<>=!~]', dep)[0].strip()
                                    dependencies.add(dep)
        except Exception as e:
            print(f"Error parsing setup.py: {str(e)}", file=sys.stderr)
        return dependencies

    def _parse_pyproject_toml(self, content: str) -> Set[str]:
        """Parse pyproject.toml content."""
        dependencies = set()
        try:
            import toml
            data = toml.loads(content)
            deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})
            for dep in deps:
                if dep != 'python':
                    dependencies.add(dep)
        except Exception as e:
            print(f"Error parsing pyproject.toml: {str(e)}", file=sys.stderr)
        return dependencies

    def _convert_sets_to_lists(self, obj):
        """Recursively convert sets to lists in the given object."""
        if isinstance(obj, dict):
            return {k: self._convert_sets_to_lists(v) for k, v in obj.items()}
        elif isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, list):
            return [self._convert_sets_to_lists(v) for v in obj]
        else:
            return obj

    def save_graph(self, output_path: str):
        """Save the knowledge graph in standard JSON format."""
        data = json_graph.node_link_data(self.graph)
        metadata = {
            "stats": {
                "total_files": self.total_files,
                "total_classes": self.total_classes,
                "total_functions": self.total_functions,
                "total_methods": self.total_methods,
                "total_modules": self.total_modules,
                "total_imports": self.total_imports,
                "total_dependencies": self.total_dependencies_count,
                "total_decorators": self.total_decorators,
            },
            "function_params": self.function_params,
            "function_returns": self.function_returns,
            "class_methods": self.class_methods,
        }

        # Convert sets to lists in metadata
        metadata = self._convert_sets_to_lists(metadata)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"graph": data, "metadata": metadata}, f, indent=2)

    def visualize_graph(self):
        """Visualize the knowledge graph."""
        try:
            import matplotlib.pyplot as plt

            # Create color map for different node types
            color_map = {
                "file": "#ADD8E6",       # Light blue
                "class": "#90EE90",      # Light green
                "function": "#FFE5B4",   # Peach
                "method": "#FFDAB9",     # Light peach
                "module": "#E6E6FA",     # Lavender
                "entity": "#FFD700",     # Gold
                "dependency_file": "#C0C0C0",  # Silver
                "dependency": "#8A2BE2",  # Blue Violet
                "decorator": "#FFB6C1",  # Light pink
            }

            # Set node colors
            node_colors = [
                color_map.get(self.graph.nodes[node].get("type", "file"), "lightgray")
                for node in self.graph.nodes()
            ]

            # Create figure and axis explicitly
            fig, ax = plt.subplots(figsize=(20, 15))

            # Calculate layout
            pos = nx.spring_layout(self.graph, k=1.5, iterations=50)

            # Draw the graph
            nx.draw(
                self.graph,
                pos,
                ax=ax,
                with_labels=True,
                node_color=node_colors,
                node_size=2000,
                font_size=8,
                font_weight="bold",
                arrows=True,
                edge_color="gray",
                arrowsize=20,
            )

            # Add legend
            legend_elements = [
                plt.Line2D(
                    [0], [0],
                    marker='o',
                    color='w',
                    markerfacecolor=color,
                    label=node_type,
                    markersize=10
                )
                for node_type, color in color_map.items()
            ]

            # Place legend outside the plot
            ax.legend(
                handles=legend_elements,
                loc='center left',
                bbox_to_anchor=(1.05, 0.5),
                title="Node Types"
            )

            # Set title
            ax.set_title("Python Code Knowledge Graph Visualization", pad=20)

            # Adjust layout to accommodate legend
            plt.subplots_adjust(right=0.85)

            # Show plot
            plt.show()

        except ImportError:
            print("Matplotlib is required for visualization. Install it using 'pip install matplotlib'.")


if __name__ == "__main__":
    try:
        # Directory containing the Python codebase.
        print("Python Code Knowledge Graph Generator")
        print("------------------------------------")
        codebase_dir = input("Enter the path to the codebase directory: ").strip()

        if not os.path.exists(codebase_dir):
            raise ValueError(f"Directory does not exist: {codebase_dir}")

        output_file = "python_code_knowledge_graph.json"

        # Create and analyze the codebase.
        print("\nAnalyzing codebase...")
        ckg = PythonCodeKnowledgeGraph(directory=codebase_dir)
        ckg.analyze_codebase()

        # Save in standard format.
        print("\nSaving graph...")
        ckg.save_graph(output_file)
        print(f"\nPython code knowledge graph saved to {output_file}")

        # Display metadata stats
        print("\nCodebase Statistics:")
        print("-------------------")
        stats = {
            "Total Files": ckg.total_files,
            "Total Classes": ckg.total_classes,
            "Total Functions": ckg.total_functions,
            "Total Methods": ckg.total_methods,
            "Total Modules": ckg.total_modules,
            "Total Imports": ckg.total_imports,
            "Total Dependencies": ckg.total_dependencies_count,
            "Total Decorators": ckg.total_decorators,
        }

        # Calculate max length for padding
        max_len = max(len(key) for key in stats.keys())

        # Print stats in aligned columns
        for key, value in stats.items():
            print(f"{key:<{max_len + 2}}: {value:,}")

        # Optional visualization.
        while True:
            visualize = input("\nWould you like to visualize the graph? (yes/no): ").strip().lower()
            if visualize in ["yes", "no"]:
                break
            print("Invalid choice. Please enter yes or no.")

        if visualize == "yes":
            print("\nGenerating visualization...")
            ckg.visualize_graph()

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
    finally:
        print("\nDone.")
