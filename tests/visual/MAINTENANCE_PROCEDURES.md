# Visual Testing Maintenance Procedures

## Overview

This document outlines comprehensive maintenance procedures for the visual regression testing suite. Regular maintenance ensures test reliability, performance, and continued value to the development process.

## Maintenance Schedule

### Daily Tasks (Automated)

#### Test Execution Monitoring
- **Automated CI/CD runs**: Monitor test results in GitHub Actions
- **Performance metrics**: Track execution time trends
- **Failure analysis**: Investigate and categorize test failures

```bash
# Daily health check script
#!/bin/bash
# daily_health_check.sh

echo "=== Daily Visual Test Health Check ==="
date

# Check test execution status
echo "\n--- Recent Test Results ---"
python visual_test_reporter.py history --days 1

# Check system resources
echo "\n--- Resource Usage ---"
python test_isolation_manager.py usage

# Clean up old files
echo "\n--- Cleanup ---"
python test_isolation_manager.py cleanup

# Check for stale baselines
echo "\n--- Baseline Status ---"
python baseline_manager.py info
```

### Weekly Tasks

#### Test Results Review
- **Performance Analysis**: Review test execution times and trends
- **Failure Pattern Analysis**: Identify recurring issues
- **Baseline Drift Detection**: Monitor similarity score trends

```python
# Weekly analysis script
#!/usr/bin/env python3
# weekly_analysis.py

import json
from datetime import datetime, timedelta
from visual_test_reporter import VisualTestReporter

def weekly_analysis():
    reporter = VisualTestReporter()
    
    # Get last 7 days of data
    historical_data = reporter.get_historical_data(7)
    
    # Analysis
    total_tests = sum(session['total_tests'] for session in historical_data)
    avg_pass_rate = sum(session['passed_tests'] / session['total_tests'] * 100 
                       for session in historical_data) / len(historical_data)
    
    # Generate report
    report = {
        "period": "last_7_days",
        "total_test_runs": len(historical_data),
        "total_tests_executed": total_tests,
        "average_pass_rate": avg_pass_rate,
        "recommendations": []
    }
    
    # Add recommendations based on metrics
    if avg_pass_rate < 90:
        report["recommendations"].append("Pass rate below 90% - investigate failing tests")
    
    if total_tests == 0:
        report["recommendations"].append("No tests executed - check CI/CD pipeline")
    
    # Save report
    with open(f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    weekly_analysis()
```

#### File Cleanup
- **Screenshot Cleanup**: Remove old screenshots (>30 days)
- **Report Cleanup**: Archive old reports (>90 days)
- **Log Cleanup**: Rotate and compress log files

```python
# Cleanup script
#!/usr/bin/env python3
# cleanup_old_files.py

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_old_files():
    test_dir = Path(__file__).parent
    
    # Cleanup screenshots older than 30 days
    screenshots_dir = test_dir / "screenshots"
    cleanup_directory(screenshots_dir, 30)
    
    # Cleanup diff images older than 14 days
    diff_dir = test_dir / "diff"
    cleanup_directory(diff_dir, 14)
    
    # Archive reports older than 90 days
    reports_dir = test_dir / "reports"
    archive_directory(reports_dir, 90)
    
    # Cleanup isolation data older than 7 days
    isolation_dir = test_dir / "isolation"
    cleanup_directory(isolation_dir, 7)

def cleanup_directory(directory, days_old):
    """Remove files older than specified days."""
    if not directory.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_age < cutoff_date:
                file_path.unlink()
                print(f"Removed: {file_path}")

def archive_directory(directory, days_old):
    """Archive files older than specified days."""
    if not directory.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    archive_dir = directory / "archive"
    archive_dir.mkdir(exist_ok=True)
    
    for file_path in directory.glob("*"):
        if file_path.is_file() and file_path.parent != archive_dir:
            file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_age < cutoff_date:
                shutil.move(str(file_path), str(archive_dir / file_path.name))
                print(f"Archived: {file_path}")

if __name__ == "__main__":
    cleanup_old_files()
```

### Monthly Tasks

#### Baseline Review and Updates
- **Baseline Audit**: Review all baseline images for accuracy
- **Version Management**: Update baseline versions
- **Similarity Threshold Review**: Adjust thresholds based on historical data

