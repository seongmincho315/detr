"""컨테이너 안에서 실행하는 in-process 추론 스모크 테스트.
합성 페이지 이미지(제목 + 본문 텍스트)를 만들어 Predictor로 직접 추론하고,
장비(device)/감지 결과를 JSON으로 저장한다.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.environ.get("APP_DIR", "/app"))

from PIL import Image, ImageDraw  # noqa: E402

from app.predictor import Predictor  # noqa: E402


def _make_sample_page() -> Image.Image:
    img = Image.new("RGB", (1000, 1300), "white")
    draw = ImageDraw.Draw(img)
    draw.text((60, 60), "1  Introduction", fill="black")
    draw.text((60, 120), "This is a synthetic smoke-test page used to verify that", fill="black")
    draw.text((60, 145), "the layout predictor loads and runs inside the container.", fill="black")
    return img


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    model_name = os.environ.get("MODEL_NAME", "docling_layout_heron")
    device = os.environ.get("DEVICE", "cpu")
    threshold = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.3"))

    predictor = Predictor(model_name=model_name, device=device, confidence_threshold=threshold)
    regions = predictor.predict(_make_sample_page())

    result = {
        "model_name": model_name,
        "device": device,
        "num_regions": len(regions),
        "regions": regions,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[smoke] model={model_name} device={device} regions={len(regions)}")


if __name__ == "__main__":
    main()
