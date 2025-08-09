"""File utility functions."""
import os
import shutil
from pathlib import Path
from typing import Optional


def ensure_directory(path: Path) -> None:
    """
    Ensure directory exists, create if not.
    
    Args:
        path: Directory path
    """
    path.mkdir(parents=True, exist_ok=True)


def clean_directory(path: Path) -> None:
    """
    Clean directory contents.
    
    Args:
        path: Directory path to clean
    """
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_static_files(src: Path, dst: Path) -> None:
    """
    Copy static files from source to destination.
    
    Args:
        src: Source directory
        dst: Destination directory
    """
    if not src.exists():
        return
    
    ensure_directory(dst)
    
    for item in src.iterdir():
        if item.is_file():
            shutil.copy2(item, dst / item.name)
        elif item.is_dir():
            shutil.copytree(item, dst / item.name, dirs_exist_ok=True)


def write_html(content: str, output_path: Path) -> None:
    """
    Write HTML content to file.
    
    Args:
        content: HTML content
        output_path: Output file path
    """
    ensure_directory(output_path.parent)
    output_path.write_text(content, encoding='utf-8')


def get_relative_path(from_path: Path, to_path: Path) -> str:
    """
    Get relative path from one file to another.
    
    Args:
        from_path: Source path
        to_path: Target path
        
    Returns:
        Relative path as string
    """
    try:
        return os.path.relpath(to_path, from_path.parent)
    except ValueError:
        # Paths are on different drives (Windows)
        return str(to_path)