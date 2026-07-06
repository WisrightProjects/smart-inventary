"""Canonical product catalog: the fixed set of recognizable products.

This is the single source of truth mapping a product name to its category.
Both the dummy-data seeder and the AI recognition label-mapping layer
(backend/models/product_recognizer.py) import from here so the two never
drift apart.
"""
from __future__ import annotations

PRODUCT_CATALOG: dict[str, str] = {
    "Pencil": "Stationery",
    "Notebook": "Books",
    "Book": "Books",
    "Marker": "Stationery",
    "Pen": "Stationery",
    "Scale": "Stationery",
    "Sharpener": "Stationery",
    "Glue Stick": "Stationery",
    "Highlighter": "Stationery",
    "Sketch Pen": "Stationery",
    "Calculator": "Electronics",
    "File Folder": "Office Supplies",
    "A4 Paper": "Office Supplies",
    "Stapler": "Office Supplies",
    "Tape": "Office Supplies",
    "Scissors": "Office Supplies",
    "Whiteboard Marker": "Stationery",
    "Eraser": "Stationery",
    "Ruler": "Stationery",
    "Clipboard": "Office Supplies",
    "Envelope": "Office Supplies",
    "Sticky Notes": "Office Supplies",
    "Binder Clip": "Office Supplies",
    "Paper Clip": "Office Supplies",
    "USB Drive": "Electronics",
    "Mouse": "Electronics",
    "Keyboard": "Electronics",
    "Headphones": "Electronics",
    "Charger": "Electronics",
    "Cable": "Accessories",
    "Bag": "Accessories",
    "Water Bottle": "Accessories",
    "Wallet": "Accessories",
    "ID Card Holder": "Accessories",
}

CATEGORIES = sorted(set(PRODUCT_CATALOG.values()))
