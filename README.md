# 🐍 CntxtPY: Minify Your Python Codebase Context for LLMs

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

> 🤯 **75% Token Reduction In Context Window Usage!**

## Why CntxtPY?

-  Boosts precision: Maps relationships and dependencies for clear analysis.
-  Eliminates noise: Focuses LLMs on key code insights.
-  Supports analysis: Reveals architecture for smarter LLM insights.
-  Speeds solutions: Helps LLMs trace workflows and logic faster.
-  Improves recommendations: Gives LLMs detailed metadata for better suggestions.
-  Optimized prompts: Provides structured context for better LLM responses.
-  Streamlines collaboration: Helps LLMs explain and document code easily.

Supercharge your LLM's understanding of Python codebases. CntxtPY generates comprehensive knowledge graphs that help LLMs navigate and comprehend your code structure with minimal token usage.

It's like handing your LLM the cliff notes instead of a novel.

## ✨ Features

- 🔍 Deep analysis of Python codebases
- 📊 Generates detailed knowledge graphs of:
  - Module relationships and imports
  - Class hierarchies and methods
  - Function signatures and type hints
  - Package structures
  - Circular dependency detection
  - Requirements.txt/Poetry/Pipenv dependencies
  - Decorators and protocols
- 🎯 Specially designed for LLM context windows
- 📈 Built-in visualization capabilities of your project's knowledge graph
- 🚀 Support for modern Python frameworks and patterns

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/brandondocusen/CntxtPY.git

# Navigate to the directory
cd CntxtPY

# Install required packages
pip install networkx matplotlib typing-extensions

# Run the analyzer
python cntxtpy.py
```

When prompted, enter the path to your Python codebase. The tool will generate a `python_code_knowledge_graph.json` file and offer to visualize the relationships.

## 💡 Example Usage with LLMs

The LLM can now provide detailed insights about your codebase's implementations, understanding the relationships between components, modules, and packages! After generating your knowledge graph, you can upload it as a single file to give LLMs deep context about your codebase. Here's a powerful example prompt:

```Prompt Example
Based on the knowledge graph, explain how dependency injection is implemented in this application, including which classes use the dependency container and how services are registered.
```

```Prompt Example
Based on the knowledge graph, map out the core package structure - starting from __main__.py through to the different modules and their interactions.
```

```Prompt Example
Using the knowledge graph, analyze the decorator usage in this application. Which decorators exist, what do they modify, and how do they interact with functions/classes?
```

```Prompt Example
From the knowledge graph data, break down this application's API route structure, focusing on endpoints and their implementation patterns.
```

```Prompt Example
According to the knowledge graph, identify all error handling patterns in this codebase - where are exceptions caught, how are they processed, and what custom exceptions exist?
```

```Prompt Example
Based on the knowledge graph's dependency analysis, outline the key pip/poetry dependencies this project relies on and their primary use cases in the application.
```

```Prompt Example
Using the knowledge graph's type hint analysis, explain how the application handles data validation and type checking across different services.
```

## 📊 Output Format

The tool generates two main outputs:
1. A JSON knowledge graph (`python_code_knowledge_graph.json`)
2. Optional visualization using matplotlib

The knowledge graph includes:
- Detailed metadata about your codebase
- Node and edge relationships
- Function signatures and type hints
- Class hierarchies
- Import mappings
- Package structures

## 🤝 Contributing

We love contributions! Whether it's:
- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation improvements
- 🎨 Visualization enhancements

Just fork, make your changes, and submit a PR. Check out our [contribution guidelines](CONTRIBUTING.md) for more details.

## 🎯 Future Goals

- [ ] Deeper support for additional frameworks
- [ ] Interactive web-based visualizations
- [ ] Custom graph export formats
- [ ] Integration with popular IDEs
- [ ] Support for Cython and PyPy

## 📝 License

MIT License - feel free to use this in your own projects!

## 🌟 Show Your Support

If you find CntxtPY helpful, give it a star! ⭐️ 

---

Made with ❤️ for the LLM and Python communities
