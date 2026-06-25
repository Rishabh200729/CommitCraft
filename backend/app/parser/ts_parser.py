import os
from pathlib import Path
from typing import List, Set
import tree_sitter_typescript as tsts
from tree_sitter import Language, Parser

class TypeScriptParser:
    def __init__(self):
        # We use TSX grammar as it covers both TS and TSX
        self.language = Language(tsts.language_tsx())
        self.parser = Parser(self.language)
        
        # Query to extract import strings
        self.import_query = self.language.query("""
            (import_statement source: (string (string_fragment) @import_path))
            (export_statement source: (string (string_fragment) @import_path))
        """)

    def extract_imports_from_content(self, code: str) -> List[str]:
        """
        Parses a TS/TSX code string and returns a list of all raw import strings.
        """
        try:
            tree = self.parser.parse(bytes(code, 'utf-8'))
            
            matches = self.import_query.matches(tree.root_node)
            imports: Set[str] = set()
            
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2 and isinstance(match[1], dict):
                    # Older style
                    for capture_name, nodes in match[1].items():
                        if not isinstance(nodes, list):
                            nodes = [nodes]
                        for node in nodes:
                            imports.add(code[node.start_byte:node.end_byte])
                else:
                    captures = match[1] if isinstance(match, tuple) else match
                    if isinstance(captures, dict):
                        for nodes in captures.values():
                            if not isinstance(nodes, list):
                                nodes = [nodes]
                            for node in nodes:
                                imports.add(code[node.start_byte:node.end_byte])
                    else:
                        for node, name in captures:
                            imports.add(code[node.start_byte:node.end_byte])
            
            return list(imports)
        except Exception as e:
            print(f"Error parsing content: {e}")
            return []

    def extract_imports(self, file_path: str) -> List[str]:
        """
        Parses a TS/TSX file and returns a list of all raw import strings.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.extract_imports_from_content(code)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []

    def resolve_import_path(self, current_file: str, raw_import: str, project_root: str) -> str | None:
        """
        Resolves a raw import string to an absolute path within the project root.
        Only resolves local imports (starting with . or .. or @/).
        Returns None for third-party packages.
        """
        if not raw_import.startswith('.') and not raw_import.startswith('@/'):
            return None # Third-party or absolute import we don't track for now
            
        current_dir = Path(current_file).parent
        
        # Handle Next.js/Vite alias imports like @/components/...
        if raw_import.startswith('@/'):
            # In our setup, frontend/src is typically the root of @/
            # We assume project_root is frontend/
            resolved_path = Path(project_root) / "src" / raw_import[2:]
        else:
            resolved_path = (current_dir / raw_import).resolve()

        # Try to find the actual file with extensions
        extensions = ['.tsx', '.ts', '/index.tsx', '/index.ts']
        for ext in extensions:
            candidate = str(resolved_path) + ext
            if os.path.exists(candidate):
                return os.path.abspath(candidate)
            
            # If the import already had the extension (rare in TS but possible)
            if str(resolved_path).endswith('.ts') or str(resolved_path).endswith('.tsx'):
                if os.path.exists(str(resolved_path)):
                    return str(resolved_path)

        return None
