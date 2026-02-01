#!/usr/bin/env python3
"""
Output Formatting Utility
Handles consistent CLI output formatting.
"""

from typing import Dict, Any, List
from datetime import datetime


class OutputFormatter:
    """Formats output for CLI display."""
    
    @staticmethod
    def format_header(title: str, width: int = 60) -> str:
        """Format a section header."""
        return f"\n{'='*width}\n{title}\n{'='*width}"
    
    @staticmethod
    def format_section(title: str) -> str:
        """Format a section title."""
        return f"\n{title}:"
    
    @staticmethod
    def format_finding(severity: str, title: str, description: str) -> str:
        """Format a finding with severity."""
        severity_label = {
            "CRITICAL": "[CRITICAL]",
            "HIGH": "[HIGH]",
            "MEDIUM": "[MEDIUM]",
            "LOW": "[LOW]"
        }.get(severity, "[INFO]")
        
        return f"  {severity_label} {title}\n    • {description}"
    
    @staticmethod
    def format_metric(name: str, value: str, status: str = "") -> str:
        """Format a metric with optional status."""
        if status:
            return f"  {name}: {value} {status}"
        return f"  {name}: {value}"
    
    @staticmethod
    def format_recommendation(text: str) -> str:
        """Format a recommendation."""
        return f"  • {text}"
