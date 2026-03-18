import sys
import re

def customize_snake(file_path):
    with open(file_path, 'r') as f:
        content = f.read()

    # 1. Change colors to match GitHub's green theme
    # Snake color: #39d353 (active green)
    content = re.sub(r'--cs:[^;]+', '--cs:#39d353', content)
    
    # 2. Slow down animation (already done or to be done)
    match = re.search(r'(\d+)ms', content)
    if match:
        original_duration = int(match.group(1))
        # Keep it slow (multiply by 3)
        if original_duration < 20000: # avoid double multiplying if run twice
           new_duration = original_duration * 3
           content = content.replace(f'{original_duration}ms', f'{new_duration}ms')

    # 3. Force all snake segments to have the same size (14.4)
    # This ensures they look like the grid cubes
    content = re.sub(r'width="[0-9.]+" height="[0-9.]+" rx="[0-9.]+" ry="[0-9.]+"', 
                     'width="14.4" height="14.4" rx="4.5" ry="4.5"', content)

    # 4. Add segments s4, s5, s6 (Total 7: s0 to s6)
    
    # First: find the base keyframe animation s0
    # @keyframes s0{...}
    s0_match = re.search(r'@keyframes s0\{(.*?)\}', content, re.DOTALL)
    if s0_match:
        s0_keyframes = s0_match.group(1)
        
        # Determine the step percentage (offset between s0 and s1)
        # s1 starts at roughly 0.83% according to my previous grep
        # But we can calculate it: 100 / total_steps. 
        # For simplicity, we'll extract it from s1 if s1 exists.
        s1_match = re.search(r'@keyframes s1\{(\d+\.\d+)%', content)
        if s1_match:
             step_pct = float(s1_match.group(1))
        else:
             step_pct = 0.83 # Default fallback
             
        # Generate new keyframes s4, s5, s6
        for i in range(4, 7):
            offset = step_pct * i
            # Function to shift percentages in keyframe string
            def shift_pct(match):
                pct = float(match.group(1))
                new_pct = (pct + offset) % 100 # Keep within 0-100
                return f'{new_pct:.2f}%'
            
            new_keyframes = re.sub(r'(\d+(?:\.\d+)?)%', shift_pct, s0_keyframes)
            content += f'\n@keyframes s{i}{{{new_keyframes}}}'
            
            # Add CSS for new segment
            # We also need to set the initial transform correctly.
            # Usually it's transform:translate(Xpx, -16px) where X = i * 16
            x_offset = i * 16
            content += f'\n.s.s{i}{{transform:translate({x_offset}px,-16px);animation-name:s{i}}}'
            
            # Add the <rect> tag before the </svg>
            new_rect = f'<rect class="s s{i}" x="0.8" y="0.8" width="14.4" height="14.4" rx="4.5" ry="4.5"/>'
            content = content.replace('</svg>', f'{new_rect}</svg>')

    with open(file_path, 'w') as f:
        f.write(content)

if __name__ == "__main__":
    customize_snake(sys.argv[1])
