# DETR Layout Server

docling이 사용하는 RT-DETR 기반 문서 레이아웃 분석 모델([docling-ibm-models](https://github.com/docling-project/docling-ibm-models))을
FastAPI로 감싼 서빙 앱입니다. 페이지 이미지를 보내면 title/section-header/text/table 등의
영역(bbox + category + confidence)을 반환합니다.

## Quick start

```shell
pip install -e .
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

첫 요청(또는 서버 기동) 시 HuggingFace에서 모델 가중치를 내려받습니다. 네트워크가 막힌
환경이라면 `huggingface-cli download <repo_id>`로 미리 캐시해두세요.

## Environment variables

| Name | Default | Description |
|---|---|---|
| `MODEL_NAME` | `docling_layout_heron` | 사용할 모델. `docling_layout_v2` / `docling_layout_heron` / `docling_layout_heron_101` / `docling_layout_egret_medium` / `docling_layout_egret_large` / `docling_layout_egret_xlarge` 중 선택 — 뒤로 갈수록 정확하지만 느림. |
| `DEVICE` | `cpu` | `cpu` / `cuda` / `mps`. |
| `CONFIDENCE_THRESHOLD` | `0.3` | 이 값 미만의 탐지 결과는 버림. |

## API

### `GET /healthcheck`

```json
{"status": "ok"}
```

### `POST /detect`

페이지 이미지를 base64(PNG/JPEG)로 묶어서 보내면, 이미지마다 감지된 영역 목록을 반환합니다.
좌표계는 `(l, t, r, b)` = 이미지 좌상단 기준 (left, top, right, bottom) 픽셀 좌표입니다.

**Request**
```json
{
  "images": ["<base64 png>", "<base64 png>"]
}
```

**Response**
```json
{
  "results": [
    [
      {"label": "Section-header", "confidence": 0.91, "l": 251.0, "t": 514.0, "r": 493.0, "b": 532.0},
      {"label": "Text", "confidence": 0.98, "l": 251.0, "t": 1012.0, "r": 975.0, "b": 1208.0}
    ],
    []
  ]
}
```

### 호출 예시 (PyMuPDF로 페이지 렌더링 → 요청)

```python
import base64
import fitz
import httpx

doc = fitz.open("sample.pdf")
page = doc[0]
png_bytes = page.get_pixmap(dpi=150).tobytes("png")

resp = httpx.post(
    "http://localhost:8080/detect",
    json={"images": [base64.b64encode(png_bytes).decode("ascii")]},
)
print(resp.json())
```
