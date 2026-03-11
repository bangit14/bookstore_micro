#!/usr/bin/env python3
"""
Script to replace direct microservice calls with API Gateway proxy endpoints.
Replaces all http://localhost:PORT/... calls to /api/... in HTML templates.
"""

import os
import re
from pathlib import Path

# Mapping of service ports to API gateway endpoints
REPLACEMENTS = {
    # Manager service
    r'http://localhost:8005/dashboard/': '/api/manager/dashboard/',
    
    # Customer service
    r'http://localhost:8001/customers/': '/api/customers/',
    r'http://localhost:8001/customers/(\d+)/': r'/api/customers/\1/',
    
    # Book service
    r'http://localhost:8002/books/': '/api/books/',
    r'http://localhost:8002/books/(\d+)/': r'/api/books/\1/',
    
    # Cart service
    r'http://localhost:8003/carts/': '/api/carts/',
    r'http://localhost:8003/carts/(\d+)/': r'/api/carts/\1/',
    r'http://localhost:8003/cart-items/': '/api/cart-items/',
    r'http://localhost:8003/cart-items/(\d+)/': r'/api/cart-items/\1/',
    
    # Staff service
    r'http://localhost:8004/staff/': '/api/staff/',
    r'http://localhost:8004/staff/(\d+)/': r'/api/staff/\1/',
    
    # Catalog service
    r'http://localhost:8006/products/': '/api/products/',
    r'http://localhost:8006/products/(\d+)/': r'/api/products/\1/',
    
    # Order service
    r'http://localhost:8007/orders/': '/api/orders/',
    r'http://localhost:8007/orders/(\d+)/': r'/api/orders/\1/',
    
    # Ship service
    r'http://localhost:8008/shipments/': '/api/shipments/',
    r'http://localhost:8008/shipments/(\d+)/': r'/api/shipments/\1/',
    
    # Payment service
    r'http://localhost:8009/payments/': '/api/payments/',
    r'http://localhost:8009/payments/(\d+)/': r'/api/payments/\1/',
    
    # Review service
    r'http://localhost:8010/reviews/': '/api/reviews/',
    r'http://localhost:8010/reviews/(\d+)/': r'/api/reviews/\1/',
    
    # Recommender AI service
    r'http://localhost:8011/recommendations/(\d+)/': r'/api/recommendations/\1/',
}

def fix_template(filepath):
    """Replace API calls in a template file"""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Apply all replacements
    for pattern, replacement in REPLACEMENTS.items():
        # Count matches before replacement
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes.append(f"  - Replaced {len(matches)} occurrence(s) of {pattern}")
    
    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated {filepath.name}")
        for change in changes:
            print(change)
        return True
    else:
        print(f"  No changes needed")
        return False

def main():
    """Main function"""
    templates_dir = Path(__file__).parent / 'templates'
    
    if not templates_dir.exists():
        print(f"Error: Templates directory not found: {templates_dir}")
        return
    
    print(f"Scanning templates in: {templates_dir}\n")
    
    # Find all HTML files
    html_files = list(templates_dir.glob('*.html'))
    print(f"Found {len(html_files)} HTML files\n")
    
    updated_count = 0
    for html_file in html_files:
        if fix_template(html_file):
            updated_count += 1
        print()  # blank line between files
    
    print(f"\n{'='*60}")
    print(f"Summary: Updated {updated_count} of {len(html_files)} files")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
