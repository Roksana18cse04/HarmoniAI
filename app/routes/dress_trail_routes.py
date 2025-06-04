from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.agents.dress_trail_agents import dress_trial_agent
from app.schemas.Image_To_Image import DressTrialImageRequest
from app.utils.r2_uploader import upload_to_r2  # make sure this exists
import uuid
router = APIRouter()
@router.post("/dress-trial-image-generate")
async def dress_trial_image_generate(
    cloth_image: UploadFile = File(...),
    human_image: UploadFile = File(...),
    mask_image: UploadFile = File(...),
    intend: str = Form(...)
):
    try:
        # 🔥 Read file bytes
        cloth_bytes = await cloth_image.read()
        human_bytes = await human_image.read()
        mask_bytes = await mask_image.read()

        # 🧠 Generate unique keys using UUID
        cloth_key = f"cloths/{uuid.uuid4().hex}_{cloth_image.filename}"
        human_key = f"humans/{uuid.uuid4().hex}_{human_image.filename}"
        mask_key = f"masks/{uuid.uuid4().hex}_{mask_image.filename}"

        # 🚀 Upload to R2
        cloth_image_url = upload_to_r2(cloth_bytes, cloth_key)
        human_image_url = upload_to_r2(human_bytes, human_key)
        mask_image_url = upload_to_r2(mask_bytes, mask_key)

        print(f"Uploaded cloth to: {cloth_image_url}")
        print(f"Uploaded human to: {human_image_url}")
        print(f"Uploaded mask to: {mask_image_url}")

        # 🧠 Create request
        data = DressTrialImageRequest(
            cloth_image_url=cloth_image_url,
            human_image_url=human_image_url,
            mask_image_url=mask_image_url,
            category=intend  # Make sure this matches your Enum
        )

        result = dress_trial_agent(data)

        return {
            "status": "success",
            "cloth_image_url": cloth_image_url,
            "human_image_url": human_image_url,
            "mask_image_url": mask_image_url,
            "new_image_url": result.get("output")
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})