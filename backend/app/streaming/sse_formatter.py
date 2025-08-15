"""
Server-Sent Events (SSE) formatting utilities.

Provides proper SSE protocol implementation with event types, IDs, retry directives,
connection management, and error handling.
"""

import time

from typing import Optional

import orjson


class SSEFormatter:
    """Proper SSE event formatter with connection management."""
    
    @staticmethod
    def format_event(
        event_type: str, 
        data: dict, 
        event_id: Optional[str] = None, 
        retry: Optional[int] = None
    ) -> str:
        """
        Format SSE event with proper headers.
        
        Args:
            event_type: The event type (e.g., 'pipeline_start', 'domain_analyzed')
            data: Event data to send as JSON
            event_id: Optional event ID for client-side tracking
            retry: Optional retry interval in milliseconds
            
        Returns:
            Properly formatted SSE event string
        """
        lines = []
        
        if event_id:
            lines.append(f"id: {event_id}")
        if retry:
            lines.append(f"retry: {retry}")
        
        lines.append(f"event: {event_type}")
        lines.append(f"data: {orjson.dumps(data).decode()}")
        lines.append("")  # Empty line to end event
        
        return "\n".join(lines) + "\n"
    
    @staticmethod
    def heartbeat() -> str:
        """Send heartbeat to keep connection alive."""
        return SSEFormatter.format_event("heartbeat", {
            "timestamp": time.time(),
            "message": "Connection alive"
        })
    
    @staticmethod
    def error(error_msg: str, recoverable: bool = True) -> str:
        """Send error event."""
        return SSEFormatter.format_event("error", {
            "message": error_msg,
            "recoverable": recoverable,
            "timestamp": time.time()
        })
    
    @staticmethod
    def connection_established(retry_interval: int = 1000) -> str:
        """Send initial connection event."""
        return SSEFormatter.format_event("connected", {
            "message": "Research pipeline connected",
            "timestamp": time.time()
        }, event_id="0", retry=retry_interval)
    
    @staticmethod
    def connection_closed(reason: str = "Normal closure") -> str:
        """Send connection closed event."""
        return SSEFormatter.format_event("disconnected", {
            "message": reason,
            "timestamp": time.time()
        })
    
    @staticmethod
    def stream_complete(total_events: int) -> str:
        """Send stream completion event."""
        return SSEFormatter.format_event("completed", {
            "message": "Research pipeline completed successfully",
            "total_events": total_events,
            "timestamp": time.time()
        })
