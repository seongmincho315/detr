from typing import FrozenSet, List

from docling_ibm_models.layoutmodel.layout_predictor import LayoutPredictor
from huggingface_hub import snapshot_download
from PIL import Image

# docling-project/docling-layout-* HF 저장소 (모델별 정확도/속도 트레이드오프 다름)
MODEL_REPOS = {
    "docling_layout_v2": "docling-project/docling-layout-old",
    "docling_layout_heron": "docling-project/docling-layout-heron",
    "docling_layout_heron_101": "docling-project/docling-layout-heron-101",
    "docling_layout_egret_medium": "docling-project/docling-layout-egret-medium",
    "docling_layout_egret_large": "docling-project/docling-layout-egret-large",
    "docling_layout_egret_xlarge": "docling-project/docling-layout-egret-xlarge",
}


class Predictor:
    def __init__(
        self,
        model_name: str = "docling_layout_heron",
        device: str = "cpu",
        confidence_threshold: float = 0.3,
        blacklist_classes: FrozenSet[str] = frozenset(),
        num_threads: int = 4,
    ):
        if model_name not in MODEL_REPOS:
            raise ValueError(f"알 수 없는 model_name입니다: {model_name} (선택지: {list(MODEL_REPOS)})")

        artifact_path = snapshot_download(repo_id=MODEL_REPOS[model_name])
        self._predictor = LayoutPredictor(
            artifact_path=artifact_path,
            device=device,
            num_threads=num_threads,
            base_threshold=confidence_threshold,
            blacklist_classes=set(blacklist_classes),
        )

    def predict(self, image: Image.Image) -> List[dict]:
        return list(self._predictor.predict(image))

    def predict_batch(self, images: List[Image.Image]) -> List[List[dict]]:
        return self._predictor.predict_batch(images)
