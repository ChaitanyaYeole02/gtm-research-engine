import time
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import ORJSONResponse, StreamingResponse

from app.core import RunMetrics
from app.models import BatchResearchRequest, BatchResearchResponse
from app.services import ResearchPipeline, QueryGenerator
from app.streaming import ResearchStreamGenerator

router = APIRouter()


@router.post(
    path="/research/batch", 
    response_model=BatchResearchResponse, 
    response_class=ORJSONResponse,
)
async def research_batch(
    payload: BatchResearchRequest
) -> BatchResearchResponse:
    run_id = str(uuid.uuid4())

    metrics = RunMetrics(start_time=time.perf_counter())

    start_time = time.time()

    query_generator = QueryGenerator()
    strategies = await query_generator.generate_strategies(
        research_goal=payload.research_goal,
        search_depth=payload.search_depth,
    )
    end_time = time.time()
    print(f"Query generation time: {end_time - start_time} seconds")

    start_time = time.time()
    pipeline = ResearchPipeline(
        run_id=run_id,
        research_goal=payload.research_goal,
        search_depth=payload.search_depth,
        company_domains=payload.company_domains,
        strategies=strategies,
        max_parallel_searches=payload.max_parallel_searches,
        confidence_threshold=payload.confidence_threshold,
        metrics=metrics,
    )

    results, total_searches_executed = await pipeline.run()
    end_time = time.time()
    print(f"Pipeline execution time: {end_time - start_time} seconds")

    response = BatchResearchResponse(
        research_id=run_id,
        total_companies=len(payload.company_domains),
        search_strategies_generated=len(strategies),
        total_searches_executed=total_searches_executed,
        processing_time_ms=int((time.perf_counter() - metrics.start_time) * 1000),
        results=results,
        search_performance=metrics.to_dict(),
    )
    return response


@router.post("/research/batch/stream")
async def research_batch_stream(
    payload: BatchResearchRequest
) -> StreamingResponse:
    """
    Enhanced streaming research with proper SSE implementation.
    
    Features:
    - Proper SSE format with event types and IDs
    - Connection management with heartbeats
    - Error handling and recovery
    - Optimized event frequency
    - Real-time evidence processing with async domain analysis
    - Live deduplication and confidence scoring
    """
    try:
        run_id = str(uuid.uuid4())
        metrics = RunMetrics(start_time=time.perf_counter())

        # Generate strategies
        query_generator = QueryGenerator()
        strategies = await query_generator.generate_strategies(
            research_goal=payload.research_goal,
            search_depth=payload.search_depth,
        )

        # Create enhanced pipeline
        pipeline = ResearchPipeline(
            run_id=run_id,
            research_goal=payload.research_goal,
            search_depth=payload.search_depth,
            company_domains=payload.company_domains,
            strategies=strategies,
            max_parallel_searches=payload.max_parallel_searches,
            confidence_threshold=payload.confidence_threshold,
            metrics=metrics,
        )

        # Use enhanced stream generator
        stream_generator = ResearchStreamGenerator(heartbeat_interval=30)
        generator = stream_generator.generate_stream(pipeline)
        
        # Return with proper SSE headers
        return StreamingResponse(
            generator, 
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start streaming: {str(e)}")
