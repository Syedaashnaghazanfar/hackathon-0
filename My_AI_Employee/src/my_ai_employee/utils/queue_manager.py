"""
Queue manager for offline resilience.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class QueueManager:
    """Manage offline operation queue."""
    def __init__(self, queue_file: str):
        self.queue_file = Path(queue_file)
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
    def enqueue(self, operation: Dict[str, Any]) -> bool:
        try:
            operation['queued_at'] = datetime.now(timezone.utc).isoformat()
            with open(self.queue_file, 'a') as f:
                f.write(json.dumps(operation) + '\n')
            logger.info(f"Operation queued: {operation.get('operation_type')}")
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue: {e}")
            return False
    def dequeue(self) -> Optional[Dict[str, Any]]:
        try:
            if not self.queue_file.exists():
                return None
            operations = []
            with open(self.queue_file, 'r') as f:
                for line in f:
                    if line.strip():
                        operations.append(json.loads(line))
            if not operations:
                return None
            operation = operations[0]
            with open(self.queue_file, 'w') as f:
                for op in operations[1:]:
                    f.write(json.dumps(op) + '\n')
            return operation
        except Exception as e:
            logger.error(f"Failed to dequeue: {e}")
            return None
    def clear(self) -> bool:
        try:
            if self.queue_file.exists():
                self.queue_file.unlink()
            return True
        except:
            return False
