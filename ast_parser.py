from tree_sitter import Parser, Language
from loguru import logger
import os
import subprocess

# Map file extensions to language identifiers
EXTENSION_TO_LANGUAGE = {
    "js": "javascript", "jsx": "javascript", "ts": "typescript",
    "tsx": "typescript", "mjs": "javascript", "py": "python", "rs": "rust",
    "go": "go", "java": "java", "cpp": "cpp", "cc": "cpp", "cxx": "cpp",
    "c": "cpp", "h": "cpp", "hpp": "cpp", "cs": "csharp", "rb": "ruby",
    "md": "markdown", "rst": "markdown", "txt": "markdown", "html": "html",
    "vue": "vue", "php": "php", "sh": "bash", "bash": "bash",
    "zsh": "bash", "json": "json",
    "yaml": "yaml", "yml": "yaml",
    "sql": "sql", "swift": "swift", "kt": "kotlin", "clj": "clojure",
}

# Cache for parsers and languages
_parser_cache = {}
_language_cache = {}


def setup_tree_sitter_languages():
    """Set up tree-sitter languages by downloading and building parsers"""
    CACHE_DIR = "cache"
    BUILD_DIR = os.path.join(CACHE_DIR, "build")
    TMP_DIR = "/tmp"

    os.makedirs(BUILD_DIR, exist_ok=True)

    LANGUAGES = {
        "python": {"repo": "tree-sitter/tree-sitter-python"},
        "javascript": {"repo": "tree-sitter/tree-sitter-javascript"},
        "typescript": {
            "repo": "tree-sitter/tree-sitter-typescript",
            "subpath": "tsx",
            "language_name": "tsx"
        },
        "cpp": {"repo": "tree-sitter/tree-sitter-cpp"},
        "java": {"repo": "tree-sitter/tree-sitter-java"},
        "rust": {"repo": "tree-sitter/tree-sitter-rust"},
        "go": {"repo": "tree-sitter/tree-sitter-go"},
        "ruby": {"repo": "tree-sitter/tree-sitter-ruby"},
        "php": {"repo": "tree-sitter/tree-sitter-php"},
        "c-sharp": {
            "repo": "tree-sitter/tree-sitter-c-sharp",
            "language_name": "c_sharp"
        },
        "markdown": {
            "repo": "MDeiml/tree-sitter-markdown",
            "subpath": "tree-sitter-markdown"
        },
        "vue": {"repo": "ikatyang/tree-sitter-vue"},
    }

    logger.debug("Downloading and building tree-sitter parsers")

    for lang_key, config in LANGUAGES.items():
        try:
            repo_path = os.path.join(CACHE_DIR, f"tree-sitter-{lang_key}")
            clone_cmd = f"git clone https://github.com/{config['repo']} {repo_path}"
            subprocess.run(clone_cmd, shell=True, check=True)

            build_path = os.path.join(BUILD_DIR, f"{lang_key}.so")
            source_path = os.path.join(repo_path, config.get('subpath', ''))
            Language.build_library(
                build_path,
                [source_path] if source_path else [repo_path]
            )

            tmp_path = os.path.join(TMP_DIR, f"{lang_key}.so")
            subprocess.run(f"cp {build_path} {tmp_path}", shell=True, check=True)

            language_name = config.get('language_name', lang_key)
            _language_cache[lang_key] = Language(tmp_path, language_name)

            logger.debug(f"Successfully set up {lang_key}")

        except Exception as e:
            logger.error(f"Failed to set up {lang_key}: {e}")
            continue

    logger.debug("Finished setting up tree-sitter parsers")
    return _language_cache


def get_parser(language):
    """Get or create a parser for the specified language"""
    if language not in _parser_cache:
        try:
            parser = Parser()
            if language in _language_cache:
                parser.set_language(_language_cache[language])
                _parser_cache[language] = parser
            else:
                logger.error(f"Language {language} not available")
                return None
        except Exception as e:
            logger.error(f"Error creating parser for {language}: {e}")
            return None
    return _parser_cache.get(language)


# Initialize languages at module load
_language_cache = setup_tree_sitter_languages()

def parse_code(content, language):
    """Parse code content using tree-sitter"""
    if not content or not language:
        return None

    parser = get_parser(language)
    if not parser:
        return None

    try:
        # Handle both string and bytes input
        if isinstance(content, str):
            content = content.encode()
        # content is already bytes, use it directly

        # Parse the content
        tree = parser.parse(content)
        root_node = tree.root_node

        return {
            "language": language,
            "size": len(content),
            "ast_node_count": count_nodes(root_node),
            "entities": extract_entities(root_node, language),
            "imports": extract_imports(root_node, language, content),
            "functions": extract_functions(root_node, language),
            "classes": extract_classes(root_node, language),
        }
    except Exception as e:
        print(f"Error parsing {language} content: {e}")
        return None

def get_language_from_path(file_path):
    """Determine language based on file extension"""
    _, ext = os.path.splitext(file_path)
    if not ext:
        return None

    # Remove the dot from extension
    ext = ext[1:].lower()
    return EXTENSION_TO_LANGUAGE.get(ext)


