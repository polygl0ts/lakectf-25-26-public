#!/usr/bin/env python3
"""
WVG (Wireless Vector Graphics) Binary Parser
Parses WVG bitstream format according to TS 23.040 Annex G
"""

class BitStreamReader:
    """Helper class to read bits from a binary string"""
    def __init__(self, bitstring):
        self.bits = bitstring.replace(' ', '').replace('\n', '').replace(';', '')
        self.pos = 0
    
    def read(self, n):
        """Read n bits and return as integer"""
        if self.pos + n > len(self.bits):
            raise ValueError(f"Not enough bits: need {n}, have {len(self.bits) - self.pos}")
        value = int(self.bits[self.pos:self.pos + n], 2)
        self.pos += n
        return value
    
    def read_signed(self, n):
        """Read n bits as signed integer (two's complement)"""
        value = self.read(n)
        if value >= (1 << (n - 1)):
            value -= (1 << n)
        return value
    
    def peek(self, n):
        """Peek at next n bits without advancing position"""
        if self.pos + n > len(self.bits):
            return None
        return int(self.bits[self.pos:self.pos + n], 2)
    
    def remaining(self):
        """Return number of remaining bits"""
        return len(self.bits) - self.pos


class WVGParser:
    """Parser for WVG (Wireless Vector Graphics) binary format"""
    
    def __init__(self, bitstring):
        self.reader = BitStreamReader(bitstring)
        self.context = {}
        
    def parse(self):
        """Parse entire WVG file and return parse tree"""
        tree = {
            'header': self.parse_header(),
            'elements': []
        }
        
        # Parse elements
        num_elements = self.parse_number_of_elements()
        tree['num_elements'] = num_elements
        print(tree)
        for i in range(num_elements):
            element = self.parse_element(i)
            tree['elements'].append(element)
            print(element)
        return tree
    
    def parse_header(self):
        """Parse WVG standard header"""
        header = {}
        assert self.reader.read(1) == 1
        # General info
        header['version'] = self.reader.read(4)
        header['reserved'] = self.reader.read(1)
        assert header['reserved'] == 0
        
        # Color configuration
        header['color_scheme'] = self.reader.read(2)
        assert header['color_scheme'] == 0
        header['default_colors'] = self.reader.read(3)
        assert header['default_colors'] == 0

        # Element mask (8 bits)
        element_mask = []
        for i in range(8):
            element_mask.append(self.reader.read(1))
        header["more_elem_mask"] = self.reader.read(1)
        assert header["more_elem_mask"] == 0
        header['element_mask'] = element_mask
        
        # Calculate number of bits for element type
        num_types = sum(element_mask)
        if num_types <= 1:
            bits_for_element_type = 0
        elif num_types == 2:
            bits_for_element_type = 1
        elif num_types <= 4:
            bits_for_element_type = 2
        elif num_types <= 8:
            bits_for_element_type = 3
        else:
            bits_for_element_type = 4
        
        self.context['element_type_bits'] = bits_for_element_type
        self.context['element_mask'] = element_mask
        
        # Build element type mapping
        type_map = []
        type_names = ['local_envelope', 'polyline', 'circular_polyline', 'bezier_polyline', 
                      'simple_shape', 'reuse', 'group', 'animation']
        for i, enabled in enumerate(element_mask):
            if enabled:
                type_map.append(type_names[i])
        self.context['element_types'] = type_map
        
        # Attribute masks (4 bits)
        header['attribute_mask'] = self.reader.read(4)
        assert header["attribute_mask"] == 0
        # Generic parameters
        header['generic_params'] = {}
        header['generic_params']['flags'] = self.reader.read(3)
        assert header['generic_params']['flags'] == 1
        header['generic_params']['index_in_bits'] = self.reader.read(4)
        header['generic_params']['curve_offset_in_bits'] = self.reader.read(1)
        
        self.context['curve_offset_bits'] = 4 if header['generic_params']['curve_offset_in_bits'] == 0 else 5
        self.context['generic_params'] = header['generic_params']
        # Coordinate parameters (flat mode)
        coord_mode = self.reader.read(1)
        header['coord_mode'] = 'flat' if coord_mode == 0 else 'compact'
        assert header['coord_mode'] == 'flat'
        
        if coord_mode == 0:  # Flat
            header['flat_coords'] = self.parse_flat_coords()
        
        return header
    
    def parse_flat_coords(self):
        """Parse flat coordinate parameters"""
        coords = {}
        
        # Drawing width (16 bits)
        coords['width'] = self.reader.read(16)
        
        # Check if height differs from width
        height_differs = self.reader.read(1)
        if height_differs:
            coords['height'] = self.reader.read(16)
        else:
            coords['height'] = coords['width']
        
        # Coordinate encoding bits
        coords['max_x_bits'] = self.reader.read(4)
        coords['max_y_bits'] = self.reader.read(4)
        coords['xy_all_positive'] = self.reader.read(1)
        assert coords["xy_all_positive"] == 1
        coords['trans_xy_bits'] = self.reader.read(4)
        coords['num_points_bits'] = self.reader.read(4)
        coords['offset_x_bits_level1'] = self.reader.read(4)
        coords['offset_y_bits_level1'] = self.reader.read(4)
        coords['offset_x_bits_level2'] = self.reader.read(4)
        coords['offset_y_bits_level2'] = self.reader.read(4)
        
        # Store in context for later use
        self.context.update(coords)
        
        return coords
    
    def parse_number_of_elements(self):
        """Parse number of elements"""
        short_form = self.reader.read(1)
        if short_form == 0:
            return self.reader.read(7)
        else:
            return self.reader.read(15)
    
    def parse_element(self, index):
        """Parse a single element"""
        element = {'index': index}
        
        # Element type
        if self.context['element_type_bits'] > 0:
            type_code = self.reader.read(self.context['element_type_bits'])
            element['type_code'] = type_code
            element['type'] = self.context['element_types'][type_code]
        else:
            element['type_code'] = 0
            element['type'] = self.context['element_types'][0]
        
        # Parse based on type
        if element['type'] == 'polyline':
            element['data'] = self.parse_polyline()
        elif element['type'] == 'circular_polyline':
            element['data'] = self.parse_circular_polyline()
        elif element['type'] == 'reuse':
            element['data'] = self.parse_reuse()
        else:
            assert False, "not implemented"
            element['data'] = {'note': 'Type not fully implemented'}
        
        return element
    
    def parse_polyline(self):
        """Parse polyline element"""
        polyline = {}
        
        # Offset bit use
        polyline['offset_x_use'] = self.reader.read(1)
        polyline['offset_y_use'] = self.reader.read(1)
        
        # Number of points
        num_points = self.reader.read(self.context['num_points_bits'])
        polyline['num_points'] = num_points
        
        # First point
        first_point = self.parse_point()
        polyline['first_point'] = first_point
        
        # Subsequent points (as offsets)
        points = [first_point]
        for i in range(num_points):
            offset = self.parse_offset(polyline['offset_x_use'], polyline['offset_y_use'])
            point = {'x': points[-1]['x'] + offset['x'], 'y': points[-1]['y'] + offset['y']}
            points.append(point)
        
        polyline['points'] = points
        
        return polyline
    
    def parse_circular_polyline(self):
        """Parse circular polyline element"""
        circular = {}
        
        # Offset bit use
        circular['offset_x_use'] = self.reader.read(1)
        circular['offset_y_use'] = self.reader.read(1)
        
        # Curve hint
        circular['curve_hint'] = self.reader.read(1)
        
        # Number of points
        num_points = self.reader.read(self.context['num_points_bits'])
        circular['num_points'] = num_points
        
        # First point
        first_point = self.parse_point()
        circular['first_point'] = first_point
        
        # Parse curve offset 0
        curve_offset0 = self.parse_curve_offset(circular['curve_hint'])

        # Parse point 2
        point2 = self.parse_point()

        # Parse points with curve offsets
        points = [first_point,point2]
        curve_offsets = [curve_offset0]
        
        for i in range(num_points):
            # Parse curve offset
            curve_offset = self.parse_curve_offset(circular['curve_hint'])
            curve_offsets.append(curve_offset)
            
            # Parse next point
            offset = self.parse_offset(circular['offset_x_use'], circular['offset_y_use'])
            point = {'x': points[-1]['x'] + offset['x'], 'y': points[-1]['y'] + offset['y']}
            points.append(point)
        
        circular['points'] = points
        circular['curve_offsets'] = curve_offsets
        
        return circular
    
    def parse_curve_offset(self, curve_hint):
        """Parse curve offset value"""
        if curve_hint:
            # With hint: optional curve offset
            has_offset = self.reader.read(1)
            if has_offset:
                return self.reader.read_signed(self.context['curve_offset_bits'])
            else:
                return 0
        else:
            # Without hint: always present
            return self.reader.read_signed(self.context['curve_offset_bits'])
    
    def parse_reuse(self):
        """Parse reuse element"""
        reuse = {}
        
        # Element index
        index_bits = self.context['generic_params']['index_in_bits'] + 1
        reuse['element_index'] = self.reader.read(index_bits)
        
        # Transform
        reuse['transform'] = self.parse_transform()
        
        # End markers
        reuse['end_marker1'] = self.reader.read(2)
        assert reuse['end_marker1'] == 0
        return reuse
    
    def parse_transform(self):
        """Parse transformation"""
        transform = {}
        
        # TranslateX
        has_translate_x = self.reader.read(1)
        if has_translate_x:
            transform['translate_x'] = self.reader.read_signed(self.context['trans_xy_bits'])
        else:
            transform['translate_x'] = 0
        
        # TranslateY
        has_translate_y = self.reader.read(1)
        if has_translate_y:
            transform['translate_y'] = self.reader.read_signed(self.context['trans_xy_bits'])
        else:
            transform['translate_y'] = 0
        
        # Transform type (0 = translation only)
        transform['type'] = self.reader.read(1)
        assert transform['type'] == 0
        return transform
    
    def parse_point(self):
        """Parse absolute point coordinates"""
        x = self.reader.read(self.context['max_x_bits'])
        y = self.reader.read(self.context['max_y_bits'])
        return {'x': x, 'y': y}
    
    def parse_offset(self, offset_x_use, offset_y_use):
        """Parse offset (signed)"""
        x_bits = self.context['offset_x_bits_level2'] if offset_x_use else self.context['offset_x_bits_level1']
        y_bits = self.context['offset_y_bits_level2'] if offset_y_use else self.context['offset_y_bits_level1']
        
        x = self.reader.read_signed(x_bits)
        y = self.reader.read_signed(y_bits)
        
        return {'x': x, 'y': y}


