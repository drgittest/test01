#!/usr/bin/env python3
"""
Manual baseline screenshot creation script.
This script creates baseline screenshots for visual testing,
including a mock modal screenshot for testing purposes.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests

class ManualBaselineCreator:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.baseline_dir = self.test_dir / "baseline"
        self.baseline_dir.mkdir(exist_ok=True)
        
    def create_mock_modal_screenshot(self):
        """Create a mock modal screenshot for baseline testing."""
        print("\n--- Creating Mock Modal Screenshot ---")
        
        try:
            # Create a 1920x1080 image with a modal overlay
            img = Image.new('RGB', (1920, 1080), color='#f3f4f6')  # Gray background
            
            # Create a modal overlay
            modal_width, modal_height = 500, 400
            modal_x = (1920 - modal_width) // 2
            modal_y = (1080 - modal_height) // 2
            
            # Draw modal background
            draw = ImageDraw.Draw(img)
            
            # Semi-transparent backdrop
            for y in range(1080):
                for x in range(1920):
                    if modal_x <= x <= modal_x + modal_width and modal_y <= y <= modal_y + modal_height:
                        continue
                    # Make background semi-transparent
                    r, g, b = img.getpixel((x, y))
                    img.putpixel((x, y), (r//2, g//2, b//2))
            
            # Draw modal box
            draw.rectangle([modal_x, modal_y, modal_x + modal_width, modal_y + modal_height], 
                         fill='white', outline='#d1d5db', width=2)
            
            # Add modal content
            try:
                # Try to use a system font
                font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
                font_medium = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
                font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Modal title
            draw.text((modal_x + 20, modal_y + 20), "Order Details", 
                     fill='#111827', font=font_large)
            
            # Close button (X)
            draw.text((modal_x + modal_width - 40, modal_y + 20), "×", 
                     fill='#6b7280', font=font_large)
            
            # Order details
            details = [
                ("Order ID:", "1"),
                ("Order Number:", "ORD-001"),
                ("Customer Name:", "John Doe"),
                ("Item:", "Product A"),
                ("Quantity:", "5"),
                ("Price:", "$100.00"),
                ("Status:", "pending"),
                ("Created At:", "2024-01-15"),
                ("Updated At:", "2024-01-15")
            ]
            
            y_offset = modal_y + 80
            for label, value in details:
                draw.text((modal_x + 20, y_offset), label, fill='#374151', font=font_medium)
                draw.text((modal_x + 200, y_offset), value, fill='#111827', font=font_medium)
                y_offset += 30
            
            # Close button
            button_y = modal_y + modal_height - 60
            draw.rectangle([modal_x + modal_width - 120, button_y, 
                          modal_x + modal_width - 20, button_y + 40], 
                         fill='#2563eb', outline='#1d4ed8')
            draw.text((modal_x + modal_width - 100, button_y + 10), "Close", 
                     fill='white', font=font_medium)
            
            # Save the mock modal screenshot
            filepath = self.baseline_dir / "expected_modal_open.png"
            img.save(filepath)
            print(f"✓ Mock modal screenshot saved: {filepath}")
            
            # Create mobile version
            mobile_img = Image.new('RGB', (375, 667), color='#f3f4f6')
            mobile_modal_width, mobile_modal_height = 320, 400
            mobile_modal_x = (375 - mobile_modal_width) // 2
            mobile_modal_y = (667 - mobile_modal_height) // 2
            
            # Draw mobile modal
            mobile_draw = ImageDraw.Draw(mobile_img)
            
            # Semi-transparent backdrop
            for y in range(667):
                for x in range(375):
                    if mobile_modal_x <= x <= mobile_modal_x + mobile_modal_width and mobile_modal_y <= y <= mobile_modal_y + mobile_modal_height:
                        continue
                    r, g, b = mobile_img.getpixel((x, y))
                    mobile_img.putpixel((x, y), (r//2, g//2, b//2))
            
            # Draw mobile modal box
            mobile_draw.rectangle([mobile_modal_x, mobile_modal_y, 
                                 mobile_modal_x + mobile_modal_width, mobile_modal_y + mobile_modal_height], 
                                fill='white', outline='#d1d5db', width=2)
            
            # Mobile modal content
            mobile_draw.text((mobile_modal_x + 15, mobile_modal_y + 15), "Order Details", 
                           fill='#111827', font=font_medium)
            
            # Close button (X)
            mobile_draw.text((mobile_modal_x + mobile_modal_width - 30, mobile_modal_y + 15), "×", 
                           fill='#6b7280', font=font_medium)
            
            # Mobile order details
            mobile_y_offset = mobile_modal_y + 60
            for label, value in details:
                mobile_draw.text((mobile_modal_x + 15, mobile_y_offset), label, 
                               fill='#374151', font=font_small)
                mobile_draw.text((mobile_modal_x + 150, mobile_y_offset), value, 
                               fill='#111827', font=font_small)
                mobile_y_offset += 25
            
            # Mobile close button
            mobile_button_y = mobile_modal_y + mobile_modal_height - 50
            mobile_draw.rectangle([mobile_modal_x + mobile_modal_width - 100, mobile_button_y, 
                                 mobile_modal_x + mobile_modal_width - 15, mobile_button_y + 35], 
                                fill='#2563eb', outline='#1d4ed8')
            mobile_draw.text((mobile_modal_x + mobile_modal_width - 80, mobile_button_y + 8), "Close", 
                           fill='white', font=font_small)
            
            # Save mobile mock modal
            mobile_filepath = self.baseline_dir / "expected_modal_open_mobile.png"
            mobile_img.save(mobile_filepath)
            print(f"✓ Mock mobile modal screenshot saved: {mobile_filepath}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to create mock modal screenshot: {e}")
            return False
    
    def update_documentation(self):
        """Update documentation to reflect the mock screenshots."""
        print("\n--- Updating Documentation ---")
        
        doc_content = """# Baseline Screenshots for Visual Testing

