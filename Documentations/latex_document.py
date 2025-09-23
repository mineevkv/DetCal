import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Union

class LatexDocument:
    """
    A class for creating LaTeX PDF documents programmatically.
    """
    
    def __init__(self, document_class: str = "article", 
                 document_class_options: Optional[List[str]] = None,
                 title: str = "Document",
                 author: str = "Author",
                 packages: Optional[List[str]] = None):
        """
        Initialize a LaTeX document.
        
        Args:
            document_class: LaTeX document class (article, report, book, etc.)
            document_class_options: Options for document class
            title: Document title
            author: Document author
            packages: List of LaTeX packages to include
        """
        self.document_class = document_class
        self.document_class_options = document_class_options or []
        self.title = title
        self.author = author
        self.packages = packages or ["amsmath", "graphicx", "hyperref"]
        
        self.content = []
        self.sections = []
        self.figures = []
        self.tables = []
        
        # Initialize with basic document structure
        self._initialize_document()
    
    def _initialize_document(self):
        """Initialize the basic LaTeX document structure."""
        self.content = [
            r"\documentclass",
            f"[{','.join(self.document_class_options)}]" if self.document_class_options else "",
            f"{{{self.document_class}}}",
            "",
            "% Packages",
        ]
        
        # Add packages
        for package in self.packages:
            if isinstance(package, dict):
                # Package with options
                pkg_name = list(package.keys())[0]
                options = package[pkg_name]
                if options:
                    self.content.append(f"\\usepackage[{options}]{{{pkg_name}}}")
                else:
                    self.content.append(f"\\usepackage{{{pkg_name}}}")
            else:
                # Simple package
                self.content.append(f"\\usepackage{{{package}}}")
        
        self.content.extend([
            "",
            "% Document information",
            f"\\title{{{self.title}}}",
            f"\\author{{{self.author}}}",
            f"\\date{{\\today}}",
            "",
            r"\begin{document}",
            "",
            r"\maketitle",
            ""
        ])
    
    def add_section(self, title: str, content: str, level: int = 1):
        """
        Add a section to the document.
        
        Args:
            title: Section title
            content: Section content
            level: Section level (1=section, 2=subsection, 3=subsubsection)
        """
        section_commands = {1: "section", 2: "subsection", 3: "subsubsection"}
        command = section_commands.get(level, "section")
        
        self.content.extend([
            f"\\{command}{{{title}}}",
            content,
            ""
        ])
        
        self.sections.append({"title": title, "level": level, "content": content})
    
    def add_text(self, text: str):
        """Add plain text to the document."""
        self.content.append(text)
        self.content.append("")
    
    def add_equation(self, equation: str, numbered: bool = True):
        """
        Add a mathematical equation.
        
        Args:
            equation: LaTeX equation code
            numbered: Whether to number the equation
        """
        env = "equation" if numbered else "equation*"
        self.content.extend([
            f"\\begin{{{env}}}",
            equation,
            f"\\end{{{env}}}",
            ""
        ])
    
    def add_figure(self, image_path: str, caption: str, label: str, 
                   width: str = "0.8\\textwidth", placement: str = "htbp"):
        """
        Add a figure to the document.
        
        Args:
            image_path: Path to the image file
            caption: Figure caption
            label: LaTeX label for referencing
            width: Image width
            placement: Figure placement options
        """
        figure_content = [
            f"\\begin{{figure}}[{placement}]",
            "\\centering",
            f"\\includegraphics[width={width}]{{{image_path}}}",
            f"\\caption{{{caption}}}",
            f"\\label{{{label}}}",
            "\\end{figure}",
            ""
        ]
        
        self.content.extend(figure_content)
        self.figures.append({
            "path": image_path,
            "caption": caption,
            "label": label
        })
    
    def add_table(self, data: List[List[str]], caption: str, label: str, 
                  headers: Optional[List[str]] = None):
        """
        Add a table to the document.
        
        Args:
            data: 2D list of table data
            caption: Table caption
            label: LaTeX label for referencing
            headers: Optional list of column headers
        """
        table_content = [
            "\\begin{table}[htbp]",
            "\\centering",
            "\\begin{tabular}{|" + "c|" * (len(data[0]) if data else 1) + "}",
            "\\hline"
        ]
        
        # Add headers if provided
        if headers:
            table_content.append(" & ".join(headers) + " \\\\")
            table_content.append("\\hline")
        
        # Add data rows
        for row in data:
            table_content.append(" & ".join(str(cell) for cell in row) + " \\\\")
            table_content.append("\\hline")
        
        table_content.extend([
            "\\end{tabular}",
            f"\\caption{{{caption}}}",
            f"\\label{{{label}}}",
            "\\end{table}",
            ""
        ])
        
        self.content.extend(table_content)
        self.tables.append({
            "headers": headers,
            "data": data,
            "caption": caption,
            "label": label
        })
    
    def add_bullet_list(self, items: List[str]):
        """Add a bulleted list."""
        self.content.append("\\begin{itemize}")
        for item in items:
            self.content.append(f"    \\item {item}")
        self.content.append("\\end{itemize}")
        self.content.append("")
    
    def add_numbered_list(self, items: List[str]):
        """Add a numbered list."""
        self.content.append("\\begin{enumerate}")
        for item in items:
            self.content.append(f"    \\item {item}")
        self.content.append("\\end{enumerate}")
        self.content.append("")
    
    def add_abstract(self, abstract_text: str):
        """Add an abstract section."""
        self.content.extend([
            "\\begin{abstract}",
            abstract_text,
            "\\end{abstract}",
            ""
        ])
    
    def generate_tex(self, output_path: Optional[str] = None) -> str:
        """
        Generate the LaTeX source code.
        
        Args:
            output_path: Path to save .tex file (optional)
            
        Returns:
            LaTeX source code as string
        """
        # Close the document
        final_content = self.content + ["\\end{document}"]
        tex_code = "\n".join(final_content)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(tex_code)
        
        return tex_code
    
    def compile_pdf(self, tex_code: Optional[str] = None, 
                   output_dir: Optional[str] = None,
                   clean_up: bool = True) -> str:
        """
        Compile the LaTeX document to PDF.
        
        Args:
            tex_code: LaTeX source code (if None, uses current content)
            output_dir: Output directory (uses temp dir if None)
            clean_up: Whether to clean up intermediate files
            
        Returns:
            Path to the generated PDF file
            
        Raises:
            RuntimeError: If LaTeX compilation fails
        """
        if tex_code is None:
            tex_code = self.generate_tex()
        
        # Create temporary directory if none provided
        if output_dir is None:
            temp_dir = tempfile.mkdtemp()
            output_dir = temp_dir
        else:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Write LaTeX file
        tex_file = Path(output_dir) / "results.tex"
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(tex_code)
        
        try:
            # Compile using pdflatex
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", str(tex_file)],
                cwd=output_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"LaTeX compilation failed:\n{result.stderr}")
            
            # Run twice to resolve references
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", str(tex_file)],
                cwd=output_dir,
                capture_output=True
            )
            
            # pdf_path = os.getcwd() + "\\results.pdf"
            pdf_path = Path(output_dir) / "document.pdf"
            
            # Clean up intermediate files
            if clean_up:
                for ext in ['.aux', '.log', '.out']:
                    cleanup_file = Path(output_dir) / f"document{ext}"
                    if cleanup_file.exists():
                        cleanup_file.unlink()
            
            return str(pdf_path)
            
        except FileNotFoundError:
            raise RuntimeError("pdflatex not found. Please install a LaTeX distribution.")
    
    def __str__(self) -> str:
        """Return the LaTeX source code."""
        return self.generate_tex()