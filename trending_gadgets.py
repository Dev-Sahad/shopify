"""
Trending Gadgets Wrapper for backward compatibility.
Exposes gadgets from the smart gadget hunter module.
"""

from gadget_hunter import (
    SMART_GADGET_CATALOG as TRENDING_GADGETS,
    get_all_gadgets as get_trending_gadgets,
    get_gadget_by_id,
    search_gadgets
)