```python
# Monthly baseline review
#!/usr/bin/env python3
# monthly_baseline_review.py

from pathlib import Path
from datetime import datetime, timedelta
from baseline_manager import BaselineManager
from baseline_comparator import BaselineComparator

def monthly_baseline_review():
    manager = BaselineManager()
    comparator = BaselineComparator()
    
    # Get baseline metadata
    baseline_info = manager.get_baseline_info()
    
    print("=== Monthly Baseline Review ===")
    print(f"Total baselines: {baseline_info.get('total_baselines', 0)}")
    print(f"Last updated: {baseline_info.get('last_updated', 'Unknown')}")
    
    # Check for outdated baselines (>90 days)
    if baseline_info.get('last_updated'):
        last_updated = datetime.fromisoformat(baseline_info['last_updated'])
        days_old = (datetime.now() - last_updated).days
        
        if days_old > 90:
            print(f"⚠️ Baselines are {days_old} days old - consider updating")
    
    # Review similarity thresholds
    print("\n--- Similarity Threshold Analysis ---")
    threshold_analysis = comparator.analyze_threshold_effectiveness()
    
    for page_type, analysis in threshold_analysis.items():
        current_threshold = analysis['current_threshold']
        recommended_threshold = analysis['recommended_threshold']
        
        if abs(current_threshold - recommended_threshold) > 2.0:
            print(f"{page_type}: Current {current_threshold}% -> Recommended {recommended_threshold}%")
    
    # Generate baseline health report
    health_report = {
        "review_date": datetime.now().isoformat(),
        "baseline_info": baseline_info,
        "threshold_analysis": threshold_analysis,
        "recommendations": []
    }
    
    # Save report
    with open(f"baseline_review_{datetime.now().strftime('%Y%m')}.json", 'w') as f:
        json.dump(health_report, f, indent=2)
    
    print("\n✓ Monthly baseline review completed")

if __name__ == "__main__":
    monthly_baseline_review()
```

#### Performance Optimization
- **Execution Time Analysis**: Identify slow tests
- **Resource Usage Review**: Monitor memory and CPU usage
- **Optimization Implementation**: Apply performance improvements

```python
# Performance optimization script
#!/usr/bin/env python3
# performance_optimization.py

import json
import statistics
from visual_test_reporter import VisualTestReporter

def performance_optimization():
    reporter = VisualTestReporter()
    
    # Get performance data from last 30 days
    historical_data = reporter.get_historical_data(30)
    
    # Analyze execution times
    execution_times = [session['total_duration'] for session in historical_data]
    
    if execution_times:
        avg_time = statistics.mean(execution_times)
        median_time = statistics.median(execution_times)
        
        print("=== Performance Analysis ===")
        print(f"Average execution time: {avg_time:.2f}s")
        print(f"Median execution time: {median_time:.2f}s")
        
        # Identify slow sessions
        slow_sessions = [s for s in historical_data if s['total_duration'] > avg_time * 1.5]
        
        if slow_sessions:
            print(f"\n⚠️ {len(slow_sessions)} slow sessions identified:")
            for session in slow_sessions[:5]:  # Show top 5
                print(f"  - {session['id']}: {session['total_duration']:.2f}s")
    
    # Generate optimization recommendations
    recommendations = []
    
    if avg_time > 300:  # 5 minutes
        recommendations.append("Consider running tests in parallel")
    
    if len([s for s in historical_data if s['failed_tests'] > 0]) > len(historical_data) * 0.1:
        recommendations.append("High failure rate - investigate test stability")
    
    print("\n--- Optimization Recommendations ---")
    for rec in recommendations:
        print(f"• {rec}")

if __name__ == "__main__":
    performance_optimization()
```

### Quarterly Tasks

#### Comprehensive Test Suite Review
- **Test Coverage Analysis**: Ensure all UI components are tested
- **Test Effectiveness Review**: Evaluate test value and reliability
- **Tool Updates**: Update testing tools and dependencies

