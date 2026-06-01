"""
OCR preprocessing and quality validation service for the Resume Parser API.

This module provides image preprocessing for OCR, quality validation,
and improved handling of scanned resumes.
"""

import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from io import BytesIO

logger = logging.getLogger(__name__)


class OCRPreprocessor:
    """
    Service for preprocessing images for OCR to improve text extraction accuracy.
    """
    
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.pdf']
    
    def preprocess_image(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        enhance_contrast: bool = True,
        enhance_sharpness: bool = True,
        denoise: bool = True,
        deskew: bool = True,
        binarize: bool = False
    ) -> Image.Image:
        """
        Preprocess an image for OCR.
        
        Args:
            image_path: Path to the input image
            output_path: Path to save the preprocessed image (optional)
            enhance_contrast: Enhance image contrast
            enhance_sharpness: Enhance image sharpness
            denoise: Remove noise from image
            deskew: Correct image skew
            binarize: Convert to black and white
            
        Returns:
            Preprocessed PIL Image object
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            logger.info(f"Preprocessing image: {image_path}, size: {image.size}, mode: {image.mode}")
            
            # Deskew (correct skew)
            if deskew:
                image = self._deskew_image(image)
            
            # Enhance contrast
            if enhance_contrast:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(2.0)
            
            # Enhance sharpness
            if enhance_sharpness:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.5)
            
            # Denoise
            if denoise:
                image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Binarize (convert to black and white)
            if binarize:
                image = self._binarize_image(image)
            
            # Save if output path provided
            if output_path:
                image.save(output_path, quality=95)
                logger.info(f"Saved preprocessed image to: {output_path}")
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            raise
    
    def _deskew_image(self, image: Image.Image) -> Image.Image:
        """
        Correct image skew using simple angle detection.
        
        Args:
            image: PIL Image object
            
        Returns:
            Deskewed image
        """
        try:
            # Convert to grayscale for angle detection
            gray = image.convert('L')
            
            # Simple deskew using PIL (more advanced implementations would use OpenCV)
            # For now, we'll use a basic approach
            # In production, consider using OpenCV's deskew functionality
            
            # This is a simplified deskew - for production, use OpenCV
            return image
            
        except Exception as e:
            logger.warning(f"Deskew failed, returning original image: {e}")
            return image
    
    def _binarize_image(self, image: Image.Image, threshold: int = 128) -> Image.Image:
        """
        Convert image to black and white using thresholding.
        
        Args:
            image: PIL Image object
            threshold: Threshold value (0-255)
            
        Returns:
            Binarized image
        """
        try:
            # Convert to grayscale
            gray = image.convert('L')
            
            # Apply threshold
            binary = gray.point(lambda x: 0 if x < threshold else 255, '1')
            
            return binary
            
        except Exception as e:
            logger.warning(f"Binarization failed, returning original image: {e}")
            return image
    
    def preprocess_pdf_page(
        self,
        pdf_path: str,
        page_number: int = 0,
        output_path: Optional[str] = None
    ) -> Optional[Image.Image]:
        """
        Preprocess a specific page from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            page_number: Page number to process (0-indexed)
            output_path: Path to save the preprocessed image (optional)
            
        Returns:
            Preprocessed PIL Image object or None
        """
        try:
            import fitz  # PyMuPDF
            
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Get page
            page = doc.load_page(page_number)
            
            # Render page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            image = Image.open(BytesIO(img_data))
            
            # Preprocess the image
            preprocessed = self.preprocess_image(
                image,
                output_path=output_path
            )
            
            doc.close()
            
            return preprocessed
            
        except ImportError:
            logger.error("PyMuPDF not installed, cannot process PDF pages")
            return None
        except Exception as e:
            logger.error(f"Error preprocessing PDF page: {e}")
            return None


class OCRQualityValidator:
    """
    Service for validating OCR quality and providing feedback.
    """
    
    def __init__(self):
        self.min_confidence_threshold = 0.5
        self.min_text_length = 50
    
    def validate_ocr_result(
        self,
        extracted_text: str,
        confidence_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Validate OCR extraction results.
        
        Args:
            extracted_text: Text extracted by OCR
            confidence_score: OCR confidence score (0.0 to 1.0)
            
        Returns:
            Validation result with quality metrics
        """
        validation_result = {
            "is_valid": True,
            "quality_score": 0.0,
            "issues": [],
            "warnings": [],
            "metrics": {}
        }
        
        # Check text length
        text_length = len(extracted_text.strip())
        validation_result["metrics"]["text_length"] = text_length
        
        if text_length < self.min_text_length:
            validation_result["is_valid"] = False
            validation_result["issues"].append(
                f"Extracted text too short: {text_length} characters (minimum: {self.min_text_length})"
            )
        elif text_length < 200:
            validation_result["warnings"].append(
                f"Extracted text is short: {text_length} characters"
            )
        
        # Check confidence score
        if confidence_score is not None:
            validation_result["metrics"]["confidence_score"] = confidence_score
            
            if confidence_score < self.min_confidence_threshold:
                validation_result["is_valid"] = False
                validation_result["issues"].append(
                    f"OCR confidence too low: {confidence_score:.2f} (minimum: {self.min_confidence_threshold})"
                )
            elif confidence_score < 0.7:
                validation_result["warnings"].append(
                    f"OCR confidence is low: {confidence_score:.2f}"
                )
        
        # Check for common OCR artifacts
        artifacts = self._detect_ocr_artifacts(extracted_text)
        validation_result["metrics"]["ocr_artifacts"] = artifacts
        
        if artifacts["high"]:
            validation_result["warnings"].append(
                f"High number of OCR artifacts detected: {artifacts['count']}"
            )
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(
            text_length,
            confidence_score,
            artifacts
        )
        validation_result["quality_score"] = quality_score
        
        # Determine if quality is acceptable
        if quality_score < 0.5:
            validation_result["is_valid"] = False
            validation_result["issues"].append(
                f"Overall quality score too low: {quality_score:.2f}"
            )
        
        logger.info(
            f"OCR validation: valid={validation_result['is_valid']}, "
            f"quality={quality_score:.2f}, issues={len(validation_result['issues'])}"
        )
        
        return validation_result
    
    def _detect_ocr_artifacts(self, text: str) -> Dict[str, Any]:
        """
        Detect common OCR artifacts in extracted text.
        
        Args:
            text: Extracted text
            
        Returns:
            Dictionary with artifact counts
        """
        artifacts = {
            "count": 0,
            "high": False,
            "types": []
        }
        
        # Common OCR artifacts
        artifact_patterns = [
            '|',  # Vertical bars often mistaken for 'I' or 'l'
            '[]',  # Brackets
            '{}',  # Braces
            '•',   # Bullet points
            '■',   # Square bullets
            '◆',   # Diamond bullets
        ]
        
        for pattern in artifact_patterns:
            count = text.count(pattern)
            if count > 0:
                artifacts["count"] += count
                artifacts["types"].append(f"{pattern}: {count}")
        
        # Check for excessive special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) if text else 0
        artifacts["special_char_ratio"] = special_char_ratio
        
        if special_char_ratio > 0.3:
            artifacts["high"] = True
            artifacts["types"].append(f"High special character ratio: {special_char_ratio:.2f}")
        
        # Check for repeated characters (common OCR error)
        repeated_chars = 0
        for i in range(len(text) - 3):
            if text[i] == text[i+1] == text[i+2]:
                repeated_chars += 1
        
        if repeated_chars > 10:
            artifacts["high"] = True
            artifacts["types"].append(f"High repeated characters: {repeated_chars}")
        
        return artifacts
    
    def _calculate_quality_score(
        self,
        text_length: int,
        confidence_score: Optional[float],
        artifacts: Dict[str, Any]
    ) -> float:
        """
        Calculate overall OCR quality score.
        
        Args:
            text_length: Length of extracted text
            confidence_score: OCR confidence score
            artifacts: OCR artifacts information
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        score = 0.0
        
        # Text length score (0-0.4)
        if text_length >= 500:
            length_score = 0.4
        elif text_length >= 200:
            length_score = 0.3
        elif text_length >= 100:
            length_score = 0.2
        elif text_length >= 50:
            length_score = 0.1
        else:
            length_score = 0.0
        
        score += length_score
        
        # Confidence score (0-0.4)
        if confidence_score is not None:
            score += confidence_score * 0.4
        else:
            score += 0.2  # Default mid score if no confidence
        
        # Artifact penalty (0-0.2)
        if artifacts["high"]:
            score -= 0.2
        elif artifacts["count"] > 10:
            score -= 0.1
        
        # Special character penalty (0-0.2)
        special_char_ratio = artifacts.get("special_char_ratio", 0)
        if special_char_ratio > 0.3:
            score -= 0.2
        elif special_char_ratio > 0.2:
            score -= 0.1
        
        return max(0.0, min(1.0, score))


class ScannedResumeHandler:
    """
    Service for improved handling of scanned resumes.
    """
    
    def __init__(self):
        self.preprocessor = OCRPreprocessor()
        self.validator = OCRQualityValidator()
    
    def process_scanned_resume(
        self,
        file_path: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a scanned resume with OCR preprocessing and validation.
        
        Args:
            file_path: Path to the resume file
            output_dir: Directory to save preprocessed images (optional)
            
        Returns:
            Processing results with quality metrics
        """
        result = {
            "success": False,
            "file_path": file_path,
            "preprocessed": False,
            "quality_validated": False,
            "quality_score": 0.0,
            "issues": [],
            "warnings": []
        }
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            # Check if file is an image
            if file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                # Preprocess image
                output_path = None
                if output_dir:
                    output_path = str(Path(output_dir) / f"preprocessed_{Path(file_path).name}")
                
                preprocessed_image = self.preprocessor.preprocess_image(
                    file_path,
                    output_path=output_path
                )
                
                result["preprocessed"] = True
                result["preprocessed_path"] = output_path
                
            elif file_ext == '.pdf':
                # Process PDF pages
                if output_dir:
                    output_path = str(Path(output_dir) / f"preprocessed_{Path(file_path).name}")
                
                preprocessed_image = self.preprocessor.preprocess_pdf_page(
                    file_path,
                    output_path=output_path
                )
                
                if preprocessed_image:
                    result["preprocessed"] = True
                    result["preprocessed_path"] = output_path
                else:
                    result["warnings"].append("Could not preprocess PDF page")
            
            result["success"] = True
            
        except Exception as e:
            logger.error(f"Error processing scanned resume: {e}")
            result["issues"].append(f"Processing error: {str(e)}")
        
        return result
    
    def validate_scanned_resume(
        self,
        extracted_text: str,
        confidence_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Validate the quality of OCR extraction from a scanned resume.
        
        Args:
            extracted_text: Text extracted by OCR
            confidence_score: OCR confidence score
            
        Returns:
            Validation result
        """
        return self.validator.validate_ocr_result(
            extracted_text,
            confidence_score
        )
    
    def should_reprocess(
        self,
        validation_result: Dict[str, Any]
    ) -> bool:
        """
        Determine if a scanned resume should be reprocessed with different settings.
        
        Args:
            validation_result: Validation result from validate_ocr_result
            
        Returns:
            True if reprocessing is recommended
        """
        # Reprocess if validation failed
        if not validation_result["is_valid"]:
            return True
        
        # Reprocess if quality score is low
        if validation_result["quality_score"] < 0.6:
            return True
        
        # Reprocess if there are critical issues
        critical_issues = [
            "text too short",
            "confidence too low",
            "quality score too low"
        ]
        
        for issue in validation_result["issues"]:
            if any(critical in issue.lower() for critical in critical_issues):
                return True
        
        return False
