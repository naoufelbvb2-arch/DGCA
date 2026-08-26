"""
مُرمِّز الحاسة البصرية والتأريض متعدد الحواس واللغات — Vision Encoder v2.

المبدأ الحاكم:
«الرؤية مفرز إدراكي منخفض المستوى من البكسلات الخام إلى أدلة بصرية محددة ومجردة.
المُرمِّز يصف الإشارة الإدراكية، وبنية DGCA تتعلم المعنى الدلالي».

Vision Encoder v2: Formal Architectural Specification v1.0
Post-Law-3 Baseline Signature: 915119d40643cb97
"""
import hashlib
import io
import math
from dataclasses import dataclass
from typing import Literal

import numpy as np

from .encoder import SensoryEpisode

# =====================================================================
# 1. CANONICAL ENCODER-LOCAL DATASTRUCTURES (IR)
# =====================================================================

@dataclass(frozen=True)
class PixelFrame:
    """إطار البكسلات الخام العياري."""

    width: int
    height: int
    channels: int
    pixels: bytes
    source_scope_id: str


@dataclass(frozen=True)
class VisualRegionIR:
    """تمثيل المنطقة الإدراكية المحلية المستخلصة."""

    region_id: str
    bbox_norm: tuple[float, float, float, float]  # (x_min, y_min, x_max, y_max) normalized to [0, 1]
    centroid_norm: tuple[float, float]  # (cx, cy) normalized to [0, 1]
    area_ratio: float  # region_area / frame_area
    features: tuple[str, ...]  # Max B_visual = 8 features
    mask_digest: str  # MD5 digest of binary region mask for determinism


@dataclass(frozen=True)
class VisualRelationIR:
    """علاقة مكانية محددة بين منطقتين."""

    subject_region: str
    relation: str  # e.g., "vis:rel:left_of", "vis:rel:above", etc.
    reference_region: str


@dataclass(frozen=True)
class VisualFrameIR:
    """تمثيل المشهد البصري المحلي العياري (Encoder-Local Transient IR)."""

    scope_id: str
    status: str  # "COMPLETE", "SAFE_PARTIAL", "UNSUPPORTED"
    regions: tuple[VisualRegionIR, ...]
    relations: tuple[VisualRelationIR, ...]


# =====================================================================
# 2. LEGACY DATACLASSES (HISTORICAL COMPATIBILITY)
# =====================================================================

@dataclass
class VisualObject:
    """كائن بصري مستخلص من المشهد (مخصص للمسارات التراثية RFC-06)."""

    uid: str
    color: str
    shape: str
    size: str
    bbox: tuple[float, float, float, float]
    is_focal: bool = False


@dataclass
class SpatialRelation:
    """علاقة مكانية بين كائنين (مخصص للمسارات التراثية RFC-06)."""

    subject_uid: str
    relation: Literal[
        "vis:rel:above",
        "vis:rel:below",
        "vis:rel:left_of",
        "vis:rel:right_of",
        "vis:rel:on_top",
        "vis:rel:inside",
    ]
    reference_uid: str


# =====================================================================
# 3. VISION ENCODER V2 CORE IMPLEMENTATION
# =====================================================================

