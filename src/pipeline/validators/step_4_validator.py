"""
Step 4 Validator: One-Page Synopsis
Validates five-paragraph synopsis expanded from Step 2
"""

from typing import Tuple, List, Dict, Any

class Step4Validator:
	"""Validator for Step 4: One-Page Synopsis"""
	
	VERSION = "1.1.0"  # Updated: Increased paragraph length limits and more flexible keyword matching
	
	def validate(self, artifact: Dict[str, Any]) -> Tuple[bool, List[str]]:
		errors: List[str] = []
		paras = artifact.get("synopsis_paragraphs")
		if not isinstance(paras, dict):
			errors.append("MISSING: synopsis_paragraphs object")
			return False, errors
		required_keys = ["paragraph_1", "paragraph_2", "paragraph_3", "paragraph_4", "paragraph_5"]
		for key in required_keys:
			if not paras.get(key) or not isinstance(paras.get(key), str):
				errors.append(f"MISSING: {key} must be a non-empty string")
				continue
			text = paras[key].strip()
			if len(text) < 50:
				errors.append(f"TOO SHORT: {key} must be at least 50 characters")
			# Allow for up to 200-250 words per paragraph for a one-page synopsis
			# (5 paragraphs * 200 words = 1000 words = ~1 page)
			# But be flexible as AI may generate slightly longer paragraphs
			if len(text) > 1500:
				errors.append(f"TOO LONG: {key} exceeds reasonable paragraph length (>250 words)")
		# Specific checks - more flexible keyword matching for AI-generated content
		p2 = paras.get("paragraph_2", "").lower()
		p3 = paras.get("paragraph_3", "").lower()
		p4 = paras.get("paragraph_4", "").lower()
		
		# Check for forcing function concepts in P2 (more flexible)
		forcing_keywords = ["forces", "no way back", "cannot retreat", "irreversible", 
						   "must", "trapped", "committed", "no choice", "no escape", 
						   "point of no return", "can't turn back", "locked in"]
		if paras.get("paragraph_2") and not any(w in p2 for w in forcing_keywords):
			errors.append("P2 MISSING FORCING FUNCTION: state why retreat is impossible")
		
		# Check for moral pivot concepts in P3 (more flexible)
		pivot_keywords = ["pivot", "new tactic", "changes tactic", "moral premise",
						 "realizes", "understands", "learns", "discovers", "shift",
						 "transformation", "new approach", "different way", "changes course"]
		if paras.get("paragraph_3") and not any(w in p3 for w in pivot_keywords):
			errors.append("P3 MISSING MORAL PIVOT: show the identity/values shift and new tactic")
		
		# Check for bottleneck concepts in P4 (more flexible)
		bottleneck_keywords = ["bottleneck", "only path", "no options", "collapse",
							   "final", "last chance", "one way", "single choice",
							   "narrowing", "closing in", "cornered", "ultimatum"]
		if paras.get("paragraph_4") and not any(w in p4 for w in bottleneck_keywords):
			errors.append("P4 MISSING BOTTLENECK: collapse options and name the bottleneck")
		return len(errors) == 0, errors
	
	def fix_suggestions(self, errors: List[str]) -> List[str]:
		suggestions: List[str] = []
		for e in errors:
			if e.startswith("MISSING: synopsis_paragraphs"):
				suggestions.append("Output object must include 'synopsis_paragraphs' with 5 strings")
			elif e.startswith("MISSING: paragraph_"):
				suggestions.append("Write the missing paragraph mapping to the corresponding Step 2 sentence")
			elif "TOO SHORT" in e:
				suggestions.append("Expand with concrete causal detail; avoid notes; 2–5 sentences is fine")
			elif "P2 MISSING FORCING FUNCTION" in e:
				suggestions.append("State the event that makes retreat impossible and why")
			elif "P3 MISSING MORAL PIVOT" in e:
				suggestions.append("Show the values/identity hit and the pivot to a new tactic tied to moral premise")
			elif "P4 MISSING BOTTLENECK" in e:
				suggestions.append("Name the bottleneck and show options collapsing so only one path remains")
			else:
				suggestions.append("Add concrete cause→effect details; minimize named extras; keep plain style")
		return suggestions