```python
# Quarterly review script
#!/usr/bin/env python3
# quarterly_review.py

import json
from pathlib import Path
from datetime import datetime, timedelta

def quarterly_review():
    print("=== Quarterly Test Suite Review ===")
    
    # Test coverage analysis
    test_modules = get_test_modules()
    coverage_report = analyze_test_coverage(test_modules)
    
    # Tool version analysis
    tool_versions = check_tool_versions()
    
    # Generate comprehensive report
    report = {
        "review_date": datetime.now().isoformat(),
        "test_coverage": coverage_report,
        "tool_versions": tool_versions,
        "recommendations": []
    }
    
    # Save report
    with open(f"quarterly_review_{datetime.now().strftime('%Y_Q%q')}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✓ Quarterly review completed")

def get_test_modules():
    """Get list of all test modules."""
    test_dir = Path(__file__).parent
    return list(test_dir.glob("*_visual_test.py"))

def analyze_test_coverage(test_modules):
    """Analyze test coverage across modules."""
    coverage = {
        "total_modules": len(test_modules),
        "modules": []
    }
    
    for module in test_modules:
        module_info = {
            "name": module.stem,
            "last_modified": datetime.fromtimestamp(module.stat().st_mtime).isoformat(),
            "size": module.stat().st_size
        }
        coverage["modules"].append(module_info)
    
    return coverage

def check_tool_versions():
    """Check versions of testing tools."""
    import subprocess
    import sys
    
    tools = {}
    
    try:
        # Python version
        tools["python"] = sys.version.split()[0]
        
        # Chrome version
        result = subprocess.run(["google-chrome", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            tools["chrome"] = result.stdout.strip()
        
        # ChromeDriver version
        result = subprocess.run(["chromedriver", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            tools["chromedriver"] = result.stdout.strip()
        
    except Exception as e:
        tools["error"] = str(e)
    
    return tools

if __name__ == "__main__":
    quarterly_review()
```

## Emergency Procedures

### Test Suite Failure

#### Immediate Response
1. **Assess Impact**: Determine if failures are widespread or isolated
2. **Check Infrastructure**: Verify CI/CD pipeline health
3. **Review Recent Changes**: Identify potential causes

```bash
# Emergency diagnostic script
#!/bin/bash
# emergency_diagnostics.sh

echo "=== Emergency Visual Test Diagnostics ==="
date

# Check server availability
echo "\n--- Server Status ---"
curl -f http://localhost:8000/health || echo "❌ Server unavailable"

# Check recent test results
echo "\n--- Recent Test Results ---"
python visual_test_reporter.py history --days 1

# Check system resources
echo "\n--- System Resources ---"
df -h
free -m

# Check browser availability
echo "\n--- Browser Status ---"
google-chrome --version
chromedriver --version

# Check test environment
echo "\n--- Test Environment ---"
ls -la tests/visual/
echo "Baseline count: $(ls -1 tests/visual/baseline/ | wc -l)"
echo "Screenshot count: $(ls -1 tests/visual/screenshots/ | wc -l)"
```

#### Root Cause Analysis
- **Log Analysis**: Review test execution logs
- **Environment Check**: Verify test environment consistency
- **Code Review**: Check recent commits for issues

#### Recovery Procedures
1. **Baseline Recovery**: Restore from backup if baselines are corrupted
2. **Environment Reset**: Recreate test environment
3. **Gradual Rollback**: Test individual components

```python
# Emergency recovery script
#!/usr/bin/env python3
# emergency_recovery.py

import shutil
from pathlib import Path
from datetime import datetime
from baseline_manager import BaselineManager

def emergency_recovery():
    print("=== Emergency Recovery Procedure ===")
    
    # Create emergency backup
    backup_name = f"emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    manager = BaselineManager()
    
    print(f"Creating emergency backup: {backup_name}")
    manager.backup_baselines(backup_name)
    
    # Check for latest stable baseline
    versions = manager.list_baseline_versions()
    stable_versions = [v for v in versions if "stable" in v.lower()]
    
    if stable_versions:
        latest_stable = stable_versions[-1]
        print(f"Restoring from latest stable baseline: {latest_stable}")
        manager.restore_baselines(latest_stable)
    else:
        print("⚠️ No stable baseline found - manual intervention required")
    
    # Clear temporary files
    test_dir = Path(__file__).parent
    temp_dirs = ["screenshots", "diff", "isolation/temp"]
    
    for temp_dir in temp_dirs:
        dir_path = test_dir / temp_dir
        if dir_path.exists():
            shutil.rmtree(dir_path)
            dir_path.mkdir()
            print(f"Cleared temporary directory: {temp_dir}")
    
    print("\n✓ Emergency recovery completed")
    print("Next steps:")
    print("1. Run basic test to verify functionality")
    print("2. Investigate root cause of failure")
    print("3. Update documentation if needed")

if __name__ == "__main__":
    emergency_recovery()
```

### Baseline Corruption

#### Detection
- **Automated Checks**: Regular baseline integrity checks
- **Test Failure Patterns**: Widespread similarity failures
- **Manual Verification**: Visual inspection of baselines

#### Recovery
1. **Restore from Backup**: Use most recent stable backup
2. **Regenerate Baselines**: Create new baselines from known good state
3. **Validation**: Verify restored baselines work correctly

## Performance Monitoring

