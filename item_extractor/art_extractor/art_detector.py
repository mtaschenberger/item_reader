import cv2

from item_extractor.models import BoundingBox

def get_kernel(size):
    if size <500:
        return  [5,5]
    elif size <1000:
        return [7,7]
    elif size <1500:
        return [7,7]
    else:  return [21,21]


class ArtworkDetector:
    def __init__(self):
        # No need to load a custom model
        pass
        
    def detect(self, image_path):
        """
        Detect artwork in an image using contour detection and image processing
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image at {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, get_kernel(image.shape[0]), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area to find potential artwork
        min_area = 1000 * 500 / image.shape[0]  # Adjust based on your images
        artwork_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
        
        boxes = []
        for contour in artwork_contours:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            box = BoundingBox(x, y, x+w, y+h)
            # Calculate aspect ratio
            boxes.append(box)
            
        return max(boxes)
