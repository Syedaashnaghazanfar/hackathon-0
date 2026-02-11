"""
Social Media Monitoring package for Gold Tier AI Employee.

Provides platform-specific monitors for detecting social media interactions
(comments, DMs, mentions) on Facebook, Instagram, and Twitter/X.
"""

from .base_monitor import BaseSocialMonitor

__all__ = ["BaseSocialMonitor"]
