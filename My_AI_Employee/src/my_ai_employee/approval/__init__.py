"""
Approval workflow components for Silver Tier AI Employee.

Handles permission boundaries parsing and approval request management.
"""

from .permission_boundaries import (
    PermissionBoundaries,
    parse_permission_boundaries,
    classify_action_risk,
)
from .approval_request import (
    ApprovalRequest,
    create_approval_request,
    write_approval_request_to_vault,
    move_to_approved,
    move_to_rejected,
    validate_approval_request,
)

__all__ = [
    "PermissionBoundaries",
    "parse_permission_boundaries",
    "classify_action_risk",
    "ApprovalRequest",
    "create_approval_request",
    "write_approval_request_to_vault",
    "move_to_approved",
    "move_to_rejected",
    "validate_approval_request",
]