def print_tree(tree, indent=0):
    """Print parse tree in a readable format"""
    prefix = "  " * indent
    
    if isinstance(tree, dict):
        for key, value in tree.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}:")
                print_tree(value, indent + 1)
            else:
                print(f"{prefix}{key}: {value}")
    elif isinstance(tree, list):
        for i, item in enumerate(tree):
            print(f"{prefix}[{i}]:")
            print_tree(item, indent + 1)
    else:
        print(f"{prefix}{tree}")


def main():
    """Main function to parse WVG file"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python wvg_parser.py <file_with_bitstream>")
        print("\nExample file content (remove comments after ; ):")
        print("10000 0 00 000 011010000 0000 001 0100 0 0 ...")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Read file and remove comments
    with open(filename, 'r') as f:
        bitstring = ""
        for line in f:
            # Remove comments (everything after ;)
            if ';' in line:
                line = line[:line.index(';')]
            bitstring += line.strip()
    bitstring = bitstring.replace(" ","")
    bitstring = int("800c8028004040081d6e666aa24029a44d3705bd037883f53071a732498a5992575544a24878144f61cd4a918a9007401d30022aa270b2e9f384f050974b0e7a9ccdc660ebae40f9658b3ae98004bba00ce935212aa425d402efa3dbe280a6351816d8644070c0",16)
    bitstring = bin(bitstring)[2:]
    print("=" * 80)
    print("WVG PARSER - Parsing Tree")
    print("=" * 80)
    print()
    
    try:
        parser = WVGParser(bitstring)
        tree = parser.parse()
        
        print_tree(tree)
        
        print()
        print("=" * 80)
        print(f"Parsing complete. Parsed {tree['num_elements']} elements.")
        print(f"Bits remaining: {parser.reader.remaining()}")
        print("=" * 80)
        display_wvg_tree(tree)
        print(bitstring)
        print(len(bitstring))
        if len (bitstring) % 8!= 0:
            bitstring += "0" * (8-(len(bitstring)%8))
        print(hex(int(bitstring,2)))
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

import math


def calculate_circular_arc(p1, p2, curve_offset_normalized):
    """
    Calculate SVG arc parameters for a circular arc segment.
    
    Args:
        p1: Start point {'x': x1, 'y': y1}
        p2: End point {'x': x2, 'y': y2}
        curve_offset_normalized: Normalized curve offset (-0.5 to 0.5)
    
    Returns:
        dict with arc parameters for SVG path
    """
    if curve_offset_normalized == 0:
        # Straight line
        return None
    
    x1, y1 = p1['x'], p1['y']
    x2, y2 = p2['x'], p2['y']
    
    # Calculate midpoint and baseline length
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    baseline_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    if baseline_length == 0:
        return None
    
    offset_distance = abs(curve_offset_normalized) * baseline_length
    
    # Calculate baseline direction vector
    dx = x2 - x1
    dy = y2 - y1
    
    # Calculate perpendicular direction
    # For "left side" when viewed from p1 to p2 direction:
    # Rotate the direction vector 90° counterclockwise: (dx, dy) -> (-dy, dx)
    # Positive offset = left side, Negative offset = right side
    if curve_offset_normalized > 0:
        # Left side: rotate 90° counterclockwise
        perp_x = -dy / baseline_length
        perp_y = dx / baseline_length
    else:
        # Right side: rotate 90° clockwise
        perp_x = dy / baseline_length
        perp_y = -dx / baseline_length
    
    # Calculate the point on the arc (offset from midpoint)
    arc_point_x = mid_x + perp_x * offset_distance
    arc_point_y = mid_y + perp_y * offset_distance
    
    # Calculate radius using the sagitta formula
    # For a circular arc, r² = (baseline/2)² + (r - h)²
    # where h is the sagitta (perpendicular distance from chord to arc)
    h = offset_distance
    r = (baseline_length**2 / 4 + h**2) / (2 * h)
    
    # Determine sweep direction based on which side the arc bulges
    # We need to check if we're going clockwise or counterclockwise around the arc
    # Cross product of (p1 to mid) and (mid to arc_point) tells us the direction
    cross = (mid_x - x1) * (arc_point_y - mid_y) - (mid_y - y1) * (arc_point_x - mid_x)
    sweep_flag = 1 if cross > 0 else 0

    
    # Large arc flag (1 if curve offset is close to ±0.5, indicating nearly a semicircle)
    large_arc_flag = 1 if abs(curve_offset_normalized) >= 0.4 else 0
    
    return {
        'radius': r,
        'sweep_flag': sweep_flag,
        'large_arc_flag': large_arc_flag
    }


def display_wvg_tree(tree, output_filename='output.svg'):
    """
    Display a parsed WVG tree as an SVG image.
    
    Args:
        tree: Parsed WVG tree from WVGParser
        output_filename: Output SVG filename
    """
    header = tree['header']
    elements = tree['elements']
    
    # Get canvas dimensions
    width = header['flat_coords']['width']
    height = header['flat_coords']['height']
    
    # Get curve offset bits for normalization
    curve_offset_bits = header['generic_params']['curve_offset_in_bits']
    curve_offset_max_value = (1 << (4 if curve_offset_bits == 0 else 5)) // 2 - 1
    
    # Start SVG
    svg_lines = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'  <rect width="{width}" height="{height}" fill="white"/>',
        f'  <!-- WVG Drawing with {len(elements)} elements -->'
    ]
    
    # Store elements for reuse
    element_paths = {}
    
    # Process each element
    for elem in elements:
        elem_type = elem['type']
        elem_index = elem['index']
        
        if elem_type == 'polyline':
            path_data = render_polyline(elem['data'])
            element_paths[elem_index] = path_data
            svg_lines.append(f'  <!-- Element {elem_index}: Polyline -->')
            svg_lines.append(f'  <path d="{path_data}" stroke="black" stroke-width="2" fill="none"/>')
        
        elif elem_type == 'circular_polyline':
            path_data = render_circular_polyline(elem['data'], curve_offset_max_value)
            element_paths[elem_index] = path_data
            svg_lines.append(f'  <!-- Element {elem_index}: Circular Polyline -->')
            svg_lines.append(f'  <path d="{path_data}" stroke="black" stroke-width="2" fill="none"/>')
        
        elif elem_type == 'reuse':
            reuse_data = elem['data']
            ref_index = reuse_data['element_index']
            transform = reuse_data['transform']
            
            if ref_index in element_paths:
                tx = transform['translate_x']
                ty = transform['translate_y']
                svg_lines.append(f'  <!-- Element {elem_index}: Reuse of Element {ref_index} -->')
                svg_lines.append(f'  <path d="{element_paths[ref_index]}" stroke="blue" stroke-width="2" fill="none" transform="translate({tx},{ty})"/>')
            else:
                svg_lines.append(f'  <!-- Element {elem_index}: Reuse reference {ref_index} not found -->')
    
    svg_lines.append('</svg>')
    
    # Write to file
    with open(output_filename, 'w') as f:
        f.write('\n'.join(svg_lines))
    
    print(f"SVG output written to: {output_filename}")
    return output_filename


def render_polyline(polyline_data):
    """Render a polyline as SVG path data"""
    points = polyline_data['points']
    
    if not points:
        return ""
    
    # Start with Move command
    path_parts = [f"M {points[0]['x']} {points[0]['y']}"]
    
    # Add Line commands for remaining points
    for point in points[1:]:
        path_parts.append(f"L {point['x']} {point['y']}")
    
    return " ".join(path_parts)


def render_circular_polyline(circular_data, curve_offset_max_value):
    """Render a circular polyline as SVG path data with arcs"""
    points = circular_data['points']
    curve_offsets = circular_data['curve_offsets']
    
    if not points:
        return ""
    
    # Start with Move command to first point
    path_parts = [f"M {points[0]['x']} {points[0]['y']}"]
    
    # Process each segment
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]
        
        # Get curve offset (normalized to -0.5 to 0.5 range)
        if i < len(curve_offsets):
            curve_offset_raw = curve_offsets[i]
            curve_offset_normalized = curve_offset_raw / curve_offset_max_value * 0.5
        else:
            curve_offset_normalized = 0
        
        # Calculate arc or use straight line
        arc_params = calculate_circular_arc(p1, p2, curve_offset_normalized)
        
        if arc_params is None:
            # Straight line
            path_parts.append(f"L {p2['x']} {p2['y']}")
        else:
            # Circular arc using SVG elliptical arc command
            # A rx ry x-axis-rotation large-arc-flag sweep-flag x y
            r = arc_params['radius']
            sweep = arc_params['sweep_flag']
            large = arc_params['large_arc_flag']
            path_parts.append(f"A {r} {r} 0 {large} {sweep} {p2['x']} {p2['y']}")
    
    return " ".join(path_parts)

if __name__ == '__main__':
    main()