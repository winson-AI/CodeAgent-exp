# Scoring Schema

## Score JSON

```json
{
  "script_final_baseline_score": 0,
  "script_raw_baseline_score": 0,
  "script_scale_tolerant_baseline_score": 0,
  "overall": 0,
  "comparability": 1.0,
  "scores": {
    "state_match": 0,
    "region_alignment": 0,
    "fixed_component_layout": 0,
    "text_integrity": 0,
    "visual_style": 0,
    "media_fit": 0,
    "anchor_integrity": 0,
    "overlap_integrity": 0
  },
  "global_scale_assessment": {
    "has_uniform_scale_difference": false,
    "estimated_candidate_scale_vs_reference": 1.0,
    "scale_affects_usability_or_layout": false,
    "notes": ""
  },
  "evidence": {
    "script_report": "report/score.json",
    "notes": []
  }
}
```

All score fields are 0-100 except `comparability`, which is 0-1.

`script_final_baseline_score` should use the scale-tolerant script score. `script_raw_baseline_score` is retained only as evidence. Do not lower `overall` because of a raw score drop caused only by global resolution/scale differences.

## Issue JSON

```json
{
  "issues": [
    {
      "area": "string",
      "problem": "string",
      "likely_code_area": "string",
      "severity": "low|medium|high|critical",
      "evidence": "optional string"
    }
  ]
}
```

Constraints:

- Emit zero, one, or two issues only.
- Do not emit more than two issues.
- Do not force two issues. Return `[]` when no difference is clearly visible, code-locatable, and meaningful.
- Do not include phone status bar/time/battery/signal as an issue.
- Do not include a purely global scale/resolution difference unless it causes a concrete UI failure.
- `area` must name a UI region, not a coordinate-only description.
- `problem` must describe the layout/visual failure in implementation terms.
- `likely_code_area` must point to plausible code constraints, styles, or components.

## Combined JSON

When the user asks for both score and differences:

```json
{
  "overall": 0,
  "comparability": 1.0,
  "scores": {},
  "issues": []
}
```

Keep the issues list capped at two.
