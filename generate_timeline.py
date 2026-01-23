import re
import os
import sys
from bs4 import BeautifulSoup

KEY_FILE = 'doc/eng.key'
HTML_FILE = 'index.html'

def parse_key_file(filepath):
    print(f"Parsing key file: {filepath}")
    stages = []
    current_stage = None
    
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        # Read lines and filter empty ones
        lines = [line.strip() for line in f if line.strip()]
        
    for line in lines:
        if line.startswith('Stage'):
            if current_stage:
                stages.append(current_stage)
            current_stage = {'title': line, 'items': []}
        else:
            if current_stage:
                current_stage['items'].append(line)
            else:
                pass
                
    if current_stage:
        stages.append(current_stage)
    
    print(f"Found {len(stages)} stages.")
    return stages

def create_svg_content(stages):
    print("Creating SVG content...")
    CENTER_X = 500
    ITEM_GAP = 100
    STAGE_GAP = 300
    START_Y = 700 
    
    svg_content = []
    
    curr_y = START_Y
    total_items = 0
    
    for stage_idx, stage in enumerate(stages):
        stage_group = []
        
        # Stage Header
        stage_group.append(f'''
        <g id="stage-{stage_idx+1}" transform="translate(0, {curr_y})">
            <line x1="{CENTER_X}" y1="-50" x2="{CENTER_X+100}" y2="-50" stroke="#333" stroke-width="1" class="stage-line"></line>
            <text x="{CENTER_X}" y="-30" text-anchor="middle" class="font-sans text-stage">{stage['title'].upper()}</text>
            <line class="axis-line" x1="{CENTER_X}" y1="-20" x2="{CENTER_X}" y2="0" stroke="#FFF" stroke-width="1"></line>
        ''')
        
        local_y = 50
        for i, item_text in enumerate(stage['items']):
            total_items += 1
            is_right = (total_items % 2 == 0)
            side_class = "right-side" if is_right else "left-side"
            text_anchor = "start" if is_right else "end"
            
            line_x2 = CENTER_X + 50 if is_right else CENTER_X - 50
            text_x = CENTER_X + 60 if is_right else CENTER_X - 60
            
            is_bold = (i % 5 == 0) or (i == len(stage['items']) - 1)
            text_class = "text-item-bold" if is_bold else "text-item"
            circle_r = 4 if is_bold else 3
            
            item_html = f'''
            <g class="sequence-item {side_class}" data-index="{total_items}" data-y="{local_y}">
                <line x1="{CENTER_X}" y1="{local_y}" x2="{line_x2}" y2="{local_y}"></line>
                <circle cx="{CENTER_X}" cy="{local_y}" r="{circle_r}"></circle>
                <text x="{text_x}" y="{local_y + 8}" text-anchor="{text_anchor}" class="font-sans {text_class}">{item_text}</text>
            </g>
            '''
            stage_group.append(item_html)
            local_y += ITEM_GAP
            
        stage_group.append('</g>')
        svg_content.append('\n'.join(stage_group))
        
        curr_y += local_y + STAGE_GAP

    # Final Node
    final_y = curr_y - STAGE_GAP + 200
    total_items += 1
    
    final_node = f'''
        <g class="sequence-item center-side" transform="translate(0, {final_y})" data-index="{total_items}" data-y="{final_y}">
            <circle cx="{CENTER_X}" cy="0" r="60" fill="none" stroke="#FFF" stroke-width="0.5" class="breathe"></circle>
            <circle cx="{CENTER_X}" cy="0" r="50" fill="#111"></circle>
            <text x="{CENTER_X}" y="5" text-anchor="middle" fill="#FFF" class="font-serif text-item-bold" font-size="20">HAPPINESS</text>
            <text x="{CENTER_X}" y="45" text-anchor="middle" fill="#888" class="font-sans" font-size="14" letter-spacing="0.2em">NARRATIVE INTELLIGENCE</text>
        </g>
    '''
    svg_content.append(final_node)
    
    footer_y = final_y + 400
    
    return "\n".join(svg_content), footer_y

def main():
    try:
        stages = parse_key_file(KEY_FILE)
        if not stages:
            print("No stages parsed.")
            return

        new_timeline_content, footer_y = create_svg_content(stages)
        
        print(f"Reading HTML file: {HTML_FILE}")
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            
        svg = soup.find('svg', id='main-svg')
        if not svg:
            print("Error: Could not find svg with id 'main-svg'")
            return

        total_height = footer_y + 300
        svg['viewbox'] = f"0 0 1000 {total_height}"
        print(f"New viewBox height: {total_height}")
        
        axis_line = svg.find('line', id='axis-line')
        if axis_line:
            axis_line['x2'] = "500"
            axis_line['y2'] = str(total_height - 100)
        
        print("Removing old stages...")
        # Safe removal
        # Collect groups first
        groups_to_remove = []
        for g in svg.find_all('g'):
            try:
                g_id = g.get('id')
                if g_id and g_id.startswith('stage-'):
                    groups_to_remove.append(g)
            except Exception:
                pass
                
        for g in groups_to_remove:
            g.decompose()
        
        footer = svg.find('g', id='footer-group')
        if footer:
            footer.decompose()
        
        print("Appending new content...")
        new_soup = BeautifulSoup(new_timeline_content, 'html.parser')
        
        for element in new_soup.contents:
            if element.name:
               svg.append(element)
               
        # Footer
        footer_html = f'''
            <g id="footer-group" transform="translate(0, {footer_y})">
                <line x1="300" y1="0" x2="700" y2="0" stroke="url(#grad-gold)" stroke-width="1" opacity="0.6"></line>
                <text x="500" y="45" text-anchor="middle" fill="#555" font-size="11" class="font-sans footer-text" letter-spacing="0.15em">RYTUNYN 2026</text>
                <a href="mailto:rytunyn@rytunyn.com" class="footer-email">
                    <text x="500" y="75" text-anchor="middle" fill="#666" font-size="10" class="font-sans footer-text footer-link" letter-spacing="0.1em">rytunyn@rytunyn.com</text>
                </a>
                <line x1="420" y1="100" x2="580" y2="100" stroke="#333" stroke-width="1" opacity="0.4"></line>
            </g>
        '''
        footer_soup = BeautifulSoup(footer_html, 'html.parser')
        svg.append(footer_soup)

        print("Writing to file...")
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        print("Success.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
