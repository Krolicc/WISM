
import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.services.comfyui_service import comfyui_service, ComfyUIService
from app.services.prompt_parser import prompt_parser_service, PromptParserService


router = APIRouter()

@router.post("/generate-image/")
async def generate_image(
    prompt_object: dict = Body(...),
    seed: int = 123,
    comfy_service: ComfyUIService = Depends(lambda: comfyui_service),
    parser_service: PromptParserService = Depends(lambda: prompt_parser_service)
):
    """
    Generates an image based on a structured prompt object.
    
    - **prompt_object**: A JSON object detailing the scene.
    - **seed**: The random seed for the generation process.
    """
    try:
        # 1. Parse the structured prompt into a single string
        final_prompt = parser_service.parse(prompt_object)
        
        # 2. Generate the image using the ComfyUI service
        image_bytes = await comfy_service.generate_image(final_prompt, seed)
        
        # 3. Return the image as a streaming response
        return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png")
    except Exception as e:
        # Rudimentary error handling
        return {"error": str(e)}

