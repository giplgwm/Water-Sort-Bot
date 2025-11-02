import cv2
import numpy as np

def find_tubes(image_path):
    """
    Find test tubes in the image - they are vertical rectangles (151x544 pixels).
    """
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold to isolate white regions
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_tubes = []
    
    print(f"Total contours found: {len(contours)}\n")
    
    for i, contour in enumerate(contours):
        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)
        
        # Look for vertical rectangles approximately 151 wide and 544 tall
        # Allow some tolerance (±10 pixels)
        width_ok = 140 <= w <= 165
        height_ok = 530 <= h <= 560
        
        if width_ok and height_ok:
            # Calculate aspect ratio (should be around 0.28 for tubes)
            aspect_ratio = w / h if h > 0 else 0
            
            # Extract the region of interest
            roi = binary[y:y+h, x:x+w]
            white_pixels = np.sum(roi == 255)
            total_pixels = w * h
            fill_percentage = (white_pixels / total_pixels) * 100
            
            print(f"✓ TUBE FOUND:")
            print(f"  Position: ({x}, {y})")
            print(f"  Size: {w} x {h} pixels")
            print(f"  Aspect ratio: {aspect_ratio:.2f}")
            print(f"  Fill: {fill_percentage:.1f}% white")
            print()
            
            detected_tubes.append({
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'center': (x + w // 2, y + h // 2),
                'top_center': (x + w // 2, y),  # Center of the top edge
                'fill_percentage': fill_percentage,
                'aspect_ratio': aspect_ratio
            })
    
    # Sort by Y position (top to bottom) then X position (left to right)
    detected_tubes.sort(key=lambda t: (t['y'], t['x']))
    
    return detected_tubes, img, binary


def visualize_tubes(image, tubes, output_path='result.jpg'):
    """
    Draw detected tubes on the image and save it.
    """
    result = image.copy()
    
    for i, tube in enumerate(tubes):
        x, y, w, h = tube['x'], tube['y'], tube['width'], tube['height']
        
        # Draw rectangle around the entire tube
        cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 3)
        
        # Draw a marker at the top center of the tube
        top_center = tube['top_center']
        cv2.circle(result, top_center, 8, (255, 0, 0), -1)
        
        # Add label
        cv2.putText(result, f"Tube {i+1}", (x, y - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.imwrite(output_path, result)
    return result


# Example usage
if __name__ == "__main__":
    image_path = "lvl8.png"
    
    # Find tubes
    tubes, original_img, binary_img = find_tubes(image_path)
    
    print(f"=== Found {len(tubes)} tubes ===\n")
    
    for i, tube in enumerate(tubes):
        print(f"Tube {i+1}:")
        print(f"  Position: ({tube['x']}, {tube['y']})")
        print(f"  Size: {tube['width']}x{tube['height']}")
        print(f"  Top center: {tube['top_center']}")
        print()
    
    # Visualize and save results
    if len(tubes) > 0:
        result = visualize_tubes(original_img, tubes, 'detected_tubes.jpg')
        print("Result saved to 'detected_tubes.jpg'")
    
    # Save binary image
    cv2.imwrite('binary.jpg', binary_img)