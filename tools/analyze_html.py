#!/usr/bin/env python3
"""
HTML Analyzer Tool

This script helps analyze the HTML structure of theater websites to assist
with developing and debugging the parsers.

Usage:
    python analyze_html.py <fixture_path> [<element_selector>]

Example:
    python analyze_html.py ../tests/fixtures/donmar_actual.html .show-item
"""

import sys
import os
from pathlib import Path
import re
from bs4 import BeautifulSoup

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def find_show_elements(soup):
    """
    Look for HTML elements that might contain show information.
    
    Args:
        soup: BeautifulSoup object of the parsed HTML
        
    Returns:
        List of potential show container elements with their selectors
    """
    potential_elements = []
    
    # Common class patterns for show containers
    show_patterns = [
        r'show[-_]item', r'show[-_]card', r'production[-_]card',
        r'event[-_]item', r'whats[-_]on[-_]item', r'performance',
        r'production', r'c-event-card'
    ]
    
    # Find all elements with classes matching our patterns
    for element in soup.find_all(class_=True):
        if not element.get('class'):
            continue
            
        classes = ' '.join(element.get('class'))
        for pattern in show_patterns:
            if re.search(pattern, classes, re.IGNORECASE):
                # Check if this element has useful child elements
                has_title = element.find(string=re.compile(r'[A-Za-z0-9]{5,}'))
                has_link = element.find('a')
                has_h_tag = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                
                if has_title and (has_link or has_h_tag):
                    selector = f"{element.name}.{'.'.join(element.get('class'))}"
                    potential_elements.append((element, selector))
                    break
    
    return potential_elements


def analyze_element(element, selector):
    """
    Analyze a potential show element to identify its structure.
    
    Args:
        element: BeautifulSoup element
        selector: CSS selector for the element
    """
    print(f"\nAnalyzing element with selector: {selector}")
    
    # Find potential title elements
    title_elements = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
    print("\nPotential title elements:")
    for i, title_elem in enumerate(title_elements):
        text = title_elem.get_text(strip=True)
        if len(text) > 50:
            text = text[:50] + "..."
        
        classes = ' '.join(title_elem.get('class', []))
        print(f"  {i+1}. <{title_elem.name}> class='{classes}' - {text}")
    
    # Find potential link elements
    link_elements = element.find_all('a')
    print("\nPotential link elements:")
    for i, link_elem in enumerate(link_elements):
        href = link_elem.get('href', '')
        if len(href) > 50:
            href = href[:50] + "..."
        
        text = link_elem.get_text(strip=True)
        if len(text) > 50:
            text = text[:50] + "..."
            
        classes = ' '.join(link_elem.get('class', []))
        print(f"  {i+1}. <a> class='{classes}' href='{href}' - {text}")
    
    # Find potential date elements
    date_patterns = [
        r'\d{1,2}\s+\w+\s+\d{4}',  # 1 June 2025
        r'\w+\s+\d{1,2},?\s+\d{4}',  # June 1, 2025
        r'\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}',  # 01/06/2025
        r'\d{4}-\d{2}-\d{2}'  # 2025-06-01
    ]
    
    print("\nPotential date elements:")
    date_count = 0
    for elem in element.find_all(string=True):
        text = elem.strip()
        if not text:
            continue
            
        parent = elem.parent
        
        for pattern in date_patterns:
            if re.search(pattern, text):
                parent_classes = ' '.join(parent.get('class', []))
                if len(text) > 50:
                    text = text[:50] + "..."
                print(f"  {date_count+1}. <{parent.name}> class='{parent_classes}' - {text}")
                date_count += 1
                break
    
    if date_count == 0:
        print("  No obvious date elements found")
    
    # Find potential description elements
    print("\nPotential description elements:")
    desc_count = 0
    for elem in element.find_all(['p', 'div']):
        text = elem.get_text(strip=True)
        if len(text) > 20:  # Probably a description if it has substantial text
            classes = ' '.join(elem.get('class', []))
            desc = text[:100] + "..." if len(text) > 100 else text
            print(f"  {desc_count+1}. <{elem.name}> class='{classes}' - {desc}")
            desc_count += 1
            
            if desc_count >= 3:  # Limit to 3 to avoid overwhelming output
                break
    
    if desc_count == 0:
        print("  No obvious description elements found")
    
    # Find potential price elements
    price_patterns = [
        r'£\d+',  # £20
        r'\$\d+',  # $20
        r'price', r'ticket', r'cost',  # Price-related words
        r'from \d+'  # "from 20"
    ]
    
    print("\nPotential price elements:")
    price_count = 0
    for elem in element.find_all(string=True):
        text = elem.strip().lower()
        if not text:
            continue
            
        parent = elem.parent
        
        for pattern in price_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                parent_classes = ' '.join(parent.get('class', []))
                print(f"  {price_count+1}. <{parent.name}> class='{parent_classes}' - {elem.strip()}")
                price_count += 1
                break
                
            if price_count >= 3:  # Limit to 3
                break
    
    if price_count == 0:
        print("  No obvious price elements found")


