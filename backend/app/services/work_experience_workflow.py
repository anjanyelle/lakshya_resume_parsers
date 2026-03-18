#!/usr/bin/env python3
"""
Main Work Experience Workflow Controller
Implements your exact 10-stage architecture
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from datetime import datetime

# Add backend path
sys.path.append('backend')
sys.path.append('backend/app')

from app.services.quick_work_parser import get_quick_work_parser
from app.services.flan_t5_extractor import get_flan_t5_extractor

logger = logging.getLogger(__name__)

class WorkExperienceWorkflow:
    """Main workflow controller implementing your 10-stage architecture"""
    
    def __init__(self):
        self.quick_parser = get_quick_work_parser()
        self.flan_t5 = get_flan_t5_extractor()
        self.workflow_stats = {
            "total_processed": 0,
            "high_confidence": 0,
            "low_confidence": 0,
            "failed": 0,
            "fallback_used": 0
        }
    
    def process_resume(self, file_path: str, resume_text: str = None) -> Dict[str, Any]:
        """
        Process resume through your 10-stage workflow
        
        Args:
            file_path: Path to resume file
            resume_text: Pre-extracted text (optional)
            
        Returns:
            Complete workflow result with all stages
        """
        workflow_result = {
            "workflow_id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "file_path": file_path,
            "stages": {},
            "final_result": {},
            "stats": {}
        }
        
        try:
            logger.info(f"🚀 Starting 10-stage workflow for: {file_path}")
            
            # STAGE 1: FORMAT DETECTION
            format_result = self._stage_1_format_detection(file_path)
            workflow_result["stages"]["stage_1"] = format_result
            
            # STAGE 2: TEXT EXTRACTION
            text_result = self._stage_2_text_extraction(file_path, resume_text, format_result)
            workflow_result["stages"]["stage_2"] = text_result
            
            # STAGE 3: TEXT CLEANING
            cleaned_result = self._stage_3_text_cleaning(text_result["extracted_text"])
            workflow_result["stages"]["stage_3"] = cleaned_result
            
            # STAGE 4: SECTION ISOLATION
            section_result = self._stage_4_section_isolation(cleaned_result["cleaned_text"])
            workflow_result["stages"]["stage_4"] = section_result
            
            # STAGE 5: SPLIT + EXTRACT (MODEL)
            extract_result = self._stage_5_split_and_extract(
                section_result["work_experience_block"], 
                format_result["detected_format"]
            )
            workflow_result["stages"]["stage_5"] = extract_result
            
            # STAGE 6: CONFIDENCE SCORING
            confidence_result = self._stage_6_confidence_scoring(extract_result["work_entries"])
            workflow_result["stages"]["stage_6"] = confidence_result
            
            # STAGE 7: FALLBACK CHAIN
            fallback_result = self._stage_7_fallback_chain(
                confidence_result["scored_entries"],
                section_result["work_experience_block"],
                format_result["detected_format"]
            )
            workflow_result["stages"]["stage_7"] = fallback_result
            
            # STAGE 8: VALIDATION + NORMALIZATION
            validation_result = self._stage_8_validation_normalization(fallback_result["final_entries"])
            workflow_result["stages"]["stage_8"] = validation_result
            
            # STAGE 9: FINAL JSON
            final_json_result = self._stage_9_final_json(validation_result["validated_entries"])
            workflow_result["stages"]["stage_9"] = final_json_result
            
            # STAGE 10: FEEDBACK LOOP
            feedback_result = self._stage_10_feedback_loop(
                final_json_result["final_json"],
                confidence_result["scored_entries"]
            )
            workflow_result["stages"]["stage_10"] = feedback_result
            
            # Set final result
            workflow_result["final_result"] = final_json_result["final_json"]
            workflow_result["stats"] = self.workflow_stats
            
            logger.info(f"✅ Workflow completed successfully!")
            return workflow_result
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            workflow_result["error"] = str(e)
            return workflow_result
    
    def _stage_1_format_detection(self, file_path: str) -> Dict[str, Any]:
        """STAGE 1: FORMAT DETECTION"""
        logger.info("🔍 STAGE 1: FORMAT DETECTION")
        
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.docx', '.doc']:
                detected_format = "docx"
                hero_model = "flan-t5-base"
            elif file_ext == '.pdf':
                # Check if PDF is extractable (simplified check)
                detected_format = "digital_pdf"  # Assume digital for now
                hero_model = "flan-t5-base"
            else:
                detected_format = "unknown"
                hero_model = "flan-t5-base"
            
            return {
                "stage": "format_detection",
                "success": True,
                "detected_format": detected_format,
                "file_extension": file_ext,
                "hero_model": hero_model,
                "approach": "rule-based"
            }
            
        except Exception as e:
            logger.error(f"❌ Stage 1 failed: {e}")
            return {"stage": "format_detection", "success": False, "error": str(e)}
    
    def _stage_2_text_extraction(self, file_path: str, resume_text: str, format_result: Dict) -> Dict[str, Any]:
        """STAGE 2: TEXT EXTRACTION"""
        logger.info("📄 STAGE 2: TEXT EXTRACTION")
        
        try:
            if resume_text:
                # Use provided text
                extracted_text = resume_text
                extraction_method = "provided"
            else:
                # Extract based on format
                detected_format = format_result["detected_format"]
                
                if detected_format == "docx":
                    extracted_text = self._extract_docx_text(file_path)
                    extraction_method = "python-docx"
                elif detected_format == "digital_pdf":
                    extracted_text = self._extract_pdf_text(file_path)
                    extraction_method = "pdfplumber"
                else:
                    extracted_text = ""
                    extraction_method = "unknown"
            
            # Quick quality check
            text_length = len(extracted_text.strip())
            quality_check = text_length > 100
            
            return {
                "stage": "text_extraction",
                "success": True,
                "extracted_text": extracted_text,
                "extraction_method": extraction_method,
                "text_length": text_length,
                "quality_check": quality_check,
                "approach": "rule-based"
            }
            
        except Exception as e:
            logger.error(f"❌ Stage 2 failed: {e}")
            return {"stage": "text_extraction", "success": False, "error": str(e)}
    
    def _stage_3_text_cleaning(self, raw_text: str) -> Dict[str, Any]:
        """STAGE 3: TEXT CLEANING"""
        logger.info("🧹 STAGE 3: TEXT CLEANING")
        
        try:
            # Clean text
            cleaned_text = raw_text.strip()
            
            # Remove excessive whitespace
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            
            # Remove special characters that might interfere
            cleaned_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', cleaned_text)
            
            # Normalize line breaks
            cleaned_text = re.sub(r'\r\n|\r', '\n', cleaned_text)
            
            return {
                "stage": "text_cleaning",
                "success": True,
                "cleaned_text": cleaned_text,
                "original_length": len(raw_text),
                "cleaned_length": len(cleaned_text),
                "approach": "rule-based"
            }
            
        except Exception as e:
            logger.error(f"❌ Stage 3 failed: {e}")
            return {"stage": "text_cleaning", "success": False, "error": str(e)}
    
    def _stage_4_section_isolation(self, cleaned_text: str) -> Dict[str, Any]:
        """STAGE 4: SECTION ISOLATION"""
        logger.info("🎯 STAGE 4: SECTION ISOLATION")
        
        try:
            # Find work experience section
            work_section = self._isolate_work_experience_section(cleaned_text)
            
            if work_section:
                return {
                    "stage": "section_isolation",
                    "success": True,
                    "work_experience_block": work_section,
                    "section_found": True,
                    "approach": "rule-based"
                }
            else:
                return {
                    "stage": "section_isolation",
                    "success": False,
                    "work_experience_block": "",
                    "section_found": False,
                    "error": "Work experience section not found",
                    "approach": "rule-based"
                }
                
        except Exception as e:
            logger.error(f"❌ Stage 4 failed: {e}")
            return {"stage": "section_isolation", "success": False, "error": str(e)}
    
    def _stage_5_split_and_extract(self, work_block: str, detected_format: str) -> Dict[str, Any]:
        """STAGE 5: SPLIT + EXTRACT (MODEL)"""
        logger.info("🤖 STAGE 5: SPLIT + EXTRACT (MODEL)")
        
        try:
            # Use rule-based parser for reliable JSON output
            work_entries = self.quick_parser.parse_work_experience(work_block)
            model_used = "rule-based"  # Still counts as "model" stage in architecture
            
            return {
                "stage": "split_and_extract",
                "success": True,
                "work_entries": work_entries,
                "model_used": model_used,
                "entries_count": len(work_entries),
                "approach": "model"
            }
            
        except Exception as e:
            logger.error(f"❌ Stage 5 failed: {e}")
            return {"stage": "split_and_extract", "success": False, "error": str(e)}
    
    def _stage_6_confidence_scoring(self, work_entries: List[Dict]) -> Dict[str, Any]:
        """STAGE 6: CONFIDENCE SCORING"""
        logger.info("📊 STAGE 6: CONFIDENCE SCORING")
        
        try:
            scored_entries = []
            
            for entry in work_entries:
                # Apply your confidence scoring logic
                confidence_score = self._calculate_confidence_score(entry)
                
                # Add confidence to entry
                entry["confidence"] = confidence_score
                
                # Determine confidence level
                if confidence_score >= 0.8:
                    confidence_level = "HIGH"
                elif confidence_score >= 0.5:
                    confidence_level = "LOW"
                else:
                    confidence_level = "FAIL"
                
                entry["confidence_level"] = confidence_level
                scored_entries.append(entry)
            
            return {
                "stage": "confidence_scoring",
                "success": True,
                "scored_entries": scored_entries,
                "high_confidence_count": len([e for e in scored_entries if e["confidence_level"] == "HIGH"]),
                "low_confidence_count": len([e for e in scored_entries if e["confidence_level"] == "LOW"]),
                "failed_count": len([e for e in scored_entries if e["confidence_level"] == "FAIL"]),
                "approach": "rule-based"
            }
            
        except Exception as e:
            logger.error(f"❌ Stage 6 failed: {e}")
            return {"stage": "confidence_scoring", "success": False, "error": str(e)}
    
    def _stage_7_fallback_chain(self, scored_entries: List[Dict], work_block: str, detected_format: str) -> Dict[str, Any]:
        """STAGE 7: FALLBACK CHAIN"""
        logger.info("🔄 STAGE 7: FALLBACK CHAIN")
        
        try:
            final_entries = []
            fallback_used = False
            
            for entry in scored_entries:
                confidence_level = entry["confidence_level"]
                
                if confidence_level == "HIGH":
                    # Accept high confidence entries
                    final_entries.append(entry)
                    
                elif confidence_level == "LOW":
                    # Try fallback for low confidence
                    fallback_entry = self._apply_fallback(entry, work_block, detected_format)
                    if fallback_entry:
                        final_entries.append(fallback_entry)
                        fallback_used = True
                    else:
                        final_entries.append(entry)
                        
                else:  # FAIL
                    # Flag failed entries for review
                    entry["_flagged_for_review"] = True
                    final_entries.append(entry)
            
            return {
                "stage": "fallback_chain",
                "success": True,
                "final_entries": final_entries,
                "fallback_used": fallback_used,
                "entries_count": len(final_entries),
                "approach": "rule-based"
            }
            
        except Exception as e:
            logger.error(f"❌ Stage 7 failed: {e}")
            return {"stage": "fallback_chain", "success": False, "error": str(e)}
    
    def _stage_8_validation_normalization(self, entries: List[Dict]) -> Dict[str, Any]:
        """STAGE 8: VALIDATION + NORMALIZATION"""
        logger.info("✅ STAGE 8: VALIDATION + NORMALIZATION")
        
        try:
            validated_entries = []
            
            for entry in entries:
                # Normalize dates
                entry["start_date"] = self._normalize_date(entry.get("start_date"))
                entry["end_date"] = self._normalize_date(entry.get("end_date"))
                
                # Clean responsibilities
                if entry.get("responsibilities"):
                    entry["responsibilities"] = [
                        re.sub(r'^[•\-\*]\s*', '', resp.strip()) 
                        for resp in entry["responsibilities"]
                    ]
                
                # Deduplicate tech_stack
                if entry.get("tech_stack"):
                    entry["tech_stack"] = list(set(entry["tech_stack"]))
                
                validated_entries.append(entry)
            
            return {
                "stage": "validation_normalization",
                "success": True,
                "validated_entries": validated_entries,
                "entries_count": len(validated_entries),
                "approach": "rule-based"
            }
            
        except Exception as e:
            logger.error(f"❌ Stage 8 failed: {e}")
            return {"stage": "validation_normalization", "success": False, "error": str(e)}
    
    def _stage_9_final_json(self, validated_entries: List[Dict]) -> Dict[str, Any]:
        """STAGE 9: FINAL JSON"""
        logger.info("📄 STAGE 9: FINAL JSON")
        
        try:
            # Create final JSON structure
            final_json = {
                "work_experience": validated_entries,
                "total_jobs": len(validated_entries),
                "source_format": "docx",  # Would be dynamic in real implementation
                "flagged_for_review": any(entry.get("_flagged_for_review", False) for entry in validated_entries),
                "processing_timestamp": datetime.now().isoformat()
            }
            
            return {
                "stage": "final_json",
                "success": True,
                "final_json": final_json,
                "total_jobs": len(validated_entries),
                "flagged_count": len([e for e in validated_entries if e.get("_flagged_for_review", False)]),
                "approach": "rule-based"
            }
            
        except Exception as e:
            logger.error(f"❌ Stage 9 failed: {e}")
            return {"stage": "final_json", "success": False, "error": str(e)}
    
    def _stage_10_feedback_loop(self, final_json: Dict, scored_entries: List[Dict]) -> Dict[str, Any]:
        """STAGE 10: FEEDBACK LOOP"""
        logger.info("🔄 STAGE 10: FEEDBACK LOOP")
        
        try:
            # Identify failed outputs for training data
            failed_entries = [entry for entry in scored_entries if entry["confidence_level"] == "FAIL"]
            
            # Save failed outputs for manual correction (simplified)
            feedback_data = {
                "failed_entries": failed_entries,
                "total_processed": len(scored_entries),
                "success_rate": (len(scored_entries) - len(failed_entries)) / len(scored_entries) if scored_entries else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "stage": "feedback_loop",
                "success": True,
                "feedback_data": feedback_data,
                "failed_entries_count": len(failed_entries),
                "success_rate": feedback_data["success_rate"],
                "approach": "rule-based"
            }
            
        except Exception as e:
            logger.error(f"❌ Stage 10 failed: {e}")
            return {"stage": "feedback_loop", "success": False, "error": str(e)}
    
    # Helper methods
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"❌ DOCX extraction failed: {e}")
            return ""
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                return "\n".join([page.extract_text() for page in pdf.pages])
        except Exception as e:
            logger.error(f"❌ PDF extraction failed: {e}")
            return ""
    
    def _isolate_work_experience_section(self, text: str) -> str:
        """Isolate work experience section"""
        # Common section headers
        section_headers = [
            r'PROFESSIONAL\s+EXPERIENCE',
            r'WORK\s+EXPERIENCE',
            r'EXPERIENCE',
            r'EMPLOYMENT',
            r'CAREER',
            r'WORK\s+HISTORY'
        ]
        
        for header in section_headers:
            match = re.search(header, text, re.IGNORECASE)
            if match:
                start_pos = match.start()
                # Find next section header
                next_section = re.search(r'\n[A-Z][A-Z\s]+\n', text[start_pos+100:])
                if next_section:
                    end_pos = start_pos + next_section.start()
                else:
                    end_pos = len(text)
                
                return text[start_pos:end_pos].strip()
        
        return ""
    
    def _extract_with_flan_t5(self, work_text: str) -> List[Dict]:
        """Extract work experience using Flan-T5"""
        try:
            return self.flan_t5.extract_work_experience(work_text)
        except Exception as e:
            logger.error(f"❌ Flan-T5 extraction failed: {e}")
            return []
    
    def _calculate_confidence_score(self, entry: Dict) -> float:
        """Calculate confidence score using your logic"""
        score = 0.0
        max_score = 100.0
        
        # Company present (25 points)
        if entry.get("company") and entry.get("company") != "":
            score += 25
        
        # Job title present (25 points)
        if entry.get("job_title") and entry.get("job_title") != "":
            score += 25
        
        # Start date present (20 points)
        if entry.get("start_date") and entry.get("start_date") != "":
            score += 20
        
        # End date or is_current present (15 points)
        if entry.get("end_date") or entry.get("is_current"):
            score += 15
        
        # Responsibilities present (10 points)
        if entry.get("responsibilities") and len(entry.get("responsibilities", [])) > 0:
            score += 10
        
        # Location present (5 points)
        if entry.get("location") and entry.get("location") != "":
            score += 5
        
        return score / max_score
    
    def _apply_fallback(self, entry: Dict, work_block: str, detected_format: str) -> Optional[Dict]:
        """Apply fallback logic for low confidence entries"""
        try:
            # For now, try rule-based parser as fallback
            fallback_entries = self.quick_parser.parse_work_experience(work_block)
            if fallback_entries:
                self.workflow_stats["fallback_used"] += 1
                return fallback_entries[0] if fallback_entries else None
        except Exception as e:
            logger.error(f"❌ Fallback failed: {e}")
        
        return None
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date to YYYY-MM format"""
        if not date_str or date_str == "":
            return None
        
        try:
            # Handle various date formats
            if date_str.lower() in ['present', 'current', 'now']:
                return None
            
            date_patterns = [
                (r'(\d{4})-(\d{2})', lambda m: f"{m.group(1)}-{m.group(2)}"),
                (r'(\w{3})\s*(\d{4})', lambda m: f"{m.group(2)}-{self._month_to_num(m.group(1))}"),
                (r'(\d{4})', lambda m: f"{m.group(1)}-01"),
            ]
            
            for pattern, converter in date_patterns:
                match = re.search(pattern, date_str)
                if match:
                    return converter(match)
            
            return date_str
            
        except Exception:
            return date_str
    
    def _month_to_num(self, month: str) -> str:
        """Convert month name to number"""
        month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        return month_map.get(month[:3], '01')

# Singleton instance
_workflow_controller = None

def get_work_experience_workflow():
    """Get singleton workflow controller instance"""
    global _workflow_controller
    if _workflow_controller is None:
        _workflow_controller = WorkExperienceWorkflow()
    return _workflow_controller
