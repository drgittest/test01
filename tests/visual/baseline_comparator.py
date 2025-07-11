#!/usr/bin/env python3
"""
Baseline Comparison System
Advanced image comparison and difference analysis for visual regression testing.
"""

import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from PIL import Image, ImageChops, ImageDraw, ImageFont
import numpy as np


class BaselineComparator:
    """Advanced baseline comparison with image analysis and difference highlighting."""
    
    def __init__(self, baseline_dir: Path = None):
        self.baseline_dir = baseline_dir or Path(__file__).parent / "baseline"
        self.screenshots_dir = Path(__file__).parent / "screenshots"
        self.diff_dir = Path(__file__).parent / "diff"
        self.reports_dir = Path(__file__).parent / "reports"
        
        # Create directories
        self.diff_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Similarity thresholds for different page types
        self.similarity_thresholds = {
            "login": 98.0,
            "register": 98.0,
            "orders": 95.0,  # May have dynamic content
            "order_create": 97.0,
            "order_edit": 95.0,  # May have pre-populated data
            "modal": 95.0,  # May have dynamic content
            "ui_components": 97.0,
            "default": 95.0
        }
        
    def calculate_image_hash(self, image_path: Path) -> str:
        """Calculate hash of an image file."""
        try:
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"⚠️ Could not calculate hash for {image_path}: {e}")
            return ""
    
    def compare_images_advanced(self, expected_path: Path, actual_path: Path, 
                              diff_path: Path = None, threshold: float = 95.0) -> Dict:
        """Advanced image comparison with detailed analysis."""
        comparison_result = {
            "expected_path": str(expected_path),
            "actual_path": str(actual_path),
            "diff_path": str(diff_path) if diff_path else None,
            "threshold": threshold,
            "compared_at": datetime.now().isoformat(),
            "similarity_percentage": 0.0,
            "passed": False,
            "error": None,
            "analysis": {}
        }
        
        try:
            # Check if files exist
            if not expected_path.exists():
                comparison_result["error"] = f"Expected image not found: {expected_path}"
                return comparison_result
            
            if not actual_path.exists():
                comparison_result["error"] = f"Actual image not found: {actual_path}"
                return comparison_result
            
            # Load images
            expected = Image.open(expected_path)
            actual = Image.open(actual_path)
            
            # Basic info
            comparison_result["analysis"]["expected_size"] = expected.size
            comparison_result["analysis"]["actual_size"] = actual.size
            comparison_result["analysis"]["expected_mode"] = expected.mode
            comparison_result["analysis"]["actual_mode"] = actual.mode
            
            # Size comparison
            if expected.size != actual.size:
                comparison_result["error"] = f"Image sizes don't match: {expected.size} vs {actual.size}"
                # Try to resize for comparison
                actual = actual.resize(expected.size, Image.Resampling.LANCZOS)
                comparison_result["analysis"]["resized_actual"] = True
            else:
                comparison_result["analysis"]["resized_actual"] = False
            
            # Convert to same mode if needed
            if expected.mode != actual.mode:
                if expected.mode == 'RGBA':
                    actual = actual.convert('RGBA')
                elif expected.mode == 'RGB':
                    actual = actual.convert('RGB')
            
            # Calculate difference
            diff = ImageChops.difference(expected, actual)
            
            # Calculate similarity using multiple methods
            similarity_methods = {}
            
            # Method 1: Pixel-wise comparison
            similarity_methods["pixel_wise"] = self._calculate_pixel_similarity(expected, actual)
            
            # Method 2: Histogram comparison
            similarity_methods["histogram"] = self._calculate_histogram_similarity(expected, actual)
            
            # Method 3: Structural similarity (simplified)
            similarity_methods["structural"] = self._calculate_structural_similarity(expected, actual)
            
            # Use the most conservative similarity score
            similarity_percentage = min(similarity_methods.values())
            comparison_result["similarity_percentage"] = similarity_percentage
            comparison_result["analysis"]["similarity_methods"] = similarity_methods
            
            # Determine if test passed
            comparison_result["passed"] = similarity_percentage >= threshold
            
            # Generate difference image if requested and there are differences
            if diff_path and similarity_percentage < threshold:
                self._generate_difference_image(expected, actual, diff, diff_path, comparison_result)
            
            # Additional analysis
            comparison_result["analysis"]["difference_bbox"] = diff.getbbox()
            comparison_result["analysis"]["has_differences"] = diff.getbbox() is not None
            
            return comparison_result
            
        except Exception as e:
            comparison_result["error"] = f"Image comparison failed: {str(e)}"
            return comparison_result
    
    def _calculate_pixel_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """Calculate pixel-wise similarity percentage."""
        try:
            # Convert to numpy arrays
            arr1 = np.array(img1)
            arr2 = np.array(img2)
            
            # Calculate absolute difference
            diff = np.abs(arr1.astype(np.float32) - arr2.astype(np.float32))
            
            # Calculate similarity (0 = identical, 255 = completely different)
            mean_diff = np.mean(diff)
            similarity = (255 - mean_diff) / 255 * 100
            
            return max(0.0, min(100.0, similarity))
            
        except Exception as e:
            print(f"⚠️ Pixel similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_histogram_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """Calculate histogram similarity percentage."""
        try:
            # Convert to RGB if necessary
            if img1.mode != 'RGB':
                img1 = img1.convert('RGB')
            if img2.mode != 'RGB':
                img2 = img2.convert('RGB')
            
            # Calculate histograms
            hist1 = img1.histogram()
            hist2 = img2.histogram()
            
            # Calculate correlation coefficient
            correlation = np.corrcoef(hist1, hist2)[0, 1]
            
            # Convert to percentage (handle NaN case)
            if np.isnan(correlation):
                return 100.0 if hist1 == hist2 else 0.0
            
            return max(0.0, min(100.0, correlation * 100))
            
        except Exception as e:
            print(f"⚠️ Histogram similarity calculation failed: {e}")
            return 0.0
    
    def _calculate_structural_similarity(self, img1: Image.Image, img2: Image.Image) -> float:
        """Calculate structural similarity (simplified SSIM)."""
        try:
            # Convert to grayscale
            gray1 = img1.convert('L')
            gray2 = img2.convert('L')
            
            # Convert to numpy arrays
            arr1 = np.array(gray1, dtype=np.float32)
            arr2 = np.array(gray2, dtype=np.float32)
            
            # Calculate means
            mu1 = np.mean(arr1)
            mu2 = np.mean(arr2)
            
            # Calculate variances and covariance
            var1 = np.var(arr1)
            var2 = np.var(arr2)
            cov = np.mean((arr1 - mu1) * (arr2 - mu2))
            
            # SSIM constants
            c1 = 0.01 ** 2
            c2 = 0.03 ** 2
            
            # Calculate SSIM
            ssim = ((2 * mu1 * mu2 + c1) * (2 * cov + c2)) / ((mu1**2 + mu2**2 + c1) * (var1 + var2 + c2))
            
            return max(0.0, min(100.0, ssim * 100))
            
        except Exception as e:
            print(f"⚠️ Structural similarity calculation failed: {e}")
            return 0.0
    
    def _generate_difference_image(self, expected: Image.Image, actual: Image.Image, 
                                  diff: Image.Image, diff_path: Path, comparison_result: Dict):
        """Generate a comprehensive difference image with highlights."""
        try:
            # Create a side-by-side comparison image
            width, height = expected.size
            comparison_width = width * 3 + 40  # 3 images + padding
            comparison_height = height + 80     # Extra space for labels
            
            # Create comparison image
            comparison = Image.new('RGB', (comparison_width, comparison_height), 'white')
            
            # Paste images
            comparison.paste(expected, (10, 40))
            comparison.paste(actual, (width + 20, 40))
            
            # Create highlighted difference
            diff_highlighted = self._highlight_differences(expected, actual, diff)
            comparison.paste(diff_highlighted, (width * 2 + 30, 40))
            
            # Add labels
            try:
                # Try to load a font
                font = ImageFont.load_default()
            except:
                font = None
            
            draw = ImageDraw.Draw(comparison)
            
            # Add text labels
            labels = ["Expected", "Actual", "Differences"]
            for i, label in enumerate(labels):
                x = 10 + i * (width + 10)
                draw.text((x, 10), label, fill='black', font=font)
            
            # Add similarity score
            similarity_text = f"Similarity: {comparison_result['similarity_percentage']:.2f}%"
            draw.text((10, comparison_height - 30), similarity_text, fill='red', font=font)
            
            # Add threshold info
            threshold_text = f"Threshold: {comparison_result['threshold']:.2f}%"
            draw.text((10, comparison_height - 15), threshold_text, fill='blue', font=font)
            
            # Save comparison image
            comparison.save(diff_path)
            
            # Update comparison result
            comparison_result["analysis"]["diff_image_generated"] = True
            comparison_result["analysis"]["diff_image_size"] = comparison.size
            
        except Exception as e:
            print(f"⚠️ Could not generate difference image: {e}")
            comparison_result["analysis"]["diff_image_generated"] = False
            comparison_result["analysis"]["diff_generation_error"] = str(e)
    
    def _highlight_differences(self, expected: Image.Image, actual: Image.Image, 
                             diff: Image.Image) -> Image.Image:
        """Create an image with differences highlighted in red."""
        try:
            # Convert to RGB if necessary
            if actual.mode != 'RGB':
                actual = actual.convert('RGB')
            
            # Create a copy of the actual image
            highlighted = actual.copy()
            
            # Convert difference to numpy array
            diff_array = np.array(diff)
            
            # Find pixels with differences (non-zero values)
            if len(diff_array.shape) == 3:
                # Color image - sum across channels
                diff_mask = np.sum(diff_array, axis=2) > 0
            else:
                # Grayscale image
                diff_mask = diff_array > 0
            
            # Convert highlighted image to numpy array
            highlighted_array = np.array(highlighted)
            
            # Highlight differences in red
            highlighted_array[diff_mask] = [255, 0, 0]  # Red
            
            # Convert back to PIL Image
            return Image.fromarray(highlighted_array)
            
        except Exception as e:
            print(f"⚠️ Could not highlight differences: {e}")
            return actual
    
    def determine_threshold(self, image_path: Path) -> float:
        """Determine appropriate similarity threshold based on image type."""
        filename = image_path.name.lower()
        
        for page_type, threshold in self.similarity_thresholds.items():
            if page_type in filename:
                return threshold
        
        return self.similarity_thresholds["default"]
    
    def compare_all_screenshots(self, screenshots_dir: Path = None) -> Dict:
        """Compare all screenshots with their corresponding baselines."""
        screenshots_dir = screenshots_dir or self.screenshots_dir
        
        comparison_report = {
            "compared_at": datetime.now().isoformat(),
            "total_comparisons": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "comparisons": {},
            "summary": {}
        }
        
        # Find all screenshot files
        screenshot_files = list(screenshots_dir.glob("*.png"))
        
        if not screenshot_files:
            comparison_report["error"] = "No screenshot files found"
            return comparison_report
        
        print(f"🔍 Comparing {len(screenshot_files)} screenshots with baselines...")
        
        for screenshot_path in screenshot_files:
            # Find corresponding baseline
            baseline_path = self.find_baseline_for_screenshot(screenshot_path)
            
            if not baseline_path:
                print(f"⚠️ No baseline found for {screenshot_path.name}")
                continue
            
            # Determine threshold
            threshold = self.determine_threshold(screenshot_path)
            
            # Generate diff path
            diff_path = self.diff_dir / f"diff_{screenshot_path.name}"
            
            # Compare images
            result = self.compare_images_advanced(baseline_path, screenshot_path, diff_path, threshold)
            
            comparison_report["comparisons"][screenshot_path.name] = result
            comparison_report["total_comparisons"] += 1
            
            if result["error"]:
                comparison_report["errors"] += 1
                print(f"✗ {screenshot_path.name}: {result['error']}")
            elif result["passed"]:
                comparison_report["passed"] += 1
                print(f"✓ {screenshot_path.name}: {result['similarity_percentage']:.2f}% (threshold: {threshold}%)")
            else:
                comparison_report["failed"] += 1
                print(f"✗ {screenshot_path.name}: {result['similarity_percentage']:.2f}% (threshold: {threshold}%)")
        
        # Generate summary
        if comparison_report["total_comparisons"] > 0:
            comparison_report["summary"]["pass_rate"] = (comparison_report["passed"] / comparison_report["total_comparisons"]) * 100
            comparison_report["summary"]["average_similarity"] = self._calculate_average_similarity(comparison_report["comparisons"])
        
        return comparison_report
    
    def find_baseline_for_screenshot(self, screenshot_path: Path) -> Optional[Path]:
        """Find the corresponding baseline image for a screenshot."""
        # Try direct mapping first
        baseline_name = f"expected_{screenshot_path.name}"
        baseline_path = self.baseline_dir / baseline_name
        
        if baseline_path.exists():
            return baseline_path
        
        # Try pattern matching
        screenshot_name = screenshot_path.stem
        
        # Remove common suffixes
        suffixes_to_remove = ["_current", "_test", "_actual"]
        for suffix in suffixes_to_remove:
            if screenshot_name.endswith(suffix):
                screenshot_name = screenshot_name[:-len(suffix)]
        
        # Look for matching baseline
        for baseline_file in self.baseline_dir.glob("expected_*.png"):
            baseline_name = baseline_file.stem.replace("expected_", "")
            if baseline_name == screenshot_name:
                return baseline_file
        
        return None
    
    def _calculate_average_similarity(self, comparisons: Dict) -> float:
        """Calculate average similarity percentage across all comparisons."""
        similarities = []
        
        for comp_name, comp_result in comparisons.items():
            if not comp_result.get("error") and comp_result.get("similarity_percentage") is not None:
                similarities.append(comp_result["similarity_percentage"])
        
        if similarities:
            return sum(similarities) / len(similarities)
        return 0.0
    
    def generate_comparison_report(self, comparison_results: Dict, output_path: Path = None) -> Path:
        """Generate a detailed HTML comparison report."""
        if not output_path:
            output_path = self.reports_dir / f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        html_content = self._generate_html_report(comparison_results)
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"📊 Comparison report generated: {output_path}")
        return output_path
    
    def _generate_html_report(self, comparison_results: Dict) -> str:
        """Generate HTML content for the comparison report."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Visual Regression Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .comparison {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .passed {{ border-left: 5px solid #28a745; }}
                .failed {{ border-left: 5px solid #dc3545; }}
                .error {{ border-left: 5px solid #ffc107; }}
                .details {{ margin-top: 10px; }}
                .diff-image {{ max-width: 100%; height: auto; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Visual Regression Test Report</h1>
                <p>Generated: {comparison_results.get('compared_at', 'Unknown')}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Total Comparisons</td><td>{comparison_results.get('total_comparisons', 0)}</td></tr>
                    <tr><td>Passed</td><td style="color: green;">{comparison_results.get('passed', 0)}</td></tr>
                    <tr><td>Failed</td><td style="color: red;">{comparison_results.get('failed', 0)}</td></tr>
                    <tr><td>Errors</td><td style="color: orange;">{comparison_results.get('errors', 0)}</td></tr>
                    <tr><td>Pass Rate</td><td>{comparison_results.get('summary', {}).get('pass_rate', 0):.1f}%</td></tr>
                    <tr><td>Average Similarity</td><td>{comparison_results.get('summary', {}).get('average_similarity', 0):.2f}%</td></tr>
                </table>
            </div>
            
            <div class="comparisons">
                <h2>Detailed Comparisons</h2>
        """
        
        for screenshot_name, result in comparison_results.get('comparisons', {}).items():
            status_class = "error" if result.get('error') else ("passed" if result.get('passed') else "failed")
            
            html += f"""
                <div class="comparison {status_class}">
                    <h3>{screenshot_name}</h3>
                    <div class="details">
                        <p><strong>Similarity:</strong> {result.get('similarity_percentage', 0):.2f}%</p>
                        <p><strong>Threshold:</strong> {result.get('threshold', 0):.2f}%</p>
                        <p><strong>Status:</strong> {"✓ PASSED" if result.get('passed') else "✗ FAILED"}</p>
                        {f"<p><strong>Error:</strong> {result.get('error')}</p>" if result.get('error') else ""}
                        {f'<p><strong>Diff Image:</strong> <br><img src="{result.get("diff_path")}" class="diff-image"></p>' if result.get('diff_path') and not result.get('error') and not result.get('passed') else ""}
                    </div>
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def update_thresholds(self, page_type: str, threshold: float):
        """Update similarity threshold for a specific page type."""
        if 0 <= threshold <= 100:
            self.similarity_thresholds[page_type] = threshold
            print(f"✓ Updated threshold for {page_type}: {threshold}%")
        else:
            print(f"✗ Invalid threshold value: {threshold}%. Must be between 0 and 100.")
    
    def get_threshold_recommendations(self, comparison_results: Dict) -> Dict:
        """Analyze comparison results and recommend threshold adjustments."""
        recommendations = {}
        
        for screenshot_name, result in comparison_results.get('comparisons', {}).items():
            if not result.get('error') and not result.get('passed'):
                # Failed comparison - analyze if threshold should be adjusted
                similarity = result.get('similarity_percentage', 0)
                threshold = result.get('threshold', 95)
                
                # Determine page type
                page_type = "default"
                for p_type in self.similarity_thresholds.keys():
                    if p_type in screenshot_name.lower():
                        page_type = p_type
                        break
                
                # If similarity is close to threshold, recommend adjustment
                if similarity > threshold * 0.9:  # Within 10% of threshold
                    recommended_threshold = max(similarity - 1, 90)  # 1% below current similarity, min 90%
                    recommendations[page_type] = {
                        "current_threshold": threshold,
                        "recommended_threshold": recommended_threshold,
                        "reason": f"Similarity {similarity:.2f}% is close to threshold {threshold:.2f}%",
                        "screenshot_example": screenshot_name
                    }
        
        return recommendations


def main():
    """Main function for baseline comparison."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visual Test Baseline Comparison")
    parser.add_argument("--baseline-dir", type=Path, help="Baseline directory path")
    parser.add_argument("--screenshots-dir", type=Path, help="Screenshots directory path")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Compare all screenshots
    compare_parser = subparsers.add_parser("compare", help="Compare all screenshots with baselines")
    compare_parser.add_argument("--report", action="store_true", help="Generate HTML report")
    
    # Compare specific images
    compare_specific_parser = subparsers.add_parser("compare-images", help="Compare specific images")
    compare_specific_parser.add_argument("expected", type=Path, help="Expected image path")
    compare_specific_parser.add_argument("actual", type=Path, help="Actual image path")
    compare_specific_parser.add_argument("--diff", type=Path, help="Output diff image path")
    compare_specific_parser.add_argument("--threshold", type=float, default=95.0, help="Similarity threshold")
    
    # Update thresholds
    threshold_parser = subparsers.add_parser("update-threshold", help="Update similarity threshold")
    threshold_parser.add_argument("page_type", help="Page type (login, register, etc.)")
    threshold_parser.add_argument("threshold", type=float, help="New threshold value (0-100)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize comparator
    comparator = BaselineComparator(args.baseline_dir)
    
    # Execute command
    if args.command == "compare":
        results = comparator.compare_all_screenshots(args.screenshots_dir)
        
        if args.report:
            comparator.generate_comparison_report(results)
        
        # Print summary
        print(f"\n📊 COMPARISON SUMMARY")
        print(f"Total: {results['total_comparisons']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Errors: {results['errors']}")
        
        return 0 if results['failed'] == 0 and results['errors'] == 0 else 1
    
    elif args.command == "compare-images":
        result = comparator.compare_images_advanced(args.expected, args.actual, args.diff, args.threshold)
        
        print(f"Similarity: {result['similarity_percentage']:.2f}%")
        print(f"Threshold: {result['threshold']:.2f}%")
        print(f"Passed: {result['passed']}")
        
        if result['error']:
            print(f"Error: {result['error']}")
        
        return 0 if result['passed'] else 1
    
    elif args.command == "update-threshold":
        comparator.update_thresholds(args.page_type, args.threshold)
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())