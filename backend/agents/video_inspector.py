"""
ViralSim AI - Multimodal Video Inspector
Extracts physical frames via FFmpeg and performs objective vision AI audits
to ground agent simulation in real visual and technical quality.
"""

import base64
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional
from backend.agents.config import get_llm_client, is_llm_available, LLM_MODEL_NAME

logger = logging.getLogger("viralsim.inspector")

class VideoInspector:
    """
    Extracts real video frames and evaluates technical, visual, and narrative signals
    to prevent sycophancy and ensure accurate, ruthless real-world scoring.
    """

    def __init__(self, data_root: Optional[Path] = None):
        if data_root is None:
            self.data_root = Path(__file__).resolve().parent.parent.parent / "data"
        else:
            self.data_root = data_root
        self.frames_dir = self.data_root / "frames"
        self.frames_dir.mkdir(parents=True, exist_ok=True)

    def extract_keyframes(self, video_path: Path, duration: float) -> Dict[str, Optional[Path]]:
        """Extracts 0.5s (opening hook), 2.0s (hook resolution), and midpoint frames with fast downscaling."""
        vid_stem = video_path.stem
        target_dir = self.frames_dir / vid_stem
        target_dir.mkdir(parents=True, exist_ok=True)

        f_hook = target_dir / "frame_hook.jpg"
        f_mid = target_dir / "frame_mid.jpg"

        # If already extracted and valid, skip FFmpeg
        if f_hook.exists() and f_hook.stat().st_size > 1000 and f_mid.exists() and f_mid.stat().st_size > 1000:
            return {"hook_frame": f_hook, "mid_frame": f_mid}

        t_hook = min(0.5, max(0.1, duration * 0.05))
        t_mid = min(duration - 0.5, max(1.0, duration * 0.5))

        ffmpeg_exe = shutil.which("ffmpeg") or "ffmpeg"

        try:
            # Fast thumbnail extraction with 360px downscaling for low-latency Vision AI
            subprocess.run(
                [ffmpeg_exe, "-y", "-ss", str(t_hook), "-i", str(video_path), "-vf", "scale=360:-2", "-frames:v", "1", "-q:v", "4", str(f_hook)],
                capture_output=True, timeout=8
            )
            subprocess.run(
                [ffmpeg_exe, "-y", "-ss", str(t_mid), "-i", str(video_path), "-vf", "scale=360:-2", "-frames:v", "1", "-q:v", "4", str(f_mid)],
                capture_output=True, timeout=8
            )
        except Exception as e:
            logger.warning(f"FFmpeg frame extraction failed for {video_path}: {e}")

        return {
            "hook_frame": f_hook if f_hook.exists() and f_hook.stat().st_size > 0 else None,
            "mid_frame": f_mid if f_mid.exists() and f_mid.stat().st_size > 0 else None,
        }

    def inspect_technical(self, video_path: Path) -> Dict[str, Any]:
        """Probes video dimensions, orientation, and streams."""
        ffprobe_exe = shutil.which("ffprobe") or "ffprobe"
        meta = {
            "width": 1080,
            "height": 1920,
            "is_vertical_9_16": True,
            "duration": 15.0,
            "has_audio": True,
            "aspect_ratio": "9:16"
        }
        try:
            p = subprocess.run(
                [ffprobe_exe, "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height", "-of", "json", str(video_path)],
                capture_output=True, text=True, timeout=10
            )
            raw = json.loads(p.stdout)
            duration = float(raw.get("format", {}).get("duration") or 15.0)
            streams = raw.get("streams", [])
            v_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
            has_audio = any(s.get("codec_type") == "audio" for s in streams)
            w = int(v_stream.get("width") or 1080)
            h = int(v_stream.get("height") or 1920)

            is_vertical = h > w
            is_9_16 = abs((w / max(1, h)) - (9 / 16)) < 0.15

            meta = {
                "width": w,
                "height": h,
                "is_vertical_9_16": is_vertical,
                "is_strict_9_16": is_9_16,
                "duration": round(duration, 2),
                "has_audio": has_audio,
                "aspect_ratio": "9:16" if is_vertical else ("16:9" if w > h else "1:1")
            }
        except Exception as e:
            logger.warning(f"Technical inspection error: {e}")
        return meta

    def inspect_visual_frames(self, hook_frame: Optional[Path], mid_frame: Optional[Path], platform: str = "Instagram Reels") -> Dict[str, Any]:
        """Sends keyframes to Gemini Vision to diagnose actual visual appeal and flaws."""
        if not is_llm_available() or not hook_frame or not hook_frame.exists():
            return {
                "is_synthetic_or_test_card": False,
                "visual_hook_score_1_to_10": 6,
                "production_quality_score_1_to_10": 6,
                "has_readable_captions": False,
                "human_subject_present": False,
                "primary_visual_subject": "Standard video presentation",
                "objective_visual_flaws": ["Metadata analysis only; visual frames unprobed"],
                "visual_summary": "Visual frame analysis unassisted."
            }

        try:
            with open(hook_frame, "rb") as f:
                b64_hook = base64.b64encode(f.read()).decode("utf-8")

            client = get_llm_client()
            system_prompt = f"""You are a ruthless, unvarnished social media video auditor for {platform}, TikTok, and YouTube Shorts.
You evaluate the ACTUAL visual frames extracted from the opening 0.5s of an uploaded video.
Social media users swipe away in 1.2 seconds if the visual is boring, static, low-effort, or broken.

Inspect the frame critically and return valid JSON with:
{{
  "is_synthetic_or_test_card": <boolean, TRUE if SMPTE color bars, black/blank screen, testsrc, unrendered placeholder>,
  "visual_hook_score_1_to_10": <int 1-10: 1-2 for test card/black/ugly; 3-4 for boring static text/talking head; 5-6 for standard; 7-8 for high energy; 9-10 for elite visual pattern interrupt>,
  "production_quality_score_1_to_10": <int 1-10: lighting, crispness, professional framing>,
  "has_readable_captions": <boolean, are there prominent, high-contrast readable text captions?>,
  "human_subject_present": <boolean, is an expressive human face or creator visible?>,
  "primary_visual_subject": <string concise description of what is actually shown>,
  "objective_visual_flaws": [<string flaw 1>, <string flaw 2>],
  "visual_summary": <string blunt 1-2 sentence critique of whether this visual stops the scroll>
}}"""

            resp = client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Evaluate the opening 0.5s visual hook frame for {platform}."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_hook}"}}
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            raw = resp.choices[0].message.content or "{}"
            return json.loads(raw)
        except Exception as e:
            logger.error(f"Vision frame inspection error: {e}")
            return {
                "is_synthetic_or_test_card": False,
                "visual_hook_score_1_to_10": 5,
                "production_quality_score_1_to_10": 5,
                "has_readable_captions": False,
                "human_subject_present": False,
                "primary_visual_subject": "Uploaded footage",
                "objective_visual_flaws": ["Vision audit fallback"],
                "visual_summary": "Vision API temporarily unavailable."
            }

    def compute_calibration(self, tech: Dict[str, Any], vision: Dict[str, Any], platform: str = "Instagram Reels") -> Dict[str, Any]:
        """Computes deterministic, unvarnished calibration constraints based on physical video signals."""
        is_test = vision.get("is_synthetic_or_test_card", False)
        v_hook = int(vision.get("visual_hook_score_1_to_10", 5))
        has_audio = tech.get("has_audio", True)
        is_vert = tech.get("is_vertical_9_16", True)

        if is_test:
            # Completely broken / placeholder / test card: 12% - 22% retention max
            calibrated_hook_score = max(8, min(24, v_hook * 8))
            max_retention_cap = 0.22
            typical_skip_rate = 0.88
            quality_tier = "Critical Failure / Unreleasable"
        elif not is_vert and "Reels" in platform:
            # Horizontal letterboxed video on short-form feed: severe penalty
            calibrated_hook_score = max(20, min(42, v_hook * 6 + 10))
            max_retention_cap = 0.36
            typical_skip_rate = 0.72
            quality_tier = "High Drop-Off Risk (Letterboxed)"
        elif v_hook <= 3:
            # Very weak visual hook (static, boring, dark, no contrast)
            calibrated_hook_score = max(18, min(38, v_hook * 10 + 5))
            max_retention_cap = 0.34
            typical_skip_rate = 0.75
            quality_tier = "High Drop-Off Risk"
        elif v_hook <= 5:
            # Mediocre / standard video
            calibrated_hook_score = max(40, min(58, v_hook * 10 + 4))
            max_retention_cap = 0.48
            typical_skip_rate = 0.58
            quality_tier = "Average / Needs Visual Polish"
        elif v_hook <= 7:
            # Good quality video
            calibrated_hook_score = max(60, min(74, v_hook * 9 + 8))
            max_retention_cap = 0.64
            typical_skip_rate = 0.38
            quality_tier = "Above Average / Strong Contender"
        else:
            # Top tier viral creative
            calibrated_hook_score = max(76, min(92, v_hook * 9 + 6))
            max_retention_cap = 0.78
            typical_skip_rate = 0.24
            quality_tier = "Top 5% Viral Contender"

        if not has_audio:
            calibrated_hook_score = max(12, calibrated_hook_score - 18)
            max_retention_cap = min(max_retention_cap, 0.28)

        return {
            "calibrated_hook_score": calibrated_hook_score,
            "max_retention_cap": max_retention_cap,
            "typical_skip_rate": typical_skip_rate,
            "quality_tier": quality_tier,
            "is_synthetic_or_test": is_test
        }

    def audit_video(self, video_path: Path, duration: float, platform: str = "Instagram Reels") -> Dict[str, Any]:
        """
        Runs complete technical + vision inspection and computes a real-world baseline constraint.
        Uses on-disk caching to make repeat audits instantaneous.
        """
        vid_stem = video_path.stem
        target_dir = self.frames_dir / vid_stem
        target_dir.mkdir(parents=True, exist_ok=True)
        cache_file = target_dir / "audit_cache.json"

        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = json.load(f)
                    if cached.get("vision") and cached.get("calibration"):
                        return cached
            except Exception as e:
                logger.debug(f"Cache read error: {e}")

        tech = self.inspect_technical(video_path)
        frames = self.extract_keyframes(video_path, duration)
        vision = self.inspect_visual_frames(frames["hook_frame"], frames["mid_frame"], platform=platform)
        calib = self.compute_calibration(tech, vision, platform=platform)

        res = {
            "technical": tech,
            "vision": vision,
            "calibration": calib
        }

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=2)
        except Exception as e:
            logger.debug(f"Cache write error: {e}")

        return res

