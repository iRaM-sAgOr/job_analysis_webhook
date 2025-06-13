"""
Webhook endpoints for job analysis processing.
Handles incoming webhook requests and processes job data using LLM services.
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.schemas.job import JobAnalysisWebhook, JobAnalysisResponse
from app.utils.logging import get_logger
from app.middlewares.webhookSecurity import verify_webhook_signature_middleware
from app.services.job_analyzer import MultiLLMJobAnalyzer
from app.core.config import settings
from app.utils.llm_data_postprocessing import post_process_llm_output

# Initialize router and logger
router = APIRouter()
logger = get_logger(__name__)

# Background processing function for job analysis
def process_job_in_background(job_id: str, url: str, analyzer: MultiLLMJobAnalyzer):
    try:
        scrapped_data = analyzer.scraper.scrape_url(url)
        if scrapped_data.get("success"):
            analyzed_content = analyzer.analyze_job_post(
                scrapped_data["content"])
            # Post-process the output for background tasks too
            processed_result = post_process_llm_output(analyzed_content)
            print(f"Job analysis completed for job_id: {processed_result}")
        else:
            logger.error(f"Failed to scrape job data for job_id: {job_id}")
    except Exception as e:
        logger.error(
            f"Background processing failed for job_id {job_id}: {str(e)}")


@router.post("/job-analysis", response_model=JobAnalysisResponse)
async def job_analysis_webhook(
    webhook_data: JobAnalysisWebhook,
    background_tasks: BackgroundTasks,
    # dependencies=Depends(verify_webhook_signature_middleware),
):
    """
    Process job analysis webhook requests.

    Args:
        webhook_data: Job analysis data from webhook
        background_tasks: FastAPI background tasks for async processing
        llm_service: Injected LLM service dependency

    Returns:
        JobAnalysisResponse: Analysis results

    Raises:
        HTTPException: For validation or processing errors
    """
    try:
        logger.info(
            f"Processing job analysis for job_id: {webhook_data.job_id}")

        analyzer = MultiLLMJobAnalyzer(
            llm_provider=settings.LLM_PROVIDER,
            api_key=settings.LLM_API_KEY,
            model_name=settings.LLM_MODEL_NAME
        )

        if webhook_data.async_processing:

            background_tasks.add_task(
                process_job_in_background,
                webhook_data.job_id,
                webhook_data.url,
                analyzer
            )
            print("Yes, async processing enabled")
            return JobAnalysisResponse(
                status="accepted",
                job_id=webhook_data.job_id,
                message="Job analysis started in background"
            )
        else:
            # print("No, async processing disabled")
            scrapped_data = analyzer.scraper.scrape_url(webhook_data.url)
            if scrapped_data.get("success"):
                analyzed_content = analyzer.analyze_job_post(
                    scrapped_data["content"])
                logger.info(
                    f"Job analysis completed for job_id: {webhook_data.job_id}")
                # print(f"Job analysis completed for job_id: {analyzed_content}")

                # Post-process LLM output to get clean JSON
                result_dict = post_process_llm_output(analyzed_content)

                return JobAnalysisResponse(
                    status="completed",
                    job_id=webhook_data.job_id,
                    result=result_dict,
                    message="Job analysis completed successfully"
                )
            else:
                raise HTTPException(
                    status_code=400, detail="Failed to scrape job data")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing job analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def webhook_health():
    """Health check endpoint for webhook service."""
    return {"status": "healthy", "service": "webhook-handler"}
