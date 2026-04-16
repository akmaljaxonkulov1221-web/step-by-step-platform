# Logs Directory

This directory contains application logs for the Step by Step Education Platform.

## Log Files

### Application Logs
- `app.log` - Main application log file
- `error.log` - Error-specific log file
- `access.log` - Access log file (if enabled)
- `security.log` - Security-related events

### Log Rotation
Logs are automatically rotated to prevent disk space issues:
- Maximum file size: 1MB
- Backup count: 5 files
- Compression: Enabled for old logs

## Log Levels

### DEBUG
Detailed information, typically of interest only when diagnosing problems.

### INFO
Confirmation that things are working as expected.

### WARNING
An indication that something unexpected happened, or indicative of some problem in the near future (e.g. 'disk space low'). The software is still working as expected.

### ERROR
Due to a more serious problem, the software has not been able to perform some function.

### CRITICAL
A serious error, indicating that the program itself may be unable to continue running.

## Log Format

### Standard Format
```
2024-01-01 12:00:00,000 - app_name - LEVEL - Message
```

### Access Log Format
```
2024-01-01 12:00:00,000 - METHOD URL - STATUS - IP - User-Agent
```

### Security Log Format
```
2024-01-01 12:00:00,000 - EVENT_TYPE - USER - IP - DETAILS
```

## Configuration

Log configuration is managed through the `config.py` file:

```python
# Log configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 1024 * 1024))  # 1MB
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
```

## Monitoring

### Log Monitoring
- Use `tail -f app.log` to monitor real-time logs
- Use `grep "ERROR" app.log` to filter errors
- Use `grep "CRITICAL" app.log` for critical issues

### Log Analysis
- Parse logs with Python scripts
- Use log analysis tools like ELK stack
- Set up automated alerts for critical errors

## Security

### Sensitive Information
- Passwords are never logged
- Personal data is masked in logs
- Security events are logged separately

### Access Control
- Log files should have restricted permissions
- Only administrators should access log files
- Regular audit of log access

## Troubleshooting

### Common Issues
1. **Log file not created**: Check file permissions
2. **No logs appearing**: Check log level configuration
3. **Disk space full**: Enable log rotation
4. **Corrupted logs**: Check for proper log formatting

### Debugging with Logs
1. Set log level to DEBUG
2. Restart the application
3. Reproduce the issue
4. Check the logs for relevant messages

## Best Practices

1. **Regular Log Review**: Check logs regularly for issues
2. **Log Rotation**: Always enable log rotation
3. **Security**: Never log sensitive information
4. **Performance**: Avoid excessive logging in production
5. **Monitoring**: Set up automated log monitoring

## Maintenance

### Daily Tasks
- Check for error logs
- Monitor disk space
- Review security logs

### Weekly Tasks
- Rotate old log files
- Analyze log patterns
- Update log configuration if needed

### Monthly Tasks
- Archive old logs
- Review log retention policy
- Update log analysis tools

## Notes

- Logs are essential for troubleshooting
- Always monitor log file sizes
- Set up proper log rotation
- Protect sensitive information in logs
- Regular log review is recommended
