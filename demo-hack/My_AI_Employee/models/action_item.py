"""
Action Item data model for Silver Tier AI Employee.
Extends Bronze tier schema with approval workflow fields.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal


@dataclass
class ActionItemSchema:
    """
    Silver Tier action item schema.

    Extends Bronze tier with approval workflow fields:
    - approval_required: Whether this action needs human approval
    - priority: Low, Medium, High (based on risk assessment)
    - risk_level: Low, Medium, High (determines approval threshold)
    - action_type: Type of action (email, linkedin_post, whatsapp, payment, etc.)
    """

    # Bronze tier fields (inherited)
    type: str  # file_drop, email, linkedin_post, whatsapp, payment
    received: str  # ISO 8601 timestamp
    status: str  # pending, processing, processed, approved, rejected, failed
    source_path: Optional[str] = None  # Original file path for file_drop type

    # Silver tier fields (new)
    approval_required: bool = False
    priority: Literal["Low", "Medium", "High"] = "Low"
    risk_level: Literal["Low", "Medium", "High"] = "Low"
    action_type: Optional[str] = None  # send_email, publish_post, send_message, process_payment

    # Additional metadata
    sender: Optional[str] = None  # Email sender or message sender
    subject: Optional[str] = None  # Email subject or message title
    body: Optional[str] = None  # Email body or message content

    # Approval workflow tracking
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None  # ISO 8601 timestamp
    rejected_by: Optional[str] = None
    rejected_at: Optional[str] = None  # ISO 8601 timestamp
    rejection_reason: Optional[str] = None

    # Execution tracking
    executed_at: Optional[str] = None  # ISO 8601 timestamp
    execution_result: Optional[str] = None
    retry_count: int = 0
    last_error: Optional[str] = None


def determine_risk_level(action_type: str, content: dict) -> str:
    """
    Determine risk level based on action type and content.

    Risk levels from Company_Handbook.md Section 6.4:
    - Low: Email responses to known contacts
    - Medium: LinkedIn posts, WhatsApp messages
    - High: Payments, financial transactions

    Args:
        action_type: Type of action (send_email, publish_post, etc.)
        content: Action content for analysis

    Returns:
        Risk level: "Low", "Medium", or "High"
    """
    if action_type in ["process_payment", "send_invoice", "financial_transaction"]:
        return "High"
    elif action_type in ["publish_post", "send_message", "linkedin_post"]:
        return "Medium"
    elif action_type in ["send_email", "reply_email"]:
        # Check if recipient is known contact (could be enhanced)
        return "Low"
    else:
        # Default to Medium for unknown action types
        return "Medium"


def determine_priority(risk_level: str, urgency_keywords: list = None, sender: str = None, subject: str = None) -> str:
    """
    Determine priority based on risk level, urgency keywords, sender, and subject.

    Priority levels:
    - High: Urgent keywords OR high risk level
    - Low: Newsletter/automated emails OR low risk + no urgency
    - Medium: Everything else

    Args:
        risk_level: Risk level (Low, Medium, High)
        urgency_keywords: List of urgency keywords found in content
        sender: Email sender address (optional, for better detection)
        subject: Email subject line (optional, for better detection)

    Returns:
        Priority: "Low", "Medium", or "High"
    """
    if urgency_keywords is None:
        urgency_keywords = []

    # Check for urgent keywords
    urgent_keywords = ["urgent", "asap", "emergency", "critical", "immediate"]
    has_urgent = any(keyword in urgency_keywords for keyword in urgent_keywords)

    # High priority: urgent keywords OR high risk
    if risk_level == "High" or has_urgent:
        return "High"

    # Low priority indicators in sender or subject
    low_priority_indicators = [
        'newsletter', 'unsubscribe', 'no-reply', 'noreply',
        'digest', 'notification', 'automated', 'do-not-reply',
        'donotreply', 'marketing', 'promo', 'promotional'
    ]

    # Check sender address
    if sender:
        sender_lower = sender.lower()
        if any(indicator in sender_lower for indicator in low_priority_indicators):
            return "Low"

    # Check subject line
    if subject:
        subject_lower = subject.lower()
        if any(indicator in subject_lower for indicator in low_priority_indicators):
            return "Low"

    # Medium priority: medium risk OR default
    if risk_level == "Medium":
        return "Medium"

    # Default to Low for low risk with no urgency
    return "Low"
