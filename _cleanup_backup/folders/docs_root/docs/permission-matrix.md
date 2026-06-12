# Permission Matrix Documentation

## Overview

This document describes the Role-Based Access Control (RBAC) system with fine-grained permissions for the Resume Parser application.

## Roles

The system supports four roles:

1. **admin** - Full system access
2. **recruiter** - Recruiting operations
3. **hr** - HR operations
4. **viewer** - Read-only access

## Permissions

### Candidate Module
- `candidate.view` - View candidate profiles
- `candidate.create` - Create/upload new candidates
- `candidate.edit` - Edit candidate information
- `candidate.delete` - Delete candidates

### Job Module
- `job.view` - View job postings
- `job.create` - Create new job postings
- `job.edit` - Edit job postings
- `job.delete` - Delete job postings

### Matching Module
- `matching.view` - View matching results
- `matching.run` - Run matching algorithms

### Analytics Module
- `analytics.view` - View analytics dashboards
- `analytics.export` - Export analytics data

### Labeling Module
- `labeling.view` - View candidate labels
- `labeling.edit` - Edit candidate labels

### User Management
- `user.view` - View user accounts
- `user.create` - Create new user accounts
- `user.edit` - Edit user accounts
- `user.delete` - Delete user accounts

### System Settings
- `settings.manage` - Manage system settings

## Permission Matrix

| Permission | Admin | Recruiter | HR | Viewer |
| ---------- | ----- | --------- | -- | ------ |
| **Candidate Module** |
| candidate.view | ✓ | ✓ | ✓ | ✓ |
| candidate.create | ✓ | ✓ | ✗ | ✗ |
| candidate.edit | ✓ | ✓ | ✓ | ✗ |
| candidate.delete | ✓ | ✓ | ✗ | ✗ |
| **Job Module** |
| job.view | ✓ | ✓ | ✗ | ✗ |
| job.create | ✓ | ✓ | ✗ | ✗ |
| job.edit | ✓ | ✓ | ✗ | ✗ |
| job.delete | ✓ | ✓ | ✗ | ✗ |
| **Matching Module** |
| matching.view | ✓ | ✓ | ✗ | ✗ |
| matching.run | ✓ | ✗ | ✗ | ✗ |
| **Analytics Module** |
| analytics.view | ✓ | ✓ | ✓ | ✓ |
| analytics.export | ✓ | ✗ | ✗ | ✗ |
| **Labeling Module** |
| labeling.view | ✓ | ✗ | ✗ | ✗ |
| labeling.edit | ✓ | ✗ | ✗ | ✗ |
| **User Management** |
| user.view | ✓ | ✗ | ✗ | ✗ |
| user.create | ✓ | ✗ | ✗ | ✗ |
| user.edit | ✓ | ✗ | ✗ | ✗ |
| user.delete | ✓ | ✗ | ✗ | ✗ |
| **System Settings** |
| settings.manage | ✓ | ✗ | ✗ | ✗ |

## API Protection Strategy

### Role-Based Authorization (Existing)
```python
@router.get("/api/v1/candidates")
def get_candidates(current_user=Depends(require_role("admin", "recruiter"))):
    # Only admin and recruiter can access
    pass
```

### Permission-Based Authorization (New)
```python
@router.delete("/api/v1/candidates/{id}")
def delete_candidate(
    candidate_id: str,
    current_user=Depends(require_permission("candidate.delete"))
):
    # Only users with candidate.delete permission can access
    pass
```

### Hybrid Approach
Both systems work together. You can use either:
- `require_role("admin")` - Role-based check
- `require_permission("candidate.delete")` - Permission-based check

## Permission Inheritance

- **Admin Role**: Automatically has all permissions (bypasses permission check)
- **Other Roles**: Must have explicit permission assignments in `role_permissions` table

## Usage Examples

### Using Role-Based Check
```python
from app.api.deps import require_role

@router.get("/admin/dashboard")
def admin_dashboard(current_user=Depends(require_role("admin"))):
    return {"message": "Admin dashboard"}
```

### Using Permission-Based Check
```python
from app.api.deps import require_permission

@router.delete("/api/v1/candidates/{id}")
def delete_candidate(
    candidate_id: str,
    current_user=Depends(require_permission("candidate.delete"))
):
    # Delete candidate
    pass
```

### Combining Both
```python
@router.put("/api/v1/candidates/{id}")
def update_candidate(
    candidate_id: str,
    current_user=Depends(require_role("admin", "recruiter")),
    db: Session = Depends(get_db)
):
    # Update candidate
    pass
```

## Default Permissions

The system is initialized with the following default permissions:

### Admin
- All permissions (18 total)

### Recruiter
- candidate.view, create, edit, delete
- job.view, create, edit, delete
- matching.view
- analytics.view

### HR
- candidate.view, edit
- analytics.view

### Viewer
- candidate.view
- analytics.view

## API Endpoints

### User Management (Admin Only)
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/{id}` - Get user details
- `POST /api/v1/users` - Create user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user
- `PUT /api/v1/users/{id}/role` - Change user role
- `PUT /api/v1/users/{id}/activate` - Activate user
- `PUT /api/v1/users/{id}/deactivate` - Deactivate user

### Permission Management (Admin Only)
- `GET /api/v1/permissions` - List all permissions
- `GET /api/v1/roles` - List all roles
- `GET /api/v1/roles/{role}/permissions` - Get role permissions
- `PUT /api/v1/roles/{role}/permissions` - Update role permissions

## Security Notes

1. **Admin Role**: Cannot modify admin permissions (always has all permissions)
2. **Self-Modification**: Users cannot delete or deactivate themselves
3. **Audit Logging**: All user and permission changes are logged
4. **Rate Limiting**: User management endpoints are rate-limited
5. **Backward Compatibility**: Existing `require_role()` checks continue to work

## Database Schema

### Permissions Table
```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    module VARCHAR(50),
    created_at TIMESTAMP
);
```

### Role Permissions Table
```sql
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP,
    UNIQUE(role, permission_id)
);
```

## Migration

To apply the permissions schema:

```bash
cd backend
python -m alembic upgrade head
```

This will create the permissions tables and seed default permissions for all roles.
