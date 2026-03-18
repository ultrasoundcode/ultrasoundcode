import sys
import re
from datetime import datetime, timedelta

def get_month_labels():
    # Today is the end of the graph
    today = datetime.now()
    labels = []
    # Go back 52 weeks
    for i in range(52, -1, -1):
        date = today - timedelta(weeks=i)
        if date.day <= 7: # Approximate start of a month
            month_name = date.strftime('%b')
            # Each column is ~16px (14.4 width + 1.6 spacing?)
            # Adjust x based on Platane/snk's 16px grid
            x = (52 - i) * 16
            labels.append((x, month_name))
    return labels

def customize_grid(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # 1. REMOVE ALL SNAKE ELEMENTS
    # Remove snake classes from CSS
    content = re.sub(r'\.s\{[^}]*\}', '', content)
    content = re.sub(r'\.s\.s\d+\{[^}]*\}', '', content)
    content = re.sub(r'@keyframes s\d+\{[^}]*\}', '', content)
    # Remove snake rects
    content = re.sub(r'<rect class="s s\d+"[^>]*/>', '', content)
    # Remove any extra CSS I added before
    content = re.sub(r'\n\.s\.s\d+\{[^}]*\}', '', content)

    # 2. ADD LABELS (MONTHS AND DAYS)
    # Styles for labels
    label_style = """
    <style>
        .label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 10px; fill: #768390; }
    </style>
    """
    
    # Month labels
    months_html = ""
    for x, name in get_month_labels():
        # Adjust x offset if needed (snk grid starts at x=0 or similar)
        months_html += f'<text x="{x}" y="-10" class="label">{name}</text>'
    
    # Weekday labels
    days_html = """
    <text x="-15" y="10" class="label">Mon</text>
    <text x="-15" y="42" class="label">Wed</text>
    <text x="-15" y="74" class="label">Fri</text>
    """
    
    # 3. CONSTRUCT FINAL SVG
    # Insert labels BEFORE the closing </svg>
    # Shift the whole grid down if necessary to make room for months? 
    # snk v3 has a viewBox. Let's adjust it to show labels.
    # Current viewBox is often "-16 -32 880 192"
    content = content.replace('viewBox="-16 -32 880 192"', 'viewBox="-25 -25 900 200"')
    
    insertion_point = content.find('</svg>')
    if insertion_point != -1:
        content = content[:insertion_point] + label_style + months_html + days_html + content[insertion_point:]

    with open(file_path, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    customize_grid(sys.argv[1])