# def parse_code(content, language):
#     """Parse code content using tree-sitter"""
#     if not content or not language:
#         return None
#
#     parser = get_parser(language)
#     if not parser:
#         return None
#
#     try:
#         # Parse the content
#         tree = parser.parse(content)
#
#         # Get the root node
#         root_node = tree.root_node
#
#         # Extract basic information
#         return {
#             "language": language,
#             "size": len(content),
#             "ast_node_count": count_nodes(root_node),
#             "entities": extract_entities(root_node, language),
#             "imports": extract_imports(root_node, language, content),
#             "functions": extract_functions(root_node, language),
#             "classes": extract_classes(root_node, language),
#         }
#
#     except Exception as e:
#         print(f"Error parsing {language} content: {e}")
#         return None


def count_nodes(node):
    """Count the total number of nodes in the AST"""
    count = 1  # Count the current node
    for child in node.children:
        count += count_nodes(child)
    return count


def extract_entities(node, language):
    """Extract named entities from the AST"""
    entities = []

    # Common entity types across languages
    entity_types = {
        "python": ["function_definition", "class_definition"],
        "javascript": ["function_declaration", "class_declaration", "method_definition"],
        "typescript": ["function_declaration", "class_declaration", "method_definition", "interface_declaration"],
        "java": ["method_declaration", "class_declaration", "interface_declaration"],
        "cpp": ["function_definition", "class_specifier", "struct_specifier"],
        "rust": ["function_item", "struct_item", "impl_item"],
        "go": ["function_declaration", "type_declaration"],
        # Add more languages as needed
    }

    def traverse(current_node):
        if current_node.type in entity_types.get(language, []):
            # Try to get entity name
            name_node = None

            # Find identifier node based on language and node type
            if language == "python":
                for child in current_node.children:
                    if child.type == "identifier":
                        name_node = child
                        break
            elif language in ["javascript", "typescript"]:
                if current_node.type in ["function_declaration", "class_declaration"]:
                    for child in current_node.children:
                        if child.type == "identifier":
                            name_node = child
                            break

            if name_node:
                entities.append({
                    "type": current_node.type,
                    "name": name_node.text.decode('utf-8')
                })

        # Recursively traverse children
        for child in current_node.children:
            traverse(child)

    traverse(node)
    return entities


def extract_imports(node, language, content):
    """Extract import statements from the AST"""
    imports = []

    # Define import node types for different languages
    import_types = {
        "python": ["import_statement", "import_from_statement"],
        "javascript": ["import_statement"],
        "typescript": ["import_statement"],
        "java": ["import_declaration"],
        "go": ["import_declaration"],
        # Add more languages as needed
    }

    def traverse(current_node):
        if current_node.type in import_types.get(language, []):
            import_text = content[current_node.start_byte:current_node.end_byte].decode('utf-8')
            imports.append(import_text.strip())

        # Recursively traverse children
        for child in current_node.children:
            traverse(child)

    traverse(node)
    return imports


def extract_functions(node, language):
    """Extract function definitions from the AST"""
    functions = []

    # Define function node types for different languages
    function_types = {
        "python": ["function_definition"],
        "javascript": ["function_declaration", "method_definition", "arrow_function"],
        "typescript": ["function_declaration", "method_definition", "arrow_function"],
        "java": ["method_declaration"],
        "cpp": ["function_definition"],
        "rust": ["function_item"],
        "go": ["function_declaration"],
        # Add more languages as needed
    }

    def traverse(current_node):
        if current_node.type in function_types.get(language, []):
            # Try to get function name
            name = "anonymous"
            for child in current_node.children:
                if child.type == "identifier":
                    name = child.text.decode('utf-8')
                    break

            functions.append({
                "name": name,
                "start_line": current_node.start_point[0],
                "end_line": current_node.end_point[0],
                "type": current_node.type
            })

        # Recursively traverse children
        for child in current_node.children:
            traverse(child)

    traverse(node)
    return functions


def extract_classes(node, language):
    """Extract class definitions from the AST"""
    classes = []

    # Define class node types for different languages
    class_types = {
        "python": ["class_definition"],
        "javascript": ["class_declaration"],
        "typescript": ["class_declaration", "interface_declaration"],
        "java": ["class_declaration", "interface_declaration"],
        "cpp": ["class_specifier", "struct_specifier"],
        "rust": ["struct_item", "impl_item"],
        # Add more languages as needed
    }

    def traverse(current_node):
        if current_node.type in class_types.get(language, []):
            # Try to get class name
            name = "anonymous"
            for child in current_node.children:
                if child.type == "identifier":
                    name = child.text.decode('utf-8')
                    break

            classes.append({
                "name": name,
                "start_line": current_node.start_point[0],
                "end_line": current_node.end_point[0],
                "type": current_node.type
            })

        # Recursively traverse children
        for child in current_node.children:
            traverse(child)

    traverse(node)
    return classes


def process_file_content(file_path, content):
    """Main entry point to process a file's content"""
    language = get_language_from_path(file_path)
    if not language:
        return None

    return parse_code(content, language)