def analyze_html(html_path, selector=None):
    """
    Analyze HTML structure to help with developing parsers.
    
    Args:
        html_path: Path to the HTML file
        selector: CSS selector to find specific elements (optional)
    """
    print(f"Analyzing HTML file: {html_path}")
    
    # Read the HTML file
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Print file size
    print(f"File size: {len(html_content)} bytes")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Extract page title
    title = soup.title.string if soup.title else "No title found"
    print(f"\nPage title: {title}")
    
    if selector:
        # Find elements matching the selector
        elements = soup.select(selector)
        print(f"\nFound {len(elements)} elements matching selector: {selector}")
        
        if elements:
            # Analyze the first matching element
            analyze_element(elements[0], selector)
        else:
            print("\nNo elements found with that selector. Looking for similar elements...")
            
            # Try to find potential show elements
            potential_elements = find_show_elements(soup)
            
            if potential_elements:
                print(f"\nFound {len(potential_elements)} potential show elements:")
                for i, (element, element_selector) in enumerate(potential_elements[:5]):  # Limit to 5
                    title_text = "Unknown Title"
                    for title_elem in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                        title_text = title_elem.get_text(strip=True)
                        break
                    
                    print(f"\n{i+1}. {element_selector} - '{title_text}'")
                    
                    # Show a bit of HTML for context
                    html_snippet = str(element)
                    if len(html_snippet) > 500:
                        html_snippet = html_snippet[:500] + "... (truncated)"
                    
                    print(f"HTML snippet: {html_snippet}")
                
                # Ask if user wants to analyze one of these elements
                print("\nTo analyze one of these elements, run the script again with the element's selector.")
            else:
                print("\nNo potential show elements found.")
    else:
        # No selector provided, try to find potential show elements
        print("\nLooking for potential show elements...")
        potential_elements = find_show_elements(soup)
        
        if potential_elements:
            print(f"\nFound {len(potential_elements)} potential show elements:")
            for i, (element, element_selector) in enumerate(potential_elements[:10]):  # Limit to 10
                title_text = "Unknown Title"
                for title_elem in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    title_text = title_elem.get_text(strip=True)
                    break
                
                print(f"{i+1}. {element_selector} - '{title_text}'")
            
            print("\nTo analyze one of these elements, run the script again with the element's selector.")
        else:
            print("\nNo potential show elements found. Check if the HTML contains the expected content.")
            
            # Look for any content patterns that might be useful
            print("\nExamining page structure for clues:")
            main_content = soup.find(['main', 'div#content', 'div#main', 'div.content', 'div.main'])
            
            if main_content:
                print(f"Found main content area: <{main_content.name}> class='{' '.join(main_content.get('class', []))}'")
                
                # Find headings in the main content
                headings = main_content.find_all(['h1', 'h2', 'h3'])
                if headings:
                    print("\nMain headings in content area:")
                    for i, h in enumerate(headings[:5]):
                        print(f"  {i+1}. <{h.name}> - {h.get_text(strip=True)}")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <fixture_path> [<element_selector>]")
        sys.exit(1)
    
    html_path = sys.argv[1]
    selector = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        analyze_html(html_path, selector)
    except Exception as e:
        print(f"Error analyzing HTML: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()