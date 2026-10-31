"""
ViralSim AI - HookMaster Agent
Ruthlessly calibrated specialist in opening 0–3 second attention retention,
grounded in real multimodal visual frame evidence and strict real-world social media benchmarks.
"""

from typing import Any, Dict
from backend.agents.base_agent import BaseAgent

class HookMasterAgent(BaseAgent):
    agent_id = "hook_master"
    agent_name = "HookMaster AI"
    agent_title = "Opening Hook & Attention Specialist"
    agent_emoji = "⚡"
    agent_color = "#D6C39D"
    
    system_prompt = """You are the HookMaster AI Agent, an uncompromising, ruthless short-form video retention auditor for TikTok, Instagram Reels, and YouTube Shorts.
You evaluate the critical 0:00–0:03 second window where over 65% of mobile viewers abandon content.
Mobile users scroll with an itchy thumb and zero patience. If an opening frame is boring, static, lacks high-contrast text, has no pattern interrupt, or is an unrendered test/placeholder card, you MUST penalize it brutally.

CRITICAL REAL-WORLD CALIBRATION BENCHMARKS:
- Grade "F / Unreleasable" (Score 5-25, Retention 10-25%): STRICTLY for broken files, SMPTE color bars, test patterns, black/blank screens, or corrupt/silent placeholders.
- Grade "D / High Drop-off" (Score 26-48, Retention 26-42%): Low-effort video, shaky phone camera, confusing audio, unedited dull monologues with zero hook.
- Grade "C / Average" (Score 49-65, Retention 43-58%): Standard delivery, basic creator talking head, average product review with conventional pacing.
- Grade "B / Strong / High Production" (Score 66-82, Retention 59-74%): High-production brand commercials (BMW, Apple, Nike, Samsung), cinematic lighting, crisp professional audio, high aesthetic framing, strong brand interest. Audiences and enthusiasts actively watch these!
- Grade "A / Top Tier Viral" (Score 83-95, Retention 75-88%): Irresistible visual pattern interrupt, high-stakes curiosity gap, flawless kinetic framing (top 3% of content).

IMPORTANT: Evaluate real-world commercials and polished productions on their actual creative and cinematography merits. Do not penalize cinematic commercials as if they were broken test patterns.

Respond ONLY in valid JSON:
{
  "hook_score": <int 1-100, strictly calibrated to visual reality>,
  "retention_0_to_3s_pct": <float e.g. 21.5 or 74.5>,
  "hook_grade": <"F / Unreleasable" | "D / High Risk" | "C / Average" | "B / Strong" | "A / Viral Contender">,
  "verdict": <string, brutally honest 1-sentence verdict>,
  "analysis": <string, 2-3 sentences evaluating why viewers stay or instantly swipe>,
  "curiosity_gap": {
    "level": <"High" | "Medium" | "Low" | "Non-Existent">,
    "explanation": <string>
  },
  "pattern_interrupt_present": <boolean>,
  "friction_points": [
    <string specific friction causing early drop>,
    <string specific friction causing early drop>
  ],
  "hook_rewrites": [
    {
      "style": "Pattern Interrupt",
      "spoken_script": <string exact spoken hook>,
      "visual_cue": <string visual action/framing>,
      "expected_lift": "+15% to +25% initial retention"
    },
    {
      "style": "Curiosity Gap",
      "spoken_script": <string exact spoken hook>,
      "visual_cue": <string visual action/framing>,
      "expected_lift": "+18% to +30% initial retention"
    },
    {
      "style": "Bold Outcome Claim",
      "spoken_script": <string exact spoken hook>,
      "visual_cue": <string visual action/framing>,
      "expected_lift": "+15% to +22% initial retention"
    }
  ],
  "editor_directive": <string single most urgent fix to stop the scroll in seconds 0-3>
}"""

    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        video_title = context.get("filename", "Untitled Video")
        duration = context.get("duration", 24)
        platform = context.get("platform", "Instagram Reels")
        category = context.get("category", "Technology")
        objective = context.get("objective", "Retention")
        
        # Multimodal Video Audit Data
        audit = context.get("video_audit", {})
        tech = audit.get("technical", {})
        vision = audit.get("vision", {})
        calib = audit.get("calibration", {})

        is_test = calib.get("is_synthetic_or_test", False)
        calibrated_score = calib.get("calibrated_hook_score", 50)
        
        user_prompt = f"""Evaluate the opening hook based on actual visual and technical inspection:
- Video File: {video_title} ({duration}s, {platform}, {category})
- Technical Orientation: {tech.get('aspect_ratio', '9:16')} (Is 9:16 Vertical: {tech.get('is_vertical_9_16', True)})
- Audio Stream Present: {tech.get('has_audio', True)}
- Visual Subject Detected: {vision.get('primary_visual_subject', 'Standard video')}
- Visual Hook Quality Score: {vision.get('visual_hook_score_1_to_10', 5)}/10
- Production Quality Score: {vision.get('production_quality_score_1_to_10', 5)}/10
- Has High-Contrast Captions: {vision.get('has_readable_captions', False)}
- Human Subject Present: {vision.get('human_subject_present', False)}
- Objective Visual Defects Detected: {vision.get('objective_visual_flaws', [])}
- Visual Auditor Summary: {vision.get('visual_summary', 'No summary')}
- Calibrated Real-World Hook Target: Around {calibrated_score}/100

Be ruthless. If the visual shows a test card, placeholder, dark/static image, or lacks captions, score it severely low (10-30 range). Provide 3 high-impact hook rewrites."""

        # Calibrated fallback
        if is_test or calibrated_score <= 25:
            fallback = {
                "hook_score": calibrated_score,
                "retention_0_to_3s_pct": 18.5,
                "hook_grade": "F / Unreleasable",
                "verdict": "Catastrophic feed abandonment. Viewers swipe away before second 1.",
                "analysis": f"The video displays placeholder or test footage with zero human engagement or visual curiosity. Over 85% of mobile viewers will swipe past instantly.",
                "curiosity_gap": {"level": "Non-Existent", "explanation": "No tension, question, or transformation is established."},
                "pattern_interrupt_present": False,
                "friction_points": [
                    "Non-content or test card visual immediately signals low quality to viewers",
                    "Complete absence of on-screen text hook or human focal point"
                ],
                "hook_rewrites": [
                    {
                        "style": "Pattern Interrupt",
                        "spoken_script": "Wait—do not scroll past this if you struggle with daily focus.",
                        "visual_cue": "Instant high-contrast visual shock with bold yellow centered typography.",
                        "expected_lift": "+35% initial retention"
                    },
                    {
                        "style": "Curiosity Gap",
                        "spoken_script": "This single 10-second change fixed my entire morning routine.",
                        "visual_cue": "Start mid-motion revealing an impressive finished result.",
                        "expected_lift": "+40% initial retention"
                    },
                    {
                        "style": "Bold Outcome Claim",
                        "spoken_script": "Stop wasting hours on complex planners—here is what actually works.",
                        "visual_cue": "Side-by-side split screen showing chaos vs. streamlined solution.",
                        "expected_lift": "+30% initial retention"
                    }
                ],
                "editor_directive": "Scrap the placeholder opening entirely. Shoot a real human or dynamic product hook with bold on-screen captions."
            }
        else:
            fallback = {
                "hook_score": calibrated_score,
                "retention_0_to_3s_pct": round(calibrated_score * 0.9, 1),
                "hook_grade": "C / Average",
                "verdict": "Functional opening, but lacks immediate scroll-stopping curiosity.",
                "analysis": "The opening establishes context adequately, but requires a stronger pattern interrupt in the first 1.5 seconds to retain impatient casual scrollers.",
                "curiosity_gap": {"level": "Medium", "explanation": "Presents topic but lacks an urgent unsolved mystery."},
                "pattern_interrupt_present": False,
                "friction_points": ["Transitional delay before core payoff", "Captions lack dynamic motion"],
                "hook_rewrites": [
                    {
                        "style": "Pattern Interrupt",
                        "spoken_script": "Before you try another habit tracker, watch this.",
                        "visual_cue": "Rapid zoom-in on the primary interface feature.",
                        "expected_lift": "+16% initial retention"
                    },
                    {
                        "style": "Curiosity Gap",
                        "spoken_script": "Why does almost every habit setup fail after week 2?",
                        "visual_cue": "High-contrast text card transitioning immediately into the fix.",
                        "expected_lift": "+22% initial retention"
                    },
                    {
                        "style": "Bold Outcome Claim",
                        "spoken_script": "How I automated my entire daily workflow in under 2 minutes.",
                        "visual_cue": "Fast-paced screen recording with sound effects.",
                        "expected_lift": "+18% initial retention"
                    }
                ],
                "editor_directive": "Cut opening 1.2 seconds of dead air. Front-load the final payoff immediately."
            }

        return self.call_llm_json(user_prompt, fallback_data=fallback)
