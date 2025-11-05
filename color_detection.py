import cv2
import numpy as np
import sys
from tube_detection import find_tubes


def detect_colors_in_tube(img, tube, index, scan_offset=30):
    """
    Scan a vertical line in the tube at scan_offset pixels from the right border.
    Returns a list of colors found from top to bottom.
    
    Args:
        img: Original image (BGR format)
        tube: Tube dictionary with position and dimensions
        scan_offset: Distance from the right border to scan (default 70px)
    
    Returns:
        List of dictionaries containing color info and positions
    """
    x, y, w, h = tube['x'], tube['y'], tube['width'], tube['height']

    # Calculate the x-position of the scan line (70px from right border)
    scan_x = x + w - scan_offset

    # Make sure scan_x is within bounds
    if scan_x < x or scan_x >= x + w:
        print(f"Warning: Scan line out of bounds for tube at ({x}, {y})")
        return []

    colors_found = []
    # Scan from top to bottom of the tube
    for scan_y in range(y + 68, y + h):
        # Get the pixel color at this position
        pixel = img[scan_y, scan_x]
        b, g, r = int(pixel[0]), int(pixel[1]), int(pixel[2])

        # Identify the color or empty space
        color_name = identify_color(r, g, b)

        # Group consecutive pixels of the same color
        if colors_found and colors_found[-1]['color'] == color_name:
            colors_found[-1]['end_y'] = scan_y
            colors_found[-1]['height'] += 1
        else:
            colors_found.append({
                'color': color_name,
                'rgb': (r, g, b),
                'start_y': scan_y,
                'end_y': scan_y,
                'height': 1,
                'scan_x': scan_x
            })
    return colors_found


def identify_color(r, g, b):
    """
    Identify the color name based on RGB values.
    Specifically tuned for this puzzle game.
    """

    if b == 255 and g == 255 and r == 255:
        return "white"

    # Dark Blue: RGB(58, 46, 196) - very high blue, low red and green
    # B should be > 150 and much greater than R and G
    if b == 196 and g == 46 and r == 58:
        return "blue"

    # Red (dark red): RGB(195, 40, 31) - high R, very low G and B
    if b == 31 and g == 40 and r == 195:
        return "red"

    # Pink: RGB(234, 94, 123) - high R, medium G and B
    if b == 123 and g == 94 and r == 234:
        return "pink"

    # Yellow: RGB(241, 217, 87) - high R and G, low B
    if b == 87 and g == 217 and r == 241:
        return "yellow"

    # Green: RGB(98, 214, 125) - very high G, lower R and B
    if b == 125 and g == 214 and r == 98:
        return "green"

    # Grey
    if b == 99 and g == 98 and r == 97:
        return "grey"

    # Light blue
    if b == 220 and g == 156 and r == 82:
        return "lightblue"

    #orange
    if b == 0 and g == 100 and r == 255:
        return "orange"

    #purple
    if b == 146 and g == 42 and r == 114:
        return "purple"

    #poop
    if b == 15 and g == 150 and r == 120:
        return "poop"

    # Check for black/dark (all values low)
    if b == 51 and g == 50 and r == 45:
        return "black"

    else:
        return "empty"

    return "unknown"


def analyze_all_tubes(image_path, scan_offset=30):
    """
    Analyze all tubes in the image and return color information.
    """
    # Find tubes using the tube_detection module
    tubes, img, binary = find_tubes(image_path)

    all_tube_colors = []

    for i, tube in enumerate(tubes):
        # print(f"\n=== Tube {i+1} at ({tube['x']}, {tube['y']}) ===")

        # Detect colors in this tube
        colors = detect_colors_in_tube(img, tube, i, scan_offset)

        # Filter out very small segments (likely noise) and background/empty at top and bottom
        significant_colors = []
        for c in colors:
            # Skip small segments (must be at least 22px tall to be a real color block)
            if c['height'] < 22:
                continue
            # Skip background and empty space (these are the tube walls and empty areas)
            # if c['color'] in ['background', 'empty']:
            #     continue
            significant_colors.append(c)

        print(f"Colors found (top to bottom):")
        for color_segment in significant_colors:
            print(
                f"  {color_segment['color']:10s} - "
                f"{color_segment['height']:3d}px tall - "
                f"RGB({color_segment['rgb'][0]:3d}, {color_segment['rgb'][1]:3d}, {color_segment['rgb'][2]:3d})"
            )

        all_tube_colors.append({
            'tube_index':
            i + 1,
            'tube_position': (tube['x'], tube['y']),
            'tube_height': tube['height'],  # CRITICAL: Actual tube capacity in pixels
            'colors':
            significant_colors,
            'top_color':
            significant_colors[0],
            'pour_color':
            significant_colors[1] if significant_colors[0]['color'] == 'empty'
            and len(significant_colors) > 1 else significant_colors[0]
        })

    return all_tube_colors, img