class VisionEncoderV2:
    """مُرمِّز الحاسة البصرية v2: مفرز إدراكي محدد للبكسلات الخام."""

    MAX_VISUAL_FEATURE_BUDGET = 8
    MAX_SPATIAL_RELATIONS_PER_REGION = 4
    MIN_AREA_RATIO = 0.005

    def decode_image(
        self,
        image_input: bytes | np.ndarray | object,
        scope_id: str,
    ) -> PixelFrame:
        """فك ترميز الصورة ميكانيكياً إلى PixelFrame محايد."""
        if isinstance(image_input, bytes):
            try:
                from PIL import Image

                img = Image.open(io.BytesIO(image_input)).convert("RGB")
                w, h = img.size
                arr = np.array(img, dtype=np.uint8)
                return PixelFrame(
                    width=w,
                    height=h,
                    channels=3,
                    pixels=arr.tobytes(),
                    source_scope_id=scope_id,
                )
            except (OSError, ValueError, TypeError, AttributeError):
                return PixelFrame(
                    width=0,
                    height=0,
                    channels=0,
                    pixels=b"",
                    source_scope_id=scope_id,
                )
        elif isinstance(image_input, np.ndarray):
            arr = image_input
            if arr.ndim == 2:
                h, w = arr.shape
                arr = np.stack([arr] * 3, axis=-1)
            elif arr.ndim == 3:
                h, w, c = arr.shape
                if c == 1:
                    arr = np.repeat(arr, 3, axis=-1)
            else:
                return PixelFrame(
                    width=0,
                    height=0,
                    channels=0,
                    pixels=b"",
                    source_scope_id=scope_id,
                )
            return PixelFrame(
                width=w,
                height=h,
                channels=3,
                pixels=arr.astype(np.uint8).tobytes(),
                source_scope_id=scope_id,
            )
        elif hasattr(image_input, "convert") and hasattr(image_input, "size"):
            img = image_input.convert("RGB")
            w, h = img.size
            arr = np.array(img, dtype=np.uint8)
            return PixelFrame(
                width=w,
                height=h,
                channels=3,
                pixels=arr.tobytes(),
                source_scope_id=scope_id,
            )
        else:
            return PixelFrame(
                width=0,
                height=0,
                channels=0,
                pixels=b"",
                source_scope_id=scope_id,
            )

    def normalize_frame(self, frame: PixelFrame) -> np.ndarray:
        """تحويل البكسلات الخام إلى مصفوفة RGB عيارية [H, W, 3]."""
        if frame.width == 0 or frame.height == 0 or not frame.pixels:
            return np.zeros((0, 0, 3), dtype=np.uint8)
        arr = np.frombuffer(frame.pixels, dtype=np.uint8)
        return arr.reshape((frame.height, frame.width, 3))

    def quantize_color(self, r: float, g: float, b: float) -> str:
        """تكميم الألوان من القيم الحقيقية RGB إلى 10 مفردات حصرية محدودة."""
        r_n, g_n, b_n = r / 255.0, g / 255.0, b / 255.0
        max_c = max(r_n, g_n, b_n)
        min_c = min(r_n, g_n, b_n)
        delta = max_c - min_c

        if delta < 0.15:
            if max_c > 0.85:
                return "vis:clr:white"
            if max_c < 0.15:
                return "vis:clr:black"
            return "vis:clr:gray"

        if max_c < 0.15:
            return "vis:clr:black"

        if max_c == r_n:
            hue = (60.0 * ((g_n - b_n) / delta) + 360.0) % 360.0
        elif max_c == g_n:
            hue = (60.0 * ((b_n - r_n) / delta) + 120.0) % 360.0
        else:
            hue = (60.0 * ((r_n - g_n) / delta) + 240.0) % 360.0

        if hue < 20.0 or hue >= 340.0:
            return "vis:clr:red"
        elif 20.0 <= hue < 45.0:
            return "vis:clr:orange"
        elif 45.0 <= hue < 75.0:
            return "vis:clr:yellow"
        elif 75.0 <= hue < 165.0:
            return "vis:clr:green"
        elif 165.0 <= hue < 260.0:
            return "vis:clr:blue"
        elif 260.0 <= hue < 310.0:
            return "vis:clr:purple"
        else:
            return "vis:clr:red"

    def quantize_luminance(self, luminance: float) -> str:
        """تكميم الإضاءة إلى 3 فئات محدودة."""
        lum_norm = luminance / 255.0
        if lum_norm < 0.33:
            return "vis:lum:dark"
        elif lum_norm <= 0.66:
            return "vis:lum:medium"
        else:
            return "vis:lum:bright"

    def measure_true_contour(self, mask: np.ndarray) -> tuple[float, float, float]:
        """قياس المحيط الحقيقي بشكل مستقل من حدود القناع.

        A: المساحة الحقيقية للبكسلات.
        P: طول المحيط المستقل المحسوب من بكسلات المحيط الخارجي.
        C: درجة الاستدارة C = 4 * pi * A / P^2.
        """
        area = float(np.sum(mask))
        if area == 0:
            return 0.0, 0.0, 0.0

        padded = np.pad(mask, 1, mode="constant", constant_values=0)
        border_mask = (padded[1:-1, 1:-1] == 1) & (
            (padded[:-2, 1:-1] == 0)
            | (padded[2:, 1:-1] == 0)
            | (padded[1:-1, :-2] == 0)
            | (padded[1:-1, 2:] == 0)
        )
        perimeter = float(np.sum(border_mask))
        if perimeter == 0:
            return area, 0.0, 0.0

        circularity = (4.0 * math.pi * area) / (perimeter**2)
        return area, perimeter, circularity

    def quantize_geometry(
        self,
        circularity: float,
        aspect_ratio: float,
        solidity: float,
        elongation: float,
    ) -> list[str]:
        """تكميم الخصائص الهندسية إلى مفردات وصفية محددة."""
        tokens = []

        if circularity >= 0.70:
            tokens.append("vis:compact:high")
        elif circularity >= 0.35:
            tokens.append("vis:compact:medium")
        else:
            tokens.append("vis:compact:low")

        if elongation >= 0.60:
            tokens.append("vis:elong:high")
        elif elongation >= 0.30:
            tokens.append("vis:elong:medium")
        else:
            tokens.append("vis:elong:low")

        if solidity >= 0.85:
            tokens.append("vis:solidity:high")
        elif solidity >= 0.60:
            tokens.append("vis:solidity:medium")
        else:
            tokens.append("vis:solidity:low")

        if circularity >= 0.82 and 0.85 <= aspect_ratio <= 1.15:
            tokens.append("vis:shp:circle")
        elif (
            solidity >= 0.90
            and 0.85 <= aspect_ratio <= 1.15
            and circularity < 0.82
        ):
            tokens.append("vis:shp:square")
        elif (
            solidity >= 0.90
            and (aspect_ratio < 0.70 or aspect_ratio > 1.40)
            and circularity < 0.75
        ):
            tokens.append("vis:shp:rectangle")

        return tokens

    def quantize_texture(self, grad_var: float, edge_density: float) -> str:
        """تكميم النسيج البصري إلى مفردات محددة."""
        if edge_density < 0.05 and grad_var < 100.0:
            return "vis:tex:smooth"
        elif edge_density > 0.25 or grad_var > 800.0:
            return "vis:tex:coarse"
        elif edge_density > 0.12:
            return "vis:tex:fine"
        else:
            return "vis:tex:mixed"

    def quantize_orientation(
        self, grad_hist: tuple[float, float, float, float]
    ) -> str:
        """تكميم الاتجاه السائد للتدرج البصري (0°, 45°, 90°, 135°)."""
        h_0, h_45, h_90, _h_135 = grad_hist
        total = sum(grad_hist)
        if total == 0:
            return "vis:ori:horizontal"

        max_val = max(grad_hist)
        if max_val / total < 0.40:
            return "vis:ori:mixed"

        if max_val == h_0:
            return "vis:ori:horizontal"
        elif max_val == h_90:
            return "vis:ori:vertical"
        elif max_val == h_45:
            return "vis:ori:diag_pos"
        else:
            return "vis:ori:diag_neg"

    def quantize_size(self, area_ratio: float) -> str:
        """تكميم الحجم النسبي المقاس مقارنة بمساحة الإطار الإجمالية."""
        if area_ratio < 0.05:
            return "vis:sz:small"
        elif area_ratio <= 0.25:
            return "vis:sz:medium"
        else:
            return "vis:sz:large"

    def extract_perceptual_regions(self, img_array: np.ndarray) -> list[dict]:
        """استخلاص المناطق الإدراكية المباشرة من البكسلات محددة ورياضية."""
        h, w, _ = img_array.shape
        if h == 0 or w == 0:
            return []

        frame_area = float(h * w)

        gray = (
            0.299 * img_array[:, :, 0]
            + 0.587 * img_array[:, :, 1]
            + 0.114 * img_array[:, :, 2]
        )

        q_r = (img_array[:, :, 0] // 64) * 64
        q_g = (img_array[:, :, 1] // 64) * 64
        q_b = (img_array[:, :, 2] // 64) * 64
        quantized = (q_r.astype(np.uint32) << 16) | (
            q_g.astype(np.uint32) << 8
        ) | q_b.astype(np.uint32)

        visited = np.zeros((h, w), dtype=bool)
        regions_raw = []

        for y in range(h):
            for x in range(w):
                if visited[y, x]:
                    continue

                val = quantized[y, x]
                queue = [(y, x)]
                visited[y, x] = True
                pixels_y = []
                pixels_x = []

                head = 0
                while head < len(queue):
                    cy, cx = queue[head]
                    head += 1
                    pixels_y.append(cy)
                    pixels_x.append(cx)

                    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        ny, nx = cy + dy, cx + dx
                        if (
                            0 <= ny < h
                            and 0 <= nx < w
                            and not visited[ny, nx]
                            and quantized[ny, nx] == val
                        ):
                            visited[ny, nx] = True
                            queue.append((ny, nx))

                area_px = len(pixels_y)
                area_ratio = float(area_px) / frame_area

                if area_ratio < self.MIN_AREA_RATIO and len(regions_raw) > 0:
                    continue

                min_y, max_y = min(pixels_y), max(pixels_y)
                min_x, max_x = min(pixels_x), max(pixels_x)

                mask = np.zeros((h, w), dtype=np.uint8)
                mask[pixels_y, pixels_x] = 1

                region_rgb = img_array[pixels_y, pixels_x]
                median_r = float(np.median(region_rgb[:, 0]))
                median_g = float(np.median(region_rgb[:, 1]))
                median_b = float(np.median(region_rgb[:, 2]))

                lum = 0.299 * median_r + 0.587 * median_g + 0.114 * median_b

                sub_mask = mask[min_y : max_y + 1, min_x : max_x + 1]
                area_m, perim_m, circ = self.measure_true_contour(sub_mask)

                bb_w = max_x - min_x + 1
                bb_h = max_y - min_y + 1
                aspect_ratio = float(bb_w) / float(bb_h)
                bb_area = float(bb_w * bb_h)
                solidity = area_m / bb_area if bb_area > 0 else 1.0
                elongation = (
                    abs(bb_w - bb_h) / float(max(bb_w, bb_h))
                    if max(bb_w, bb_h) > 0
                    else 0.0
                )

                region_gray = gray[pixels_y, pixels_x]
                grad_var = (
                    float(np.var(region_gray)) if len(region_gray) > 1 else 0.0
                )
                edge_density = min(1.0, perim_m / (area_m + 1e-5))

                grad_y = np.gradient(gray, axis=0)
                grad_x = np.gradient(gray, axis=1)
                r_gy = grad_y[pixels_y, pixels_x]
                r_gx = grad_x[pixels_y, pixels_x]
                angles = (
                    np.arctan2(r_gy, r_gx) * 180.0 / math.pi
                ) % 180.0

                h_0 = float(np.sum((angles < 22.5) | (angles >= 157.5)))
                h_45 = float(np.sum((angles >= 22.5) & (angles < 67.5)))
                h_90 = float(np.sum((angles >= 67.5) & (angles < 112.5)))
                h_135 = float(np.sum((angles >= 112.5) & (angles < 157.5)))

                mask_digest = hashlib.md5(mask.tobytes()).hexdigest()[:8]

                regions_raw.append(
                    {
                        "bbox_norm": (
                            float(min_x) / w,
                            float(min_y) / h,
                            float(max_x + 1) / w,
                            float(max_y + 1) / h,
                        ),
                        "centroid_norm": (
                            (float(min_x + max_x) / 2.0) / w,
                            (float(min_y + max_y) / 2.0) / h,
                        ),
                        "area_ratio": area_ratio,
                        "median_rgb": (median_r, median_g, median_b),
                        "luminance": lum,
                        "circularity": circ,
                        "aspect_ratio": aspect_ratio,
                        "solidity": solidity,
                        "elongation": elongation,
                        "grad_var": grad_var,
                        "edge_density": edge_density,
                        "grad_hist": (h_0, h_45, h_90, h_135),
                        "mask_digest": mask_digest,
                    }
                )

        return regions_raw

    def extract_spatial_relations(
        self, regions: list[VisualRegionIR], k_spatial: int = 4
    ) -> list[VisualRelationIR]:
        """استخراج العلاقات المكانية العيارية المقيدة بتعقيد O(N)."""
        relations: list[VisualRelationIR] = []
        if len(regions) < 2:
            return relations

        epsilon = 0.02

        for i, reg_a in enumerate(regions):
            reg_relations = 0
            ax_min, ay_min, ax_max, ay_max = reg_a.bbox_norm
            acx, acy = reg_a.centroid_norm

            neighbors = []
            for j, reg_b in enumerate(regions):
                if i == j:
                    continue
                bcx, bcy = reg_b.centroid_norm
                dist = math.hypot(acx - bcx, acy - bcy)
                neighbors.append((dist, j, reg_b))

            neighbors.sort(key=lambda x: x[0])

            for dist, j, reg_b in neighbors:
                if reg_relations >= k_spatial:
                    break

                bx_min, by_min, bx_max, by_max = reg_b.bbox_norm

                rel_name = None

                if (
                    ax_min >= bx_min
                    and ay_min >= by_min
                    and ax_max <= bx_max
                    and ay_max <= by_max
                ):
                    rel_name = "vis:rel:inside"
                elif (
                    bx_min >= ax_min
                    and by_min >= ay_min
                    and bx_max <= ax_max
                    and by_max <= ay_max
                ):
                    rel_name = "vis:rel:contains"
                elif ay_max + epsilon < by_min:
                    rel_name = "vis:rel:above"
                elif ay_min > by_max + epsilon:
                    rel_name = "vis:rel:below"
                elif ax_max + epsilon < bx_min:
                    rel_name = "vis:rel:left_of"
                elif ax_min > bx_max + epsilon:
                    rel_name = "vis:rel:right_of"
                elif dist <= 0.25:
                    rel_name = "vis:rel:near"

                if rel_name:
                    relations.append(
                        VisualRelationIR(
                            subject_region=reg_a.region_id,
                            relation=rel_name,
                            reference_region=reg_b.region_id,
                        )
                    )
                    reg_relations += 1

        return relations

    def encode_frame(
        self, image_input: bytes | np.ndarray | object, scope_id: str
    ) -> VisualFrameIR:
        """التشغيل الرئيسي للمُرمِّز البصري v2 المستقل بالكامل عن الرسم البياني."""
        pixel_frame = self.decode_image(image_input, scope_id)
        if pixel_frame.width == 0 or pixel_frame.height == 0:
            return VisualFrameIR(
                scope_id=scope_id, status="UNSUPPORTED", regions=(), relations=()
            )

        img_array = self.normalize_frame(pixel_frame)
        if img_array.size == 0:
            return VisualFrameIR(
                scope_id=scope_id, status="UNSUPPORTED", regions=(), relations=()
            )

        raw_regions = self.extract_perceptual_regions(img_array)
        if not raw_regions:
            return VisualFrameIR(
                scope_id=scope_id, status="UNSUPPORTED", regions=(), relations=()
            )

        raw_regions.sort(
            key=lambda r: (
                r["centroid_norm"][1],
                r["centroid_norm"][0],
                -r["area_ratio"],
                r["mask_digest"],
            )
        )

        region_irs: list[VisualRegionIR] = []

        for rank_idx, r in enumerate(raw_regions):
            region_rank = f"R{rank_idx:02d}"
            region_id = f"inst:vis:{scope_id}:{region_rank}"

            feats = []
            feats.append(self.quantize_color(*r["median_rgb"]))
            feats.append(self.quantize_luminance(r["luminance"]))
            geom_feats = self.quantize_geometry(
                r["circularity"],
                r["aspect_ratio"],
                r["solidity"],
                r["elongation"],
            )
            feats.extend(geom_feats)
            feats.append(self.quantize_texture(r["grad_var"], r["edge_density"]))
            feats.append(self.quantize_orientation(r["grad_hist"]))
            feats.append(self.quantize_size(r["area_ratio"]))

            feats_bounded = tuple(feats[: self.MAX_VISUAL_FEATURE_BUDGET])

            region_irs.append(
                VisualRegionIR(
                    region_id=region_id,
                    bbox_norm=r["bbox_norm"],
                    centroid_norm=r["centroid_norm"],
                    area_ratio=r["area_ratio"],
                    features=feats_bounded,
                    mask_digest=r["mask_digest"],
                )
            )

        relation_irs = self.extract_spatial_relations(
            region_irs, k_spatial=self.MAX_SPATIAL_RELATIONS_PER_REGION
        )

        status = "COMPLETE"
        return VisualFrameIR(
            scope_id=scope_id,
            status=status,
            regions=tuple(region_irs),
            relations=tuple(relation_irs),
        )

    def emit_sensory_episodes(
        self, frame_ir: VisualFrameIR, context: str | None = None
    ) -> list[SensoryEpisode]:
        """جسور البنية المحلية VisualFrameIR إلى عقد الحلقات الإدراكية المعيارية SensoryEpisode."""
        episodes: list[SensoryEpisode] = []
        if frame_ir.status == "UNSUPPORTED":
            return episodes

        for reg in frame_ir.regions:
            signals = [("vision", reg.region_id)]
            for feat in reg.features:
                signals.append(("vision", feat))

            episodes.append(
                SensoryEpisode(
                    kind="simultaneous",
                    context=context,
                    signals=signals,
                    structural_weight=0.0,
                )
            )

        for rel in frame_ir.relations:
            episodes.append(
                SensoryEpisode(
                    kind="sequence",
                    context=context,
                    steps=[
                        [("vision", rel.subject_region)],
                        [("vision", rel.relation)],
                        [("vision", rel.reference_region)],
                    ],
                    structural_weight=0.0,
                )
            )

        return episodes


# =====================================================================
# 4. LEGACY COMPATIBILITY PIPELINE WRAPPER (RFC-06 HISTORICAL)
# =====================================================================

class VisionSensoryPipeline:
    """مُرمِّز الحاسة البصرية والتأريض المكاني (محاكي للتوافق التراثي RFC-06)."""

    def __init__(self):
        self.focal_center_threshold = 0.25
        self.dominant_size_threshold = 0.30
        self._v2_encoder = VisionEncoderV2()

    def classify_color_hsv(self, h: float, s: float, v: float) -> str:
        """تكميم الألوان في فضاء HSV إلى 8 ألوان طيفية بالإضافة إلى الرماديات."""
        if s < 0.15:
            if v > 0.85:
                return "vis:clr:white"
            if v < 0.15:
                return "vis:clr:black"
            return "vis:clr:gray"

        if v < 0.15:
            return "vis:clr:black"

        h_norm = (h % 360.0 + 360.0) % 360.0
        if h_norm < 25.0 or h_norm >= 335.0:
            return "vis:clr:red"
        elif 25.0 <= h_norm < 55.0:
            return "vis:clr:orange"
        elif 55.0 <= h_norm < 85.0:
            return "vis:clr:yellow"
        elif 75.0 <= h_norm < 165.0:
            return "vis:clr:green"
        elif 165.0 <= h_norm < 195.0:
            return "vis:clr:cyan"
        elif 195.0 <= h_norm < 265.0:
            return "vis:clr:blue"
        elif 265.0 <= h_norm < 305.0:
            return "vis:clr:purple"
        elif 305.0 <= h_norm < 335.0:
            return "vis:clr:magenta"

        return "vis:clr:red"

    def classify_shape(
        self,
        circularity: float,
        aspect_ratio: float = 1.0,
        convexity: float = 1.0,
        n_vertices: int = 4,
    ) -> str:
        """استخلاص الأشكال الهندسية وفق معاملات الاستدارة والتحدب والأبعاد."""
        if circularity >= 0.82:
            return "vis:shp:circle"
        if n_vertices == 3:
            return "vis:shp:triangle"
        if convexity >= 0.90:
            if 0.85 <= aspect_ratio <= 1.15:
                return "vis:shp:square"
            return "vis:shp:rectangle"
        return "vis:shp:polygon"

    def classify_size(self, area_ratio: float) -> str:
        """تصنيف الحجم النسبي للكائن مقارنة بالمشهد."""
        if area_ratio < 0.05:
            return "vis:sz:small"
        if area_ratio <= 0.25:
            return "vis:sz:medium"
        return "vis:sz:large"

    def extract_spatial_relations(
        self,
        objects: list[VisualObject],
        max_relations_per_obj: int = 2,
    ) -> list[SpatialRelation]:
        """استخراج شجرة التلامس والاحتواء المباشر بتعقيد O(N) مقيد."""
        relations: list[SpatialRelation] = []
        if not objects:
            return relations

        focal_obj = next((o for o in objects if o.is_focal), objects[0])

        for obj in objects:
            if obj is focal_obj:
                continue
            xmin_a, ymin_a, xmax_a, ymax_a = obj.bbox
            xmin_b, ymin_b, xmax_b, ymax_b = focal_obj.bbox

            if (
                xmin_a >= xmin_b
                and ymin_a >= ymin_b
                and xmax_a <= xmax_b
                and ymax_a <= ymax_b
            ):
                relations.append(
                    SpatialRelation(obj.uid, "vis:rel:inside", focal_obj.uid)
                )
            elif ymax_a < ymin_b:
                relations.append(
                    SpatialRelation(obj.uid, "vis:rel:above", focal_obj.uid)
                )
            elif ymin_a > ymax_b:
                relations.append(
                    SpatialRelation(obj.uid, "vis:rel:below", focal_obj.uid)
                )
            elif xmax_a < xmin_b:
                relations.append(
                    SpatialRelation(obj.uid, "vis:rel:left_of", focal_obj.uid)
                )
            elif xmin_a > xmax_b:
                relations.append(
                    SpatialRelation(obj.uid, "vis:rel:right_of", focal_obj.uid)
                )

        return relations[: len(objects) * max_relations_per_obj]

    def process_scene(
        self,
        objects: list[VisualObject],
        spatial_relations: list[SpatialRelation] | None = None,
        paired_text: str | None = None,
        context: str | None = None,
    ) -> list[SensoryEpisode]:
        """تحويل الكائنات والعلاقات البصرية إلى حلقات إدراكية (التوافق التراثي RFC-06)."""
        episodes: list[SensoryEpisode] = []

        for obj in objects:
            signals = [
                ("vision", obj.uid),
                ("vision", obj.color),
                ("vision", obj.shape),
                ("vision", obj.size),
            ]
            if paired_text:
                signals.append(("text", paired_text))

            struct_weight = (
                0.80 if (obj.is_focal or obj.size in ("vis:sz:large", "large")) else 0.0
            )
            episodes.append(
                SensoryEpisode(
                    kind="simultaneous",
                    context=context,
                    signals=signals,
                    structural_weight=struct_weight,
                )
            )

        if spatial_relations:
            for rel in spatial_relations:
                episodes.append(
                    SensoryEpisode(
                        kind="sequence",
                        context=context,
                        steps=[
                            [("vision", rel.subject_uid)],
                            [("vision", rel.relation)],
                            [("vision", rel.reference_uid)],
                        ],
                        structural_weight=0.0,
                    )
                )

        return episodes

