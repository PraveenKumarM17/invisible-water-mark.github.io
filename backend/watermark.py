import cv2
import numpy as np
import uuid
import os

def dct_watermark(image, watermark_text, alpha=0.1):
    # Convert to YUV
    yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    Y = yuv[:,:,0]
    
    # Apply DCT
    dct = cv2.dct(np.float32(Y))
    
    # Generate watermark pattern from text
    h, w = Y.shape
    watermark = np.zeros((h, w), np.float32)
    cv2.putText(watermark, watermark_text, (w//4, h//2), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, 1, 2)
    
    # Embed watermark
    dct_watermarked = dct + alpha * watermark
    
    # Inverse DCT
    watermarked_y = cv2.idct(dct_watermarked)
    yuv[:,:,0] = watermarked_y
    
    # Convert back to BGR
    return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

def embed_watermark(image_path, watermark_text, upload_folder='uploads'):
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image could not be loaded")
    
    # Apply watermark
    watermarked = dct_watermark(image, watermark_text)
    
    # Generate unique filename
    filename = f"watermarked_{uuid.uuid4()}.png"
    output_path = os.path.join(upload_folder, filename)
    
    # Save watermarked image
    if not cv2.imwrite(output_path, watermarked):
        raise ValueError("Failed to save watermarked image")
        
    media_id = str(uuid.uuid4())
    return media_id, output_path

def extract_watermark(image_path, alpha=0.1):
    # Read watermarked image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image could not be loaded")
    
    # Convert to YUV and get Y channel
    yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    Y = yuv[:,:,0]
    
    # Apply DCT
    dct = cv2.dct(np.float32(Y))
    
    # Extract approximate watermark
    extracted = dct / alpha
    
    return "Watermark Present" if np.mean(extracted) > 0.5 else "No Watermark Detected"