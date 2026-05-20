# Vision Model Prompt

Use this prompt when asking a vision model to help structure UI comparison. Replace placeholders with the actual image paths or attachments.

```text
You are comparing two UI screenshots:
- Reference/design screenshot: <reference>
- Candidate/implementation screenshot: <candidate>

Ignore the top device status information area, including time, signal, carrier, Wi-Fi, and battery. Do not report it as a difference.

Treat the reference as the source of truth. Analyze the candidate against it.

Before selecting issues, divide both screenshots into semantic UI regions and compare each region separately. Account for possible device-resolution or global-scale differences. If the candidate is uniformly larger/smaller but preserves anchors, hierarchy, readability, and region relationships, do not report that as an issue.

Return JSON only:
{
  "page_type": "full_screen_app|list_or_grid|media_immersive|bottom_sheet_or_dialog|empty_error_skeleton|other",
  "comparability": 0.0,
  "global_scale_assessment": {
    "has_uniform_scale_difference": false,
    "estimated_candidate_scale_vs_reference": 1.0,
    "scale_affects_usability_or_layout": false,
    "notes": "string"
  },
  "regions": [
    {
      "id": "string",
      "type": "status_ignored|header|tabs|search|content_flow|list|grid|media|overlay|dialog|bottom_sheet|bottom_nav|empty_state|other",
      "reference_box": [x, y, w, h],
      "candidate_box": [x, y, w, h],
      "anchor": "top|bottom|center|content_flow|none",
      "importance": "low|medium|high",
      "assessment": "match|acceptable_scale_delta|minor_delta|issue"
    }
  ],
  "dynamic_regions": [
    {
      "reason": "string",
      "reference_box": [x, y, w, h],
      "candidate_box": [x, y, w, h]
    }
  ],
  "candidate_issues": [
    {
      "area": "UI region name",
      "problem": "Actionable problem in the candidate implementation",
      "likely_code_area": "Likely component/style/constraint to inspect",
      "severity": "low|medium|high|critical"
    }
  ]
}

Issue selection rules:
- Include zero, one, or two candidate_issues. Return an empty array when there is no clearly actionable problem.
- Prefer anchor, overlay/layer, region shift, clipping/wrapping, media fit, and opacity/color issues that are visible and code-locatable.
- Do not report tiny or non-actionable differences. Do not add a second issue just to have two.
- Do not report a globally consistent scale/resolution difference unless it causes clipping, overlap, wrong item count, broken anchoring, or readability problems.
- Do not say only that two things are different. Describe the implementation problem and likely cause.
- Do not include phone status bar/time/battery/signal differences.
```
