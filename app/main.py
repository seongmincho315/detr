import base64
import io
import os
from typing import List

from fastapi import FastAPI
from PIL import Image
from pydantic import BaseModel

from app.predictor import Predictor

app = FastAPI(title="DETR Layout Server")

predictor = Predictor(
    model_name=os.getenv("MODEL_NAME", "docling_layout_heron"),
    device=os.getenv("DEVICE", "cpu"),
    confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.3")),
)


class DetectRequest(BaseModel):
    images: List[str]  # base64 인코딩된 PNG/JPEG 페이지 이미지 목록


class Region(BaseModel):
    label: str
    confidence: float
    l: float
    t: float
    r: float
    b: float


class DetectResponse(BaseModel):
    results: List[List[Region]]  # 이미지별 감지된 영역 목록


def _decode_image(b64: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64)))


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.post("/detect", response_model=DetectResponse)
async def detect(request: DetectRequest):
    images = [_decode_image(b64) for b64 in request.images]
    results = predictor.predict_batch(images)
    return {"results": results}
