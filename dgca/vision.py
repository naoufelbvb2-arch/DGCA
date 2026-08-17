"""
مُرمِّز الحاسة البصرية والتأريض متعدد الحواس واللغات (RFC-06: Vision Modality & Multimodal Grounding).

المبدأ الحاكم:
«الرؤية مفرز دلالي خفيف وليست شبكة عمياء؛ تُفكك المشهد إلى مسار بطني للهوية ومسار ظهري للمكان،
وتعمل كوسيط وجودي محايد لتوحيد اللغات دون قواميس ترجمة».
"""
from dataclasses import dataclass
from typing import Literal

from .encoder import SensoryEpisode


@dataclass
class VisualObject:
    """كائن بصري مستخلص من المشهد."""

    uid: str
    color: str  # مثل "vis:clr:red"
    shape: str  # مثل "vis:shp:circle"
    size: str  # مثل "vis:sz:medium"
    bbox: tuple[float, float, float, float]  # (x_min, y_min, x_max, y_max)
    is_focal: bool = False


@dataclass
class SpatialRelation:
    """علاقة مكانية بين كائنين."""

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


class VisionSensoryPipeline:
    """مُرمِّز الحاسة البصرية والتأريض المكاني."""

    def __init__(self):
        self.focal_center_threshold = 0.25
        self.dominant_size_threshold = 0.30

    def classify_color_hsv(self, h: float, s: float, v: float) -> str:
        """تكميم الألوان في فضاء HSV إلى 8 ألوان طيفية بالإضافة إلى الرماديات."""
        # الرماديات
        if s < 0.15:
            if v > 0.85:
                return "vis:clr:white"
            if v < 0.15:
                return "vis:clr:black"
            return "vis:clr:gray"

        if v < 0.15:
            return "vis:clr:black"

        # الألوان الطيفية الأساسية (8 قطاعات بزاوية 0..360)
        h_norm = (h % 360.0 + 360.0) % 360.0
        if h_norm < 25.0 or h_norm >= 335.0:
            return "vis:clr:red"
        elif 25.0 <= h_norm < 55.0:
            return "vis:clr:orange"
        elif 55.0 <= h_norm < 85.0:
            return "vis:clr:yellow"
        elif 85.0 <= h_norm < 165.0:
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

            # احتواء inside
            if (
                xmin_a >= xmin_b
                and ymin_a >= ymin_b
                and xmax_a <= xmax_b
                and ymax_a <= ymax_b
            ):
                relations.append(
                    SpatialRelation(obj.uid, "vis:rel:inside", focal_obj.uid)
                )
            # استناد on_top
            elif (
                ymax_a <= ymin_b + 5
                and abs((xmin_a + xmax_a) / 2 - (xmin_b + xmax_b) / 2) < 20
            ):
                relations.append(
                    SpatialRelation(obj.uid, "vis:rel:on_top", focal_obj.uid)
                )
            # فوق above
            elif ymax_a < ymin_b:
                relations.append(
                    SpatialRelation(obj.uid, "vis:rel:above", focal_obj.uid)
                )
            # يسار left_of
            elif xmax_a < xmin_b:
                relations.append(
                    SpatialRelation(obj.uid, "vis:rel:left_of", focal_obj.uid)
                )
            # يمين right_of
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
        """يحول الكائنات والعلاقات البصرية إلى حلقات إدراكية معيارية."""
        episodes: list[SensoryEpisode] = []

        # 1. توليد الحلقات المتزامنة للكائنات (Micro-Episodes)
        for obj in objects:
            signals = [
                ("vision", obj.uid),  # ◄ الرأس في الموضع 0
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

        # 2. توليد حلقات الأحداث المكانية التتابعية (ق11)
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
                    )
                )

        return episodes