This directory contains baseline screenshots used for automated visual testing of the order modal functionality.

## Screenshots

### Desktop (1920x1080)
- `expected_orders_list.png` - Orders list page in normal state
- `expected_modal_open.png` - Mock modal window in open state with order details

### Mobile (375x667 - iPhone SE)
- `expected_orders_list_mobile.png` - Orders list page on mobile viewport
- `expected_modal_open_mobile.png` - Mock modal window on mobile viewport

## Expected Visual State

### Orders List Page
- Clean table layout with order data
- Responsive design that adapts to screen size
- Proper spacing and typography
- No modal visible initially

### Modal Window
- Centered modal with backdrop
- Order details displayed in structured format
- Close button (X) in top-right corner
- Edit button for navigation to edit page
- Proper focus management and keyboard navigation

## Usage

These baseline screenshots are used by the automated visual testing suite to:
1. Compare current visual state against expected state
2. Detect visual regressions
3. Ensure consistent appearance across different environments
4. Validate responsive design behavior

## Screenshot Types

### Real Screenshots
- `expected_orders_list.png` - Actual screenshot of orders list page
- `expected_orders_list_mobile.png` - Actual screenshot of orders list on mobile

### Mock Screenshots
- `expected_modal_open.png` - Mock modal for testing (created manually)
- `expected_modal_open_mobile.png` - Mock mobile modal for testing

## Regenerating Baselines

To regenerate these baseline screenshots:

```bash
cd tests/visual
python create_baseline_screenshots_simple.py  # For real screenshots
python create_manual_baseline.py              # For mock screenshots
```

## Notes

- Real screenshots are taken in headless Chrome with consistent settings
- Mock screenshots are created programmatically for testing purposes
- Window size is fixed at 1920x1080 for desktop and 375x667 for mobile
- JavaScript is enabled for proper modal functionality
- Screenshots include the full page content for comprehensive comparison
"""
        
        doc_path = self.baseline_dir / "README.md"
        with open(doc_path, 'w') as f:
            f.write(doc_content)
        
        print("✓ Documentation updated")
        return True
    
    def run_all(self):
        """Run all manual baseline creation tasks."""
        print("🎨 Creating Manual Baseline Screenshots")
        print("=" * 40)
        
        success = True
        success &= self.create_mock_modal_screenshot()
        success &= self.update_documentation()
        
        if success:
            print("\n🎉 Manual baseline screenshots created successfully!")
            print(f"📁 Baseline files saved in: {self.baseline_dir}")
            print("\n📋 Next steps:")
            print("1. Review the mock modal screenshots")
            print("2. Run automated visual tests: python run_tests.py")
            print("3. Update baselines if needed after design changes")
        else:
            print("\n❌ Some manual baseline screenshots failed to create!")
            print("Check the error messages above.")
        
        return success

def main():
    """Main function to run manual baseline creation."""
    creator = ManualBaselineCreator()
    success = creator.run_all()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 