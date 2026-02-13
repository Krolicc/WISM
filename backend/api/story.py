from fastapi import APIRouter, HTTPException
from backend.models import (
    GeneratePlotRequest,
    GenerateFramesRequest,
    PlotResponse,
    FramesResponse
)
from backend.services.story_service import (
    generate_plot,
    generate_frames_for_plot_point
)

router = APIRouter()

@router.post("/plot/generate", response_model=PlotResponse)
async def handle_generate_plot(request: GeneratePlotRequest):
    """
    API endpoint to generate the initial plot structure from a user prompt.
    """
    try:
        plot_response = await generate_plot(request.prompt)
        if not plot_response.plot_points:
            raise HTTPException(status_code=500, detail="Failed to generate a plot from the model.")
        return plot_response
    except Exception as e:
        # Log the error for debugging
        print(f"Error in /plot/generate endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/frames/generate-for-plot-point", response_model=FramesResponse)
async def handle_generate_frames(request: GenerateFramesRequest):
    """
    API endpoint to generate comic frames for a single, specific plot point.
    """
    try:
        frames_response = await generate_frames_for_plot_point(request.plot_point)
        if not frames_response.frames:
            raise HTTPException(status_code=500, detail="Failed to generate frames from the model.")
        return frames_response
    except Exception as e:
        print(f"Error in /frames/generate-for-plot-point endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
