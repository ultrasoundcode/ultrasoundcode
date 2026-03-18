import sys
import re

def customize_snake(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # 1. Slow down animation
    match = re.search(r'(\d+)ms', content)
    if match:
        original_duration = int(match.group(1))
        # Multiply by 3 for slow motion
        if original_duration < 20000:
           new_duration = original_duration * 3
           content = content.replace(f'{original_duration}ms', f'{new_duration}ms')

    # 2. Find grid size
    grid_size_match = re.search(r'\.c\{[^}]*width:(\d+)px', content)
    if grid_size_match:
        target_size = grid_size_match.group(1)
        target_rx = str(float(target_size) * 0.3)
    else:
        target_size = "12"
        target_rx = "2"

    # 3. Fix sizes of all snake segments - Use \g<1> to avoid ambiguity with numbers
    content = re.sub(r'(<rect class="s s\d+"[^>]*width=")[0-9.]+"', r'\g<1>' + target_size + '"', content)
    content = re.sub(r'(<rect class="s s\d+"[^>]*height=")[0-9.]+"', r'\g<1>' + target_size + '"', content)
    content = re.sub(r'(<rect class="s s\d+"[^>]*rx=")[0-9.]+"', r'\g<1>' + target_rx + '"', content)
    content = re.sub(r'(<rect class="s s\d+"[^>]*ry=")[0-9.]+"', r'\g<1>' + target_rx + '"', content)

    # 4. Add segments s4, s5, s6
    s0_match = re.search(r'@keyframes s0\{(.*?)\}', content, re.DOTALL)
    style_end_match = re.search(r'</style>', content)
    svg_end_match = re.search(r'</svg>', content)
    
    if s0_match and style_end_match and svg_end_match:
        s0_keyframes_body = s0_match.group(1)
        style_end_pos = style_end_match.start()
        
        s1_key_match = re.search(r'@keyframes s1\{(\d+\.\d+)%', content)
        step_pct = float(s1_key_match.group(1)) if s1_key_match else 0.83
        
        new_css = ""
        new_rects = ""
        for i in range(4, 7):
            offset = step_pct * i
            def shift_pct(match):
                pct = float(match.group(1))
                new_pct = (pct + offset) % 100
                return f'{new_pct:.2f}%'
            
            shifted_keyframes = re.sub(r'(\d+(?:\.\d+)?)%', shift_pct, s0_keyframes_body)
            new_css += f'\n@keyframes s{i}{{{shifted_keyframes}}}'
            x_offset = i * 16
            new_css += f'\n.s.s{i}{{transform:translate({x_offset}px,-16px);animation-name:s{i}}}'
            new_rects += f'<rect class="s s{i}" x="0.8" y="0.8" width="{target_size}" height="{target_size}" rx="{target_rx}" ry="{target_rx}"/>'
        
        content = content[:style_end_pos] + new_css + content[style_end_pos:]
        svg_end_match = re.search(r'</svg>', content)
        svg_end_pos = svg_end_match.start()
        content = content[:svg_end_pos] + new_rects + content[svg_end_pos:]

    with open(file_path, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    customize_snake(sys.argv[1])
