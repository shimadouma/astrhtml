"""Date formatting utilities."""
from datetime import datetime
from typing import Optional


def format_timestamp(timestamp: int, format_str: str = '%Y年%m月%d日') -> str:
    """
    Format Unix timestamp to Japanese date string.
    
    Args:
        timestamp: Unix timestamp
        format_str: Date format string
        
    Returns:
        Formatted date string
    """
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime(format_str)
    except (ValueError, OSError):
        return 'Unknown Date'


def format_date_range(start_timestamp: int, end_timestamp: int) -> str:
    """
    Format date range for display.
    
    Args:
        start_timestamp: Start Unix timestamp
        end_timestamp: End Unix timestamp
        
    Returns:
        Formatted date range string
    """
    start_date = format_timestamp(start_timestamp)
    end_date = format_timestamp(end_timestamp)
    
    return f"{start_date} ~ {end_date}"


def get_relative_time(timestamp: int) -> str:
    """
    Get relative time description.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Relative time string (e.g., "2日前", "3ヶ月前")
    """
    now = datetime.now()
    try:
        dt = datetime.fromtimestamp(timestamp)
        diff = now - dt
        
        days = diff.days
        
        if days < 0:
            return "未来"
        elif days == 0:
            return "今日"
        elif days == 1:
            return "昨日"
        elif days < 7:
            return f"{days}日前"
        elif days < 30:
            weeks = days // 7
            return f"{weeks}週間前"
        elif days < 365:
            months = days // 30
            return f"{months}ヶ月前"
        else:
            years = days // 365
            return f"{years}年前"
    except (ValueError, OSError):
        return "Unknown"