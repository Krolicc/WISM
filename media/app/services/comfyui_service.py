
import httpx
import websockets
import json
import uuid
from urllib.parse import urlparse, urljoin
from app.core.config import settings

class ComfyUIService:
    def __init__(self, server_address: str):
        self.server_address = server_address

    async def generate_image(self, prompt: str, seed: int) -> bytes:
        """Generates an image using ComfyUI and returns the image data as bytes."""
        client_id = str(uuid.uuid4())
        ws_url = f"ws://{urlparse(self.server_address).netloc}/ws?clientId={client_id}"

        # 1. Load the workflow template
        with open("app/core/workflows/sdxl_lightning_workflow.json", "r") as f:
            workflow = json.load(f)

        # 2. Modify the workflow with the given prompt and seed
        # These numbers (e.g., '6', '3') are the node IDs in the workflow JSON
        workflow["6"]["inputs"]["text"] = prompt
        workflow["3"]["inputs"]["seed"] = seed

        # 3. Queue the prompt
        prompt_id = await self._queue_prompt(workflow, client_id)
        if not prompt_id:
            raise Exception("Failed to queue prompt")

        async with websockets.connect(ws_url) as websocket:
            while True:
                out = await websocket.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message['type'] == 'executed' and message['data']['node'] == '9': # '9' is the Save Image node
                        image_data = await self._get_image(message['data']['output']['images'][0])
                        return image_data

    async def _queue_prompt(self, prompt_workflow: dict, client_id: str) -> str | None:
        """Sends the prompt workflow to the ComfyUI server."""
        url = urljoin(self.server_address, "/prompt")
        payload = {"prompt": prompt_workflow, "client_id": client_id}
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                return response.json()["prompt_id"]
            return None

    async def _get_image(self, image_info: dict) -> bytes:
        """Fetches the generated image from the ComfyUI server."""
        url = urljoin(self.server_address, f"/view?filename={image_info['filename']}&subfolder={image_info['subfolder']}&type={image_info['type']}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status() # Raise an exception for bad status codes
            return response.content

# Singleton instance
comfyui_service = ComfyUIService(settings.COMFYUI_URL)

