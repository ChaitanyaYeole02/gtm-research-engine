"""
Research pipeline stream generator for Server-Sent Events.

Handles the streaming logic for real-time research pipeline updates,
including connection management, heartbeats, and error handling.
"""

import asyncio
import time

from typing import AsyncGenerator

import orjson

from .sse_formatter import SSEFormatter
from app.services import ResearchPipeline


class ResearchStreamGenerator:
    """Enhanced SSE generator for research pipeline with proper connection management."""
    
    def __init__(self, heartbeat_interval: int = 30):
        """
        Initialize stream generator.
        
        Args:
            heartbeat_interval: Interval in seconds between heartbeat messages
        """
        self.heartbeat_interval = heartbeat_interval
    
    async def generate_stream(self, pipeline: ResearchPipeline) -> AsyncGenerator[str, None]:
        """
        Generate SSE stream for research pipeline with proper error handling.
        
        Args:
            pipeline: Research pipeline instance to stream from
            
        Yields:
            SSE-formatted event strings
        """
        last_heartbeat = time.time()
        event_count = 0
        
        try:
            # Send initial connection event
            yield SSEFormatter.connection_established()
            event_count += 1
            
            # Start streaming events from pipeline
            async for raw_event in pipeline.run_stream_optimized():
                event_count += 1
                current_time = time.time()
                
                # Send heartbeat if needed
                if current_time - last_heartbeat > self.heartbeat_interval:
                    yield SSEFormatter.heartbeat()
                    last_heartbeat = current_time
                
                # Parse and enhance the event
                try:
                    event_data = orjson.loads(raw_event)
                    event_type = event_data.get("type", "unknown")
                    
                    # Send formatted SSE event
                    yield SSEFormatter.format_event(
                        event_type, 
                        event_data, 
                        event_id=str(event_count)
                    )
                    
                except orjson.JSONDecodeError as e:
                    yield SSEFormatter.error(f"Failed to parse event: {str(e)}")
            
            # Send completion event
            yield SSEFormatter.stream_complete(event_count)
            
        except asyncio.CancelledError:
            # Client disconnected gracefully
            yield SSEFormatter.connection_closed("Client disconnected")
            raise
            
        except Exception as e:
            # Unexpected error - send error event but don't raise exception mid-stream
            yield SSEFormatter.error(f"Pipeline error: {str(e)}", recoverable=False)
            yield SSEFormatter.format_event("stream_error", {
                "message": "Stream ended due to error", 
                "error": str(e),
                "timestamp": time.time()
            })
            # Gracefully end stream instead of raising exception
