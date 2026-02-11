"""
Keyword Filter for Gold Tier AI Employee.

Intelligently classifies social media interactions by priority based on keyword matching.
Loads keywords from Company_Handbook.md, falls back to .env, then hardcoded defaults.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from ..models.social_interaction import SocialInteractionSchema


logger = logging.getLogger(__name__)


@dataclass
class KeywordRule:
    """
    Represents a keyword classification rule.

    Attributes:
        keywords: List of keyword phrases
        priority: Priority level (HIGH, MEDIUM, LOW)
        category: Category description (e.g., "urgent_inquiries", "business_opportunities")
    """
    keywords: List[str]
    priority: str
    category: str


class KeywordFilter:
    """
    Analyzes social media interactions and classifies priority based on keywords.

    Priority Levels:
    - HIGH: Urgent customer inquiries (urgent, help, pricing, emergency, etc.)
    - MEDIUM: Business opportunities (project, quote, proposal, consulting, etc.)
    - LOW: Everything else (generic messages, spam, FYI, etc.)

    Keyword Sources (in order of precedence):
    1. Company_Handbook.md (user-defined in vault)
    2. .env environment variables (SOCIAL_HIGH_PRIORITY_KEYWORDS, etc.)
    3. Hardcoded defaults (fallback)

    Usage:
        filter = KeywordFilter()
        interaction = SocialInteractionSchema(...)
        updated_interaction = filter.classify_interaction(interaction)
    """

    # Default keywords (fallback if no config found)
    DEFAULT_HIGH_KEYWORDS = [
        "urgent", "asap", "emergency", "critical", "immediately",
        "help", "support", "issue", "problem", "error", "bug",
        "pricing", "price", "cost", "invoice", "payment", "billing",
        "client", "customer", "complaint", "refund", "cancellation"
    ]

    DEFAULT_MEDIUM_KEYWORDS = [
        "project", "quote", "proposal", "consulting", "services",
        "hire", "contract", "opportunity", "business", "partnership",
        "meeting", "call", "discuss", "proposal", "estimate"
    ]

    def __init__(self, vault_root: str = "AI_Employee_Vault"):
        """
        Initialize the keyword filter.

        Args:
            vault_root: Path to Obsidian vault root
        """
        self.vault_root = Path(vault_root)
        self.company_handbook_path = self.vault_root / "Company_Handbook.md"

        # Load keyword rules
        self.high_priority_rules = self._load_keyword_rules("HIGH")
        self.medium_priority_rules = self._load_keyword_rules("MEDIUM")

        self.logger.info(
            f"KeywordFilter initialized: {len(self.high_priority_rules)} HIGH rules, "
            f"{len(self.medium_priority_rules)} MEDIUM rules"
        )

    def _load_keyword_rules(self, priority: str) -> List[KeywordRule]:
        """
        Load keyword rules for a priority level.

        Args:
            priority: Priority level (HIGH, MEDIUM)

        Returns:
            List of KeywordRule objects

        Loading order:
        1. Try Company_Handbook.md
        2. Try .env environment variables
        3. Use hardcoded defaults
        """
        # Try loading from Company_Handbook.md
        rules = self._load_from_handbook(priority)
        if rules:
            self.logger.info(f"Loaded {len(rules)} {priority} priority rules from Company_Handbook.md")
            return rules

        # Try loading from .env
        rules = self._load_from_env(priority)
        if rules:
            self.logger.info(f"Loaded {len(rules)} {priority} priority rules from .env")
            return rules

        # Use hardcoded defaults
        default_keywords = self.DEFAULT_HIGH_KEYWORDS if priority == "HIGH" else self.DEFAULT_MEDIUM_KEYWORDS
        category = "urgent_inquiries" if priority == "HIGH" else "business_opportunities"

        self.logger.warning(f"Using hardcoded {priority} priority keywords (no config found)")
        return [KeywordRule(keywords=default_keywords, priority=priority, category=category)]

    def _load_from_handbook(self, priority: str) -> Optional[List[KeywordRule]]:
        """
        Load keyword rules from Company_Handbook.md.

        Expected format in Company_Handbook.md:

        ## Social Media Priority Keywords

        ### HIGH Priority
        - urgent, help, pricing
        - Category: urgent_inquiries

        ### MEDIUM Priority
        - project, quote, consulting
        - Category: business_opportunities

        Args:
            priority: Priority level to load

        Returns:
            List of KeywordRule objects, or None if section not found
        """
        if not self.company_handbook_path.exists():
            return None

        try:
            with open(self.company_handbook_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for social media keywords section
            # Try multiple section heading formats
            patterns = [
                r"## Social Media.*?(?=##|\Z)",  # ## Social Media...
                r"## Priority Keywords.*?(?=##|\Z)",  # ## Priority Keywords...
                r"# Social Media.*?(?=#|\Z)",  # # Social Media...
            ]

            keywords_section = None
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    keywords_section = match.group(0)
                    break

            if not keywords_section:
                return None

            # Parse priority-specific keywords
            priority_pattern = rf"###?\s*{priority}\s+Priority.*?(?=###?|\Z)"
            priority_match = re.search(priority_pattern, keywords_section, re.IGNORECASE | re.DOTALL)

            if not priority_match:
                return None

            priority_section = priority_match.group(0)

            # Extract keywords (comma-separated or bullet list)
            keywords = []
            # Match: "keyword1, keyword2, keyword3" or "- keyword1\n- keyword2"
            keyword_matches = re.findall(
                r"(?:^|[\n-])\s*([a-zA-Z][a-zA-Z0-9\s]+)(?:[,.\n]|$)",
                priority_section
            )

            for match in keyword_matches:
                keyword = match.strip().lower()
                if keyword and len(keyword) > 2:  # Minimum 3 chars
                    keywords.append(keyword)

            # Extract category if present
            category_match = re.search(r"Category:\s*([a-zA-Z_]+)", priority_section, re.IGNORECASE)
            category = category_match.group(1) if category_match else (
                "urgent_inquiries" if priority == "HIGH" else "business_opportunities"
            )

            if keywords:
                return [KeywordRule(keywords=keywords, priority=priority, category=category)]

        except Exception as e:
            self.logger.error(f"Error loading keywords from handbook: {e}")

        return None

    def _load_from_env(self, priority: str) -> Optional[List[KeywordRule]]:
        """
        Load keyword rules from environment variables.

        Args:
            priority: Priority level to load

        Returns:
            List of KeywordRule objects, or None if env vars not set
        """
        from os import getenv

        # Map priority to environment variable name
        env_var_map = {
            "HIGH": "SOCIAL_HIGH_PRIORITY_KEYWORDS",
            "MEDIUM": "SOCIAL_BUSINESS_KEYWORDS",
        }

        env_var = env_var_map.get(priority)
        if not env_var:
            return None

        env_value = getenv(env_var)
        if not env_value:
            return None

        # Parse comma-separated keywords
        keywords = [k.strip().lower() for k in env_value.split(",") if k.strip()]

        if keywords:
            category = "urgent_inquiries" if priority == "HIGH" else "business_opportunities"
            return [KeywordRule(keywords=keywords, priority=priority, category=category)]

        return None

    def classify_interaction(self, interaction: SocialInteractionSchema) -> SocialInteractionSchema:
        """
        Classify an interaction's priority based on keyword matching.

        Args:
            interaction: SocialInteractionSchema object to classify

        Returns:
            Updated SocialInteractionSchema with priority and priority_reason set

        Classification logic:
        1. Check HIGH priority keywords first (urgent, pricing, help, etc.)
        2. If no match, check MEDIUM priority keywords (project, quote, etc.)
        3. If no match, set priority to LOW (no action item will be created)
        """
        content_lower = interaction.content.lower()
        author_lower = interaction.author.lower()

        # Check HIGH priority rules
        for rule in self.high_priority_rules:
            for keyword in rule.keywords:
                # Check if keyword appears in content or author
                if keyword.lower() in content_lower or keyword.lower() in author_lower:
                    interaction.priority = "HIGH"
                    interaction.priority_reason = f"Matched HIGH priority keyword: '{keyword}' ({rule.category})"
                    self.logger.debug(
                        f"Classified as HIGH: '{keyword}' matched in content from {interaction.author}"
                    )
                    return interaction

        # Check MEDIUM priority rules
        for rule in self.medium_priority_rules:
            for keyword in rule.keywords:
                if keyword.lower() in content_lower or keyword.lower() in author_lower:
                    interaction.priority = "MEDIUM"
                    interaction.priority_reason = f"Matched MEDIUM priority keyword: '{keyword}' ({rule.category})"
                    self.logger.debug(
                        f"Classified as MEDIUM: '{keyword}' matched in content from {interaction.author}"
                    )
                    return interaction

        # No keyword match - LOW priority
        interaction.priority = "LOW"
        interaction.priority_reason = "No priority keywords matched"
        self.logger.debug(f"Classified as LOW: No keywords matched in content from {interaction.author}")

        return interaction

    def batch_classify(self, interactions: List[SocialInteractionSchema]) -> List[SocialInteractionSchema]:
        """
        Classify multiple interactions at once.

        Args:
            interactions: List of SocialInteractionSchema objects

        Returns:
            List of updated SocialInteractionSchema objects with priorities set

        Stats:
            Logs summary: X HIGH, Y MEDIUM, Z LOW
        """
        high_count = 0
        medium_count = 0
        low_count = 0

        classified = []
        for interaction in interactions:
            updated = self.classify_interaction(interaction)
            classified.append(updated)

            if updated.priority == "HIGH":
                high_count += 1
            elif updated.priority == "MEDIUM":
                medium_count += 1
            else:
                low_count += 1

        self.logger.info(
            f"Batch classification complete: {high_count} HIGH, "
            f"{medium_count} MEDIUM, {low_count} LOW"
        )

        return classified

    def add_custom_keyword(self, keyword: str, priority: str, category: str = "custom") -> None:
        """
        Add a custom keyword rule at runtime.

        Args:
            keyword: Keyword phrase to add
            priority: Priority level (HIGH, MEDIUM)
            category: Category description
        """
        priority = priority.upper()
        if priority not in ["HIGH", "MEDIUM"]:
            raise ValueError("Priority must be HIGH or MEDIUM")

        rule = KeywordRule(
            keywords=[keyword.lower()],
            priority=priority,
            category=category
        )

        if priority == "HIGH":
            self.high_priority_rules.append(rule)
        else:
            self.medium_priority_rules.append(rule)

        self.logger.info(f"Added custom {priority} priority keyword: '{keyword}' ({category})")

    def get_keywords_summary(self) -> Dict[str, List[str]]:
        """
        Get summary of all loaded keywords.

        Returns:
            Dict with 'HIGH' and 'MEDIUM' keys, each containing list of keywords
        """
        summary = {
            "HIGH": [],
            "MEDIUM": []
        }

        for rule in self.high_priority_rules:
            summary["HIGH"].extend(rule.keywords)

        for rule in self.medium_priority_rules:
            summary["MEDIUM"].extend(rule.keywords)

        # Remove duplicates
        summary["HIGH"] = list(set(summary["HIGH"]))
        summary["MEDIUM"] = list(set(summary["MEDIUM"]))

        return summary
