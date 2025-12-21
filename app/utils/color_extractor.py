"""
Color extraction utility for background images.
Extracts dominant colors from images and generates suitable text/accent colors.
"""
from PIL import Image
import colorsys
from collections import Counter


def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color code."""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def get_luminance(rgb):
    """Calculate relative luminance of a color (0=black, 1=white)."""
    r, g, b = [x / 255.0 for x in rgb]
    # Apply gamma correction
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_complementary_color(rgb):
    """Get a complementary accent color based on the dominant color."""
    h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
    # Shift hue by 180 degrees for complementary color
    h = (h + 0.5) % 1.0
    # Boost saturation and value for accent
    s = min(s * 1.3, 1.0)
    v = min(v * 1.2, 1.0)
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def extract_colors_from_image(image_path, num_colors=5):
    """
    Extract dominant colors from an image and return suitable color scheme.
    
    Args:
        image_path: Path to the image file
        num_colors: Number of dominant colors to analyze
    
    Returns:
        dict: {
            'bg_color': hex color for background,
            'text_color': hex color for text (high contrast with bg),
            'accent_color': hex color for accents/highlights
        }
    """
    # Open and resize image for faster processing
    img = Image.open(image_path)
    img = img.convert('RGB')
    img = img.resize((150, 150), Image.Resampling.LANCZOS)
    
    # Get all pixels
    pixels = list(img.getdata())
    
    # Count color frequencies
    color_counts = Counter(pixels)
    dominant_colors = color_counts.most_common(num_colors)
    
    # Get the most dominant color for background
    bg_color = dominant_colors[0][0]
    bg_luminance = get_luminance(bg_color)
    
    # Determine text color based on background luminance
    # Use WCAG contrast guidelines
    if bg_luminance > 0.5:
        # Light background -> dark text
        text_color = (30, 30, 40)  # Very dark blue-gray
    else:
        # Dark background -> light text
        text_color = (226, 232, 240)  # Light gray
    
    # Get complementary color for accent
    accent_color = get_complementary_color(bg_color)
    
    # Ensure accent has good contrast
    accent_luminance = get_luminance(accent_color)
    if abs(accent_luminance - bg_luminance) < 0.3:
        # Not enough contrast, adjust accent
        if bg_luminance > 0.5:
            # Darken accent for light backgrounds
            accent_color = tuple(int(c * 0.6) for c in accent_color)
        else:
            # Brighten accent for dark backgrounds
            accent_color = tuple(min(int(c * 1.4), 255) for c in accent_color)
    
    return {
        'bg_color': rgb_to_hex(bg_color),
        'text_color': rgb_to_hex(text_color),
        'accent_color': rgb_to_hex(accent_color)
    }
