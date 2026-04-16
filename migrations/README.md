# Database Migrations

This directory contains database migration files for the Step by Step Education Platform.

## Migration Structure

Migrations are organized chronologically with the following naming convention:
- `001_initial_schema.py` - Initial database schema
- `002_add_user_roles.py` - Add user roles and permissions
- `003_add_test_system.py` - Add test and result tables
- `004_add_notifications.py` - Add notification system
- `005_add_audit_logs.py` - Add audit logging

## Running Migrations

### Development
```bash
# Create new migration
python manage.py db migrate -m "Add new feature"

# Apply migrations
python manage.py db upgrade

# Rollback migration
python manage.py db downgrade
```

### Production
```bash
# Apply migrations with backup
python manage.py db upgrade
python manage.py db backup
```

## Migration Files

### 001_initial_schema.py
Creates the basic database schema:
- Users table
- Groups table
- Subjects table
- Basic relationships

### 002_add_user_roles.py
Adds user role system:
- Role-based access control
- Permission system
- User role assignments

### 003_add_test_system.py
Adds test functionality:
- Tests table
- Questions table
- Results table
- Test sessions

### 004_add_notifications.py
Adds notification system:
- Notifications table
- User preferences
- Email notifications

### 005_add_audit_logs.py
Adds audit logging:
- Audit logs table
- User activity tracking
- System events

## Best Practices

1. Always test migrations in development first
2. Create backups before running migrations in production
3. Use descriptive migration messages
4. Keep migrations simple and focused
5. Test rollback procedures
6. Document breaking changes

## Troubleshooting

### Migration Conflicts
If you encounter migration conflicts:
1. Identify the conflicting migrations
2. Resolve the conflict manually
3. Create a new migration to fix the issue

### Rollback Issues
If rollback fails:
1. Check database state
2. Restore from backup if needed
3. Create manual fix migration

### Performance Issues
For large databases:
1. Run migrations during maintenance windows
2. Use batch processing for large updates
3. Monitor database performance

## Notes

- Always backup before running migrations
- Test migrations thoroughly
- Document any breaking changes
- Monitor database performance after migrations
