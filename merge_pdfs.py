from collections.abc import Iterable
from genericpath import isdir
from glob import glob
from os import PathLike
from os.path import basename, getmtime
from typing import Literal, AnyStr

from pypdf import PdfWriter, PdfReader
from pypdf.errors import PyPdfError, PdfReadError


"""
This script merges pdf files in a given directory into a single pdf file.

Usage:
    python merge_pdfs.py [options]
"""


_File = str | bytes | PathLike
_Order = Literal["none", "name", "date"]

# Helper function to get files by fila names, glob pattern, or directory
# Arguments are mutually exclusive; only one must be provided
# Does not perform validation if files exist
# TODO: docstring
def _get_files(
    *,
    files: Iterable[_File] | None = None,
    pattern: AnyStr | None = None,
    directory: _File | None = None
) -> list[_File | bytes | str]:
    if files is None and pattern is None and directory is None:
        raise ValueError("Either 'files', 'pattern', or 'directory' must be provided.")
    elif files is not None:
        return [basename(file) for file in files]
    elif pattern is not None:
        return [basename(file) for file in glob(pathname=pattern)]
    elif directory is not None:
        return [basename(file) for file in glob(pathname=f"{directory}/*")]
    else:
        return []

# Helper function to sort files by file name, modified time, or none
# Does not perform validation if files exist
# TODO: docstring
def _sort_files(
    files: Iterable[_File], 
    /,
    order: _Order = "none", 
    ascending: bool = False
) -> list[_File]:
    if order == "none":
        return list(files)
    elif order == "name":
        return sorted(files, key=lambda f: basename(f), reverse=not ascending)
    elif order == "date":
        return sorted(files, key=lambda f: getmtime(f), reverse=not ascending)
    else:
        raise ValueError(f"Invalid order: {order}; expected 'none', 'name', or 'date'")

# Performs merging of PDFs
# TODO: docstring
def merge_pdfs(
    pdfs: list[_File],
    /,
    *,
    output: str = "merged.pdf",
    skip_invalid: bool = False,
) -> dict[str, str | list[str]]:
    if not isinstance(pdfs, list):
        raise TypeError(f"Invalid list of pdfs type: {type(pdfs).__name__}; expected list")
    
    if not all(isinstance(pdf, _File.__args__) for pdf in pdfs):
        raise TypeError(f"Invalid pdf file name type: {type(pdfs).__name__}; expected str, bytes, or PathLike")

    if not isinstance(output, str):
        raise TypeError(f"Invalid output type: {type(output).__name__}; expected str")

    if not output.endswith(".pdf"):
        output += ".pdf"

    results = {"output": "", "merged": [], "skipped": []}

    with PdfWriter() as merger:
        for pdf in pdfs:
            try:
                if isdir(pdf):
                    raise IsADirectoryError(f"Not a valid file (a directory was given): {pdf}")

                # Try to open file if valid pdf
                pdf_read = PdfReader(pdf) 

                # Then append to the pdf to be merged
                merger.append(pdf_read)

                results["merged"].append(pdf)

            except (PyPdfError, FileNotFoundError, IsADirectoryError, PermissionError) as e:
                if skip_invalid:
                    results["skipped"].append(pdf)
                    continue
                else:
                    raise PdfReadError(f"Error processing file {pdf}: {e}") from e
                
        # Only write output file when there is at least one PDF file
        if len(results["merged"]) > 0:
            merger.write(output)
            results["output"] = output

    return results


if __name__ == '__main__':
    from argparse import SUPPRESS, ArgumentParser
    from datetime import datetime

    parser = ArgumentParser(description="Merge PDF files.")
    input_file_group = parser.add_mutually_exclusive_group(required=True)

    input_file_group.add_argument(
        "-f", "--files", 
        help="list of specific PDF files to merge",
        nargs="+",
        type=str,
    )

    input_file_group.add_argument(
        "-p", "--pattern",
        help="glob pattern to match input PDF files (e.g., '*.pdf' or 'folder/*.pdf')",
        type=str,
    )

    input_file_group.add_argument(
        "-d", "--directory",
        help="directory containing PDF files to merge",
        type=str,
    )

    parser.add_argument(
        "-o", "--output",
        help="name of the output PDF file (e.g., merged.pdf)",
        default=f"merged_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf",
        type=str,
    )

    parser.add_argument(
        "--order",
        choices=("none", "name", "date"),
        default="none",
        help="order PDFs by 'name', 'date', or 'none' (default is 'none')"
    )

    parser.add_argument(
        "--ascending",
        action="store_true",
        help="sort in ascending order; by default, sorting is descending when "
             "using order 'name' or 'date'"
    )

    parser.add_argument(
        "--skip-invalid",
        action="store_true",
        help="skip invalid PDF files during merging; if not set, the merge will"
            " abort on the first invalid file"
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help=SUPPRESS
    )

    args = parser.parse_args()

    pdfs = _get_files(files=args.files, pattern=args.pattern, directory=args.directory)
    pdfs = _sort_files(pdfs, order=args.order, ascending=args.ascending)

    if len(pdfs) == 0 or pdfs[0] == "":
        print("No PDF files to merge.")
        exit(1)

    # Ask for confirmation before proceeding; skipped if yes=True
    if not args.yes:
        print("PDF Files to merge (in order):")
        for pdf in pdfs:
            print(f"- {pdf}")

        print(f"Output PDF file: {args.output}")

        response = input("Proceed merging? ([y]/n): ").lower()
        if response in {"yes", "y", ""}:
            print("Merging PDFs...")
        else:
            print("Aborted.")
            exit(0)

    try:
        results = merge_pdfs(
            pdfs,
            output=args.output,
            skip_invalid=args.skip_invalid,
        )
    except Exception as e:
        print(f"Error encountered while merging PDFs: {e}")
        exit(1)

    if results.get("output") == "":
        print("No PDF files were merged.")
        exit(1)
    else:
        print(f"Merged PDFs into {results.get('output')}")
        print(f"Merged: {results.get('merged')}")
        print(f"Skipped: {results.get('skipped')}")