### Key Performance Indicators (KPIs)

#### Test Execution Metrics
- **Average Execution Time**: Target < 5 minutes for full suite
- **Test Pass Rate**: Target > 95%
- **Baseline Update Frequency**: Monthly or after major UI changes
- **False Positive Rate**: Target < 5%

#### Resource Usage Metrics
- **CPU Usage**: Monitor during test execution
- **Memory Usage**: Track memory consumption trends
- **Disk Space**: Monitor storage usage for screenshots/reports
- **Network Usage**: Track if applicable

```python
# Performance monitoring script
#!/usr/bin/env python3
# performance_monitor.py

import psutil
import time
from datetime import datetime

def monitor_performance():
    """Monitor system performance during test execution."""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "network_io": psutil.net_io_counters()._asdict()
    }
    
    return metrics

def continuous_monitoring(duration_minutes=10):
    """Continuously monitor performance."""
    end_time = time.time() + (duration_minutes * 60)
    measurements = []
    
    while time.time() < end_time:
        measurements.append(monitor_performance())
        time.sleep(30)  # Measure every 30 seconds
    
    return measurements

if __name__ == "__main__":
    print("Starting performance monitoring...")
    results = continuous_monitoring(5)  # Monitor for 5 minutes
    
    # Save results
    with open(f"performance_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Performance monitoring completed")
```

### Alerting and Notifications

#### Alert Conditions
- **Test Failures**: > 10% failure rate
- **Performance Degradation**: > 50% increase in execution time
- **Resource Issues**: > 90% CPU or memory usage
- **Baseline Issues**: Widespread similarity failures

#### Notification Channels
- **Email**: For non-urgent issues
- **Slack/Teams**: For immediate attention
- **Dashboard**: Real-time status display

```python
# Alerting system
#!/usr/bin/env python3
# alerting_system.py

import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class AlertingSystem:
    def __init__(self):
        self.email_config = {
            "smtp_server": "smtp.company.com",
            "smtp_port": 587,
            "username": "visual-tests@company.com",
            "password": "password",
            "recipients": ["dev-team@company.com"]
        }
    
    def send_alert(self, alert_type, message, severity="medium"):
        """Send alert notification."""
        subject = f"[Visual Tests] {alert_type.upper()} - {severity.upper()}"
        
        body = f"""
        Visual Test Alert
        
        Type: {alert_type}
        Severity: {severity}
        Time: {datetime.now().isoformat()}
        
        Details:
        {message}
        
        Dashboard: https://your-dashboard.com/visual-tests
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_config['username']
        msg['To'] = ', '.join(self.email_config['recipients'])
        
        try:
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            print(f"Alert sent: {alert_type}")
        except Exception as e:
            print(f"Failed to send alert: {e}")
    
    def check_test_health(self):
        """Check test health and send alerts if needed."""
        # Example health checks
        from visual_test_reporter import VisualTestReporter
        
        reporter = VisualTestReporter()
        recent_sessions = reporter.get_historical_data(1)
        
        if not recent_sessions:
            self.send_alert("no_tests_executed", "No tests executed in the last 24 hours", "high")
            return
        
        latest_session = recent_sessions[0]
        pass_rate = (latest_session['passed_tests'] / latest_session['total_tests']) * 100
        
        if pass_rate < 90:
            self.send_alert("low_pass_rate", f"Pass rate dropped to {pass_rate:.1f}%", "medium")
        
        if latest_session['total_duration'] > 600:  # 10 minutes
            self.send_alert("slow_execution", f"Test execution took {latest_session['total_duration']:.1f}s", "low")

if __name__ == "__main__":
    alerting = AlertingSystem()
    alerting.check_test_health()
```

## Documentation Updates

### Documentation Review Schedule
- **Monthly**: Review and update README files
- **Quarterly**: Update best practices guide
- **Annually**: Comprehensive documentation overhaul

### Documentation Checklist
- [ ] README.md is current and accurate
- [ ] BEST_PRACTICES.md reflects current standards
- [ ] API documentation matches implementation
- [ ] Troubleshooting guide is comprehensive
- [ ] Installation instructions are tested
- [ ] Examples are working and relevant

## Conclusion

Regular maintenance following these procedures ensures:
- **Test Reliability**: Consistent and dependable test results
- **Performance Optimization**: Efficient test execution
- **Early Issue Detection**: Proactive problem identification
- **System Health**: Optimal test environment condition
- **Documentation Currency**: Up-to-date and useful documentation

Implement these procedures systematically to maintain a robust and effective visual testing suite.
