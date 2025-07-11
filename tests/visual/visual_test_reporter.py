#!/usr/bin/env python3
"""
Visual Test Reporter
Generates comprehensive HTML reports for visual regression tests with performance metrics.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import base64
from jinja2 import Template
import sqlite3
from dataclasses import dataclass
import hashlib


@dataclass
class TestResult:
    """Test result data structure."""
    test_name: str
    page_name: str
    device: str
    status: str  # 'passed', 'failed', 'error'
    similarity: float = 0.0
    threshold: float = 95.0
    duration: float = 0.0
    screenshot_path: str = ""
    baseline_path: str = ""
    diff_path: str = ""
    error_message: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "page_name": self.page_name,
            "device": self.device,
            "status": self.status,
            "similarity": self.similarity,
            "threshold": self.threshold,
            "duration": self.duration,
            "screenshot_path": self.screenshot_path,
            "baseline_path": self.baseline_path,
            "diff_path": self.diff_path,
            "error_message": self.error_message,
            "timestamp": self.timestamp
        }


class VisualTestReporter:
    """Generates comprehensive visual test reports with performance metrics."""
    
    def __init__(self, test_env: str = "visual_test"):
        self.test_env = test_env
        self.test_dir = Path(__file__).parent
        self.reports_dir = self.test_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Database for storing test results
        self.db_path = self.reports_dir / "test_results.db"
        self.init_database()
        
        # Report templates
        self.html_template = self.get_html_template()
        self.json_template = self.get_json_template()
        
        # Performance tracking
        self.performance_metrics = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "error_tests": 0,
            "total_duration": 0.0,
            "avg_similarity": 0.0,
            "screenshots_generated": 0,
            "baselines_compared": 0,
            "started_at": "",
            "ended_at": ""
        }
    
    def init_database(self):
        """Initialize SQLite database for test results."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Create test results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_session_id TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    page_name TEXT NOT NULL,
                    device TEXT NOT NULL,
                    status TEXT NOT NULL,
                    similarity REAL,
                    threshold REAL,
                    duration REAL,
                    screenshot_path TEXT,
                    baseline_path TEXT,
                    diff_path TEXT,
                    error_message TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create test sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_sessions (
                    id TEXT PRIMARY KEY,
                    test_env TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    total_tests INTEGER,
                    passed_tests INTEGER,
                    failed_tests INTEGER,
                    error_tests INTEGER,
                    total_duration REAL,
                    avg_similarity REAL,
                    status TEXT NOT NULL DEFAULT 'running',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_session_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    metric_unit TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            print("✓ Test results database initialized")
            
        except Exception as e:
            print(f"✗ Failed to initialize database: {e}")
    
    def start_test_session(self) -> str:
        """Start a new test session."""
        session_id = f"session_{int(time.time())}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"
        
        self.performance_metrics["started_at"] = datetime.now().isoformat()
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO test_sessions (id, test_env, started_at)
                VALUES (?, ?, ?)
            ''', (session_id, self.test_env, self.performance_metrics["started_at"]))
            
            conn.commit()
            conn.close()
            
            print(f"✓ Test session started: {session_id}")
            
        except Exception as e:
            print(f"⚠️ Failed to record test session: {e}")
        
        return session_id
    
    def end_test_session(self, session_id: str):
        """End a test session and update metrics."""
        self.performance_metrics["ended_at"] = datetime.now().isoformat()
        
        # Calculate average similarity
        if self.performance_metrics["total_tests"] > 0:
            self.performance_metrics["avg_similarity"] = (
                self.performance_metrics["avg_similarity"] / self.performance_metrics["total_tests"]
            )
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE test_sessions 
                SET ended_at = ?, total_tests = ?, passed_tests = ?, 
                    failed_tests = ?, error_tests = ?, total_duration = ?, 
                    avg_similarity = ?, status = 'completed'
                WHERE id = ?
            ''', (
                self.performance_metrics["ended_at"],
                self.performance_metrics["total_tests"],
                self.performance_metrics["passed_tests"],
                self.performance_metrics["failed_tests"],
                self.performance_metrics["error_tests"],
                self.performance_metrics["total_duration"],
                self.performance_metrics["avg_similarity"],
                session_id
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✓ Test session ended: {session_id}")
            
        except Exception as e:
            print(f"⚠️ Failed to update test session: {e}")
    
    def record_test_result(self, session_id: str, test_result: TestResult):
        """Record a test result in the database."""
        # Update performance metrics
        self.performance_metrics["total_tests"] += 1
        
        if test_result.status == "passed":
            self.performance_metrics["passed_tests"] += 1
        elif test_result.status == "failed":
            self.performance_metrics["failed_tests"] += 1
        else:
            self.performance_metrics["error_tests"] += 1
        
        self.performance_metrics["total_duration"] += test_result.duration
        self.performance_metrics["avg_similarity"] += test_result.similarity
        
        if test_result.screenshot_path:
            self.performance_metrics["screenshots_generated"] += 1
        
        if test_result.baseline_path:
            self.performance_metrics["baselines_compared"] += 1
        
        # Store in database
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO test_results (
                    test_session_id, test_name, page_name, device, status,
                    similarity, threshold, duration, screenshot_path, baseline_path,
                    diff_path, error_message, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                test_result.test_name,
                test_result.page_name,
                test_result.device,
                test_result.status,
                test_result.similarity,
                test_result.threshold,
                test_result.duration,
                test_result.screenshot_path,
                test_result.baseline_path,
                test_result.diff_path,
                test_result.error_message,
                test_result.timestamp
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Failed to record test result: {e}")
    
    def generate_html_report(self, session_id: str, output_path: Path = None) -> Path:
        """Generate comprehensive HTML report."""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.reports_dir / f"visual_test_report_{timestamp}.html"
        
        # Get test results from database
        test_results = self.get_session_results(session_id)
        session_data = self.get_session_data(session_id)
        
        # Prepare template data
        template_data = {
            "session_id": session_id,
            "session_data": session_data,
            "test_results": test_results,
            "performance_metrics": self.performance_metrics,
            "generated_at": datetime.now().isoformat(),
            "report_title": f"Visual Test Report - {session_id}",
            "summary_stats": self.calculate_summary_stats(test_results),
            "device_stats": self.calculate_device_stats(test_results),
            "page_stats": self.calculate_page_stats(test_results),
            "failure_analysis": self.analyze_failures(test_results)
        }
        
        # Render HTML template
        try:
            template = Template(self.html_template)
            html_content = template.render(**template_data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✓ HTML report generated: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Failed to generate HTML report: {e}")
            return None
    
    def generate_json_report(self, session_id: str, output_path: Path = None) -> Path:
        """Generate machine-readable JSON report."""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.reports_dir / f"visual_test_report_{timestamp}.json"
        
        # Get test results from database
        test_results = self.get_session_results(session_id)
        session_data = self.get_session_data(session_id)
        
        # Prepare JSON data
        json_data = {
            "report_metadata": {
                "session_id": session_id,
                "generated_at": datetime.now().isoformat(),
                "test_env": self.test_env,
                "report_version": "1.0"
            },
            "session_data": session_data,
            "performance_metrics": self.performance_metrics,
            "test_results": [result.to_dict() for result in test_results],
            "summary_stats": self.calculate_summary_stats(test_results),
            "device_stats": self.calculate_device_stats(test_results),
            "page_stats": self.calculate_page_stats(test_results),
            "failure_analysis": self.analyze_failures(test_results)
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ JSON report generated: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Failed to generate JSON report: {e}")
            return None
    
    def get_session_results(self, session_id: str) -> List[TestResult]:
        """Get all test results for a session."""
        results = []
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT test_name, page_name, device, status, similarity, threshold,
                       duration, screenshot_path, baseline_path, diff_path, 
                       error_message, timestamp
                FROM test_results 
                WHERE test_session_id = ?
                ORDER BY timestamp ASC
            ''', (session_id,))
            
            for row in cursor.fetchall():
                result = TestResult(
                    test_name=row[0],
                    page_name=row[1],
                    device=row[2],
                    status=row[3],
                    similarity=row[4] or 0.0,
                    threshold=row[5] or 95.0,
                    duration=row[6] or 0.0,
                    screenshot_path=row[7] or "",
                    baseline_path=row[8] or "",
                    diff_path=row[9] or "",
                    error_message=row[10] or "",
                    timestamp=row[11] or ""
                )
                results.append(result)
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Failed to get session results: {e}")
        
        return results
    
    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get session data from database."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT test_env, started_at, ended_at, total_tests, passed_tests,
                       failed_tests, error_tests, total_duration, avg_similarity, status
                FROM test_sessions 
                WHERE id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "test_env": row[0],
                    "started_at": row[1],
                    "ended_at": row[2],
                    "total_tests": row[3] or 0,
                    "passed_tests": row[4] or 0,
                    "failed_tests": row[5] or 0,
                    "error_tests": row[6] or 0,
                    "total_duration": row[7] or 0.0,
                    "avg_similarity": row[8] or 0.0,
                    "status": row[9] or "unknown"
                }
            
        except Exception as e:
            print(f"⚠️ Failed to get session data: {e}")
        
        return {}
    
    def calculate_summary_stats(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        if not test_results:
            return {}
        
        total_tests = len(test_results)
        passed_tests = sum(1 for r in test_results if r.status == "passed")
        failed_tests = sum(1 for r in test_results if r.status == "failed")
        error_tests = sum(1 for r in test_results if r.status == "error")
        
        similarities = [r.similarity for r in test_results if r.similarity > 0]
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        
        durations = [r.duration for r in test_results if r.duration > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "pass_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "avg_similarity": avg_similarity,
            "avg_duration": avg_duration,
            "total_duration": sum(durations)
        }
    
    def calculate_device_stats(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Calculate device-specific statistics."""
        device_stats = {}
        
        for result in test_results:
            device = result.device
            if device not in device_stats:
                device_stats[device] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "error": 0,
                    "similarities": [],
                    "durations": []
                }
            
            stats = device_stats[device]
            stats["total"] += 1
            
            if result.status == "passed":
                stats["passed"] += 1
            elif result.status == "failed":
                stats["failed"] += 1
            else:
                stats["error"] += 1
            
            if result.similarity > 0:
                stats["similarities"].append(result.similarity)
            
            if result.duration > 0:
                stats["durations"].append(result.duration)
        
        # Calculate averages
        for device, stats in device_stats.items():
            stats["pass_rate"] = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            stats["avg_similarity"] = sum(stats["similarities"]) / len(stats["similarities"]) if stats["similarities"] else 0
            stats["avg_duration"] = sum(stats["durations"]) / len(stats["durations"]) if stats["durations"] else 0
        
        return device_stats
    
    def calculate_page_stats(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Calculate page-specific statistics."""
        page_stats = {}
        
        for result in test_results:
            page = result.page_name
            if page not in page_stats:
                page_stats[page] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "error": 0,
                    "similarities": [],
                    "durations": []
                }
            
            stats = page_stats[page]
            stats["total"] += 1
            
            if result.status == "passed":
                stats["passed"] += 1
            elif result.status == "failed":
                stats["failed"] += 1
            else:
                stats["error"] += 1
            
            if result.similarity > 0:
                stats["similarities"].append(result.similarity)
            
            if result.duration > 0:
                stats["durations"].append(result.duration)
        
        # Calculate averages
        for page, stats in page_stats.items():
            stats["pass_rate"] = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            stats["avg_similarity"] = sum(stats["similarities"]) / len(stats["similarities"]) if stats["similarities"] else 0
            stats["avg_duration"] = sum(stats["durations"]) / len(stats["durations"]) if stats["durations"] else 0
        
        return page_stats
    
    def analyze_failures(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """Analyze failure patterns."""
        failures = [r for r in test_results if r.status == "failed"]
        
        if not failures:
            return {"total_failures": 0, "patterns": []}
        
        # Group failures by device
        device_failures = {}
        for failure in failures:
            device = failure.device
            if device not in device_failures:
                device_failures[device] = []
            device_failures[device].append(failure)
        
        # Group failures by page
        page_failures = {}
        for failure in failures:
            page = failure.page_name
            if page not in page_failures:
                page_failures[page] = []
            page_failures[page].append(failure)
        
        # Find common failure patterns
        patterns = []
        
        # Pages with multiple device failures
        for page, page_fails in page_failures.items():
            if len(page_fails) > 1:
                devices = [f.device for f in page_fails]
                patterns.append({
                    "type": "cross_device_failure",
                    "description": f"Page '{page}' failed on multiple devices: {', '.join(devices)}",
                    "count": len(page_fails),
                    "avg_similarity": sum(f.similarity for f in page_fails) / len(page_fails)
                })
        
        # Low similarity patterns
        low_similarity = [f for f in failures if f.similarity < 85.0]
        if low_similarity:
            patterns.append({
                "type": "low_similarity",
                "description": f"{len(low_similarity)} tests with very low similarity (<85%)",
                "count": len(low_similarity),
                "avg_similarity": sum(f.similarity for f in low_similarity) / len(low_similarity)
            })
        
        return {
            "total_failures": len(failures),
            "device_failures": device_failures,
            "page_failures": page_failures,
            "patterns": patterns
        }
    
    def get_html_template(self) -> str:
        """Get HTML template for reports."""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report_title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0;
            opacity: 0.9;
        }
        .content {
            padding: 30px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }
        .metric-card.success {
            border-left-color: #28a745;
        }
        .metric-card.warning {
            border-left-color: #ffc107;
        }
        .metric-card.danger {
            border-left-color: #dc3545;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .test-results {
            overflow-x: auto;
        }
        .test-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .test-table th,
        .test-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .test-table th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-passed {
            background-color: #d4edda;
            color: #155724;
        }
        .status-failed {
            background-color: #f8d7da;
            color: #721c24;
        }
        .status-error {
            background-color: #fff3cd;
            color: #856404;
        }
        .similarity-bar {
            width: 100px;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }
        .similarity-fill {
            height: 100%;
            background-color: #28a745;
            transition: width 0.3s ease;
        }
        .similarity-fill.warning {
            background-color: #ffc107;
        }
        .similarity-fill.danger {
            background-color: #dc3545;
        }
        .similarity-text {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7em;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
        }
        .footer {
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        .expandable {
            cursor: pointer;
            user-select: none;
        }
        .expandable:hover {
            background-color: #f8f9fa;
        }
        .expandable-content {
            display: none;
            padding: 15px;
            background-color: #f8f9fa;
            border-top: 1px solid #ddd;
        }
        .expandable-content.active {
            display: block;
        }
        .chart-container {
            height: 300px;
            margin: 20px 0;
        }
        @media (max-width: 768px) {
            .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ report_title }}</h1>
            <p>Generated on {{ generated_at }}</p>
            <p>Session ID: {{ session_id }}</p>
        </div>
        
        <div class="content">
            <!-- Performance Metrics -->
            <div class="section">
                <h2>Performance Overview</h2>
                <div class="metrics-grid">
                    <div class="metric-card success">
                        <div class="metric-value">{{ summary_stats.total_tests }}</div>
                        <div class="metric-label">Total Tests</div>
                    </div>
                    <div class="metric-card {{ 'success' if summary_stats.pass_rate > 90 else 'warning' if summary_stats.pass_rate > 70 else 'danger' }}">
                        <div class="metric-value">{{ "%.1f" | format(summary_stats.pass_rate) }}%</div>
                        <div class="metric-label">Pass Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ "%.1f" | format(summary_stats.avg_similarity) }}%</div>
                        <div class="metric-label">Avg Similarity</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{{ "%.1f" | format(summary_stats.avg_duration) }}s</div>
                        <div class="metric-label">Avg Duration</div>
                    </div>
                </div>
            </div>
            
            <!-- Test Results -->
            <div class="section">
                <h2>Test Results</h2>
                <div class="test-results">
                    <table class="test-table">
                        <thead>
                            <tr>
                                <th>Test Name</th>
                                <th>Page</th>
                                <th>Device</th>
                                <th>Status</th>
                                <th>Similarity</th>
                                <th>Duration</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for result in test_results %}
                            <tr class="expandable" onclick="toggleExpand(this)">
                                <td>{{ result.test_name }}</td>
                                <td>{{ result.page_name }}</td>
                                <td>{{ result.device }}</td>
                                <td>
                                    <span class="status-badge status-{{ result.status }}">
                                        {{ result.status }}
                                    </span>
                                </td>
                                <td>
                                    <div class="similarity-bar">
                                        <div class="similarity-fill {{ 'danger' if result.similarity < 90 else 'warning' if result.similarity < 95 else '' }}" 
                                             style="width: {{ result.similarity }}%"></div>
                                        <div class="similarity-text">{{ "%.1f" | format(result.similarity) }}%</div>
                                    </div>
                                </td>
                                <td>{{ "%.2f" | format(result.duration) }}s</td>
                                <td>{{ result.timestamp }}</td>
                            </tr>
                            {% if result.error_message or result.diff_path %}
                            <tr>
                                <td colspan="7" class="expandable-content">
                                    {% if result.error_message %}
                                    <div><strong>Error:</strong> {{ result.error_message }}</div>
                                    {% endif %}
                                    {% if result.diff_path %}
                                    <div><strong>Diff Image:</strong> {{ result.diff_path }}</div>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endif %}
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Device Statistics -->
            <div class="section">
                <h2>Device Statistics</h2>
                <div class="metrics-grid">
                    {% for device, stats in device_stats.items() %}
                    <div class="metric-card">
                        <div class="metric-value">{{ device }}</div>
                        <div class="metric-label">
                            {{ stats.total }} tests, {{ "%.1f" | format(stats.pass_rate) }}% pass rate
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <!-- Failure Analysis -->
            {% if failure_analysis.total_failures > 0 %}
            <div class="section">
                <h2>Failure Analysis</h2>
                <div class="metric-card danger">
                    <div class="metric-value">{{ failure_analysis.total_failures }}</div>
                    <div class="metric-label">Total Failures</div>
                </div>
                
                {% if failure_analysis.patterns %}
                <h3>Failure Patterns</h3>
                <ul>
                    {% for pattern in failure_analysis.patterns %}
                    <li>{{ pattern.description }} ({{ pattern.count }} occurrences)</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>Visual Test Report generated by Visual Test Reporter v1.0</p>
            <p>Session: {{ session_id }} | Environment: {{ session_data.test_env }}</p>
        </div>
    </div>
    
    <script>
        function toggleExpand(row) {
            const next = row.nextElementSibling;
            if (next && next.querySelector('.expandable-content')) {
                const content = next.querySelector('.expandable-content');
                content.classList.toggle('active');
            }
        }
        
        // Initialize chart if needed
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Visual Test Report loaded');
        });
    </script>
</body>
</html>
        '''
    
    def get_json_template(self) -> str:
        """Get JSON template structure."""
        return '''
{
    "report_metadata": {
        "session_id": "{{ session_id }}",
        "generated_at": "{{ generated_at }}",
        "test_env": "{{ test_env }}",
        "report_version": "1.0"
    },
    "session_data": {{ session_data | tojson }},
    "performance_metrics": {{ performance_metrics | tojson }},
    "test_results": {{ test_results | tojson }},
    "summary_stats": {{ summary_stats | tojson }},
    "device_stats": {{ device_stats | tojson }},
    "page_stats": {{ page_stats | tojson }},
    "failure_analysis": {{ failure_analysis | tojson }}
}
        '''
    
    def get_historical_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get historical test data for trend analysis."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, test_env, started_at, ended_at, total_tests, 
                       passed_tests, failed_tests, error_tests, 
                       total_duration, avg_similarity, status
                FROM test_sessions 
                WHERE started_at > ? AND status = 'completed'
                ORDER BY started_at DESC
            ''', (cutoff_date.isoformat(),))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    "id": row[0],
                    "test_env": row[1],
                    "started_at": row[2],
                    "ended_at": row[3],
                    "total_tests": row[4],
                    "passed_tests": row[5],
                    "failed_tests": row[6],
                    "error_tests": row[7],
                    "total_duration": row[8],
                    "avg_similarity": row[9],
                    "status": row[10]
                })
            
            conn.close()
            return sessions
            
        except Exception as e:
            print(f"⚠️ Failed to get historical data: {e}")
            return []
    
    def export_ci_metrics(self, session_id: str, output_path: Path = None) -> Path:
        """Export CI/CD compatible metrics."""
        if not output_path:
            output_path = self.reports_dir / "ci_metrics.json"
        
        session_data = self.get_session_data(session_id)
        test_results = self.get_session_results(session_id)
        
        # CI/CD friendly metrics
        ci_metrics = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "status": "passed" if session_data.get("failed_tests", 0) == 0 else "failed",
            "total_tests": session_data.get("total_tests", 0),
            "passed_tests": session_data.get("passed_tests", 0),
            "failed_tests": session_data.get("failed_tests", 0),
            "error_tests": session_data.get("error_tests", 0),
            "pass_rate": (session_data.get("passed_tests", 0) / session_data.get("total_tests", 1)) * 100,
            "avg_similarity": session_data.get("avg_similarity", 0),
            "total_duration": session_data.get("total_duration", 0),
            "test_env": session_data.get("test_env", "unknown"),
            "failures": [
                {
                    "test_name": r.test_name,
                    "page_name": r.page_name,
                    "device": r.device,
                    "similarity": r.similarity,
                    "error_message": r.error_message
                }
                for r in test_results if r.status == "failed"
            ]
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(ci_metrics, f, indent=2)
            
            print(f"✓ CI metrics exported: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Failed to export CI metrics: {e}")
            return None


def main():
    """Main function for visual test reporting."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visual Test Reporter")
    parser.add_argument("--env", default="visual_test", help="Test environment")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate report
    report_parser = subparsers.add_parser("report", help="Generate test report")
    report_parser.add_argument("session_id", help="Test session ID")
    report_parser.add_argument("--format", choices=["html", "json", "both"], default="both", help="Report format")
    report_parser.add_argument("--output", type=Path, help="Output directory")
    
    # Historical data
    hist_parser = subparsers.add_parser("history", help="Get historical data")
    hist_parser.add_argument("--days", type=int, default=30, help="Number of days")
    
    # CI metrics
    ci_parser = subparsers.add_parser("ci-metrics", help="Export CI metrics")
    ci_parser.add_argument("session_id", help="Test session ID")
    ci_parser.add_argument("--output", type=Path, help="Output file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    reporter = VisualTestReporter(args.env)
    
    if args.command == "report":
        if args.format in ["html", "both"]:
            reporter.generate_html_report(args.session_id, args.output)
        
        if args.format in ["json", "both"]:
            reporter.generate_json_report(args.session_id, args.output)
        
        return 0
    
    elif args.command == "history":
        history = reporter.get_historical_data(args.days)
        print(json.dumps(history, indent=2))
        return 0
    
    elif args.command == "ci-metrics":
        reporter.export_ci_metrics(args.session_id, args.output)
        return 0
    
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
