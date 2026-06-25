import re
from typing import List, Dict

class DiffParser:
    @staticmethod
    def parse_diff(diff_text: str) -> List[Dict[str, str]]:
        """
        Parses a raw git diff string and returns a list of changed files with their status.
        Status can be: 'added', 'modified', 'removed'
        """
        changed_files = []
        
        # Regex to match the 'diff --git a/path b/path' line
        # The path is captured from the 'b/' part
        file_header_pattern = re.compile(r'^diff --git a/(.*?) b/(.*?)$', re.MULTILINE)
        
        # Find all file blocks in the diff
        blocks = re.split(r'^diff --git ', diff_text, flags=re.MULTILINE)
        
        for block in blocks:
            if not block.strip():
                continue
                
            # Reconstruct the split block line to match regex
            block = "diff --git " + block
            
            match = file_header_pattern.search(block)
            if not match:
                continue
                
            file_a = match.group(1)
            file_b = match.group(2)
            
            # Default is modified, unless we see 'new file mode' or 'deleted file mode'
            status = "modified"
            if "new file mode" in block:
                status = "added"
            elif "deleted file mode" in block:
                status = "removed"
                
            # Use file_b unless it's deleted, then file_a
            file_path = file_b if status != "removed" else file_a
            
            changed_files.append({
                "file": file_path,
                "status": status,
                "block": block
            })
            
        return changed_files

    @staticmethod
    def reconstruct_file_from_added_diff(block: str) -> str:
        """
        Reconstructs the full content of an added file from its diff block.
        """
        lines = []
        for line in block.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                lines.append(line[1:])
        return '\n'.join(lines)

    @staticmethod
    def extract_import_changes_from_modified_diff(block: str) -> dict:
        """
        Extracts added and removed import paths from a modified file diff block.
        """
        added_imports = []
        removed_imports = []
        
        # Regex to match TS/JS imports/exports with from clause
        import_from_pattern = re.compile(r'^\s*(?:import|export)\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]')
        # Regex to match TS/JS direct imports
        import_direct_pattern = re.compile(r'^\s*import\s+[\'"]([^\'"]+)[\'"]')
        
        for line in block.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                clean_line = line[1:].strip()
                match = import_from_pattern.match(clean_line) or import_direct_pattern.match(clean_line)
                if match:
                    added_imports.append(match.group(1))
            elif line.startswith('-') and not line.startswith('---'):
                clean_line = line[1:].strip()
                match = import_from_pattern.match(clean_line) or import_direct_pattern.match(clean_line)
                if match:
                    removed_imports.append(match.group(1))
                    
        return {
            "added": added_imports,
            "removed": removed_imports
        }