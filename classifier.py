"""
Phase 3: Vehicle Classification using ResNet50
Classifies vehicles into: Auto, Truck, Bus, Motocicleta
Using pre-trained ResNet50 from ImageNet with fine-tuning capability
"""

import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
import torch.nn as nn
from PIL import Image
import numpy as np
import cv2
from typing import Tuple, Dict


class VehicleClassifier:
    """
    ResNet50-based vehicle classifier for 4 vehicle types:
    0: Auto (sedan, hatchback, pickup)
    1: Truck (cargo truck, semi-truck)
    2: Bus (passenger bus, coach)
    3: Motocicleta (motorcycle, scooter)
    """
    
    def __init__(self, device='cpu', confidence_threshold=0.5):
        """
        Initialize vehicle classifier.
        
        Args:
            device: 'cpu' or 'cuda' (GPU)
            confidence_threshold: Min confidence for prediction
        """
        self.device = device
        self.confidence_threshold = confidence_threshold
        
        # Vehicle class labels
        self.classes = ['Auto', 'Truck', 'Bus', 'Motocicleta']
        self.class_colors = {
            0: (0, 255, 0),      # Auto - Green
            1: (255, 0, 0),      # Truck - Blue
            2: (0, 0, 255),      # Bus - Red
            3: (0, 255, 255)     # Motocicleta - Yellow
        }
        
        # Load pre-trained ResNet50
        weights = ResNet50_Weights.DEFAULT
        self.model = resnet50(weights=weights)
        
        # Replace final layer for 4 classes
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, len(self.classes))
        
        self.model = self.model.to(device)
        self.model.eval()
        
        # Image preprocessing (ImageNet normalization)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Use pre-trained weights without fine-tuning (transfer learning mode)
        for param in self.model.parameters():
            param.requires_grad = False
        self.model.fc.requires_grad = True
    
    def classify(self, image_cv2) -> Tuple[str, float, int]:
        """
        Classify vehicle from OpenCV image.
        
        Args:
            image_cv2: BGR image from OpenCV (numpy array)
        
        Returns:
            (class_name, confidence, class_id)
            Example: ('Auto', 0.92, 0)
        """
        if image_cv2 is None or image_cv2.size == 0:
            return 'Unknown', 0.0, -1
        
        try:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL
            pil_image = Image.fromarray(image_rgb)
            
            # Preprocess
            input_tensor = self.transform(pil_image)
            input_batch = input_tensor.unsqueeze(0).to(self.device)
            
            # Inference
            with torch.no_grad():
                output = self.model(input_batch)
                probabilities = torch.softmax(output, dim=1)
                confidence, predicted_class = torch.max(probabilities, 1)
            
            confidence_score = float(confidence[0].item())
            class_id = int(predicted_class[0].item())
            class_name = self.classes[class_id]
            
            return class_name, confidence_score, class_id
        
        except Exception as e:
            print(f"Classification error: {e}")
            return 'Unknown', 0.0, -1
    
    def classify_batch(self, images_cv2: list) -> list:
        """
        Classify multiple vehicles (batch processing).
        
        Args:
            images_cv2: List of BGR images
        
        Returns:
            List of (class_name, confidence, class_id) tuples
        """
        results = []
        for image in images_cv2:
            results.append(self.classify(image))
        return results
    
    def get_class_color(self, class_id: int) -> Tuple[int, int, int]:
        """Get BGR color for drawing overlay."""
        return self.class_colors.get(class_id, (128, 128, 128))
    
    def draw_classification(self, frame, bbox, class_name, confidence, class_id):
        """
        Draw classification result on frame.
        
        Args:
            frame: OpenCV image
            bbox: (x1, y1, x2, y2)
            class_name: Vehicle class name
            confidence: Classification confidence
            class_id: Class index
        
        Returns:
            Modified frame
        """
        x1, y1, x2, y2 = bbox
        color = self.get_class_color(class_id)
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Prepare label
        label = f"{class_name} ({confidence:.0%})"
        label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        
        # Draw background for text
        cv2.rectangle(frame, 
                     (x1, y1 - label_size[1] - 10),
                     (x1 + label_size[0] + 8, y1),
                     color, -1)
        
        # Draw text
        cv2.putText(frame, label, (x1 + 4, y1 - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def reset(self):
        """Reset model state if needed."""
        pass


class VehicleClassifierWithTracking:
    """
    Combines tracker + classifier for intelligent vehicle analysis.
    Classifies each tracked vehicle and stores classification history.
    """
    
    def __init__(self, classifier=None, device='cpu'):
        """
        Initialize classifier with tracking integration.
        
        Args:
            classifier: VehicleClassifier instance
            device: 'cpu' or 'cuda'
        """
        self.classifier = classifier or VehicleClassifier(device=device)
        self.tracked_classes = {}  # {object_id: class_info}
        self.classification_history = {}  # {object_id: [(class_id, conf, frame), ...]}
    
    def classify_tracked_objects(self, tracked_objects, frame) -> list:
        """
        Classify each tracked vehicle from frame.
        
        Args:
            tracked_objects: List from tracker.update()
            frame: OpenCV frame
        
        Returns:
            tracked_objects with added 'vehicle_class' field
        """
        results = []
        
        for obj in tracked_objects:
            obj_id = obj['object_id']
            x1, y1, x2, y2 = obj['bbox']
            
            # Extract vehicle ROI from frame
            roi = frame[max(0, y1):min(frame.shape[0], y2), 
                       max(0, x1):min(frame.shape[1], x2)]
            
            if roi.size == 0:
                # Use cached classification if available
                if obj_id in self.tracked_classes:
                    obj['vehicle_class'] = self.tracked_classes[obj_id]['class_name']
                    obj['vehicle_class_id'] = self.tracked_classes[obj_id]['class_id']
                    obj['class_confidence'] = self.tracked_classes[obj_id]['confidence']
                else:
                    obj['vehicle_class'] = 'Unknown'
                    obj['vehicle_class_id'] = -1
                    obj['class_confidence'] = 0.0
            else:
                # Classify vehicle
                class_name, confidence, class_id = self.classifier.classify(roi)
                
                obj['vehicle_class'] = class_name
                obj['vehicle_class_id'] = class_id
                obj['class_confidence'] = confidence
                
                # Store in cache (use highest confidence reading)
                if obj_id not in self.tracked_classes:
                    self.tracked_classes[obj_id] = {
                        'class_name': class_name,
                        'class_id': class_id,
                        'confidence': confidence
                    }
                else:
                    # Update if higher confidence
                    if confidence > self.tracked_classes[obj_id]['confidence']:
                        self.tracked_classes[obj_id].update({
                            'class_name': class_name,
                            'class_id': class_id,
                            'confidence': confidence
                        })
                
                # Store in history
                if obj_id not in self.classification_history:
                    self.classification_history[obj_id] = []
                self.classification_history[obj_id].append({
                    'class_id': class_id,
                    'confidence': confidence,
                    'frame': len(self.classification_history[obj_id])
                })
            
            results.append(obj)
        
        return results
    
    def get_best_classification(self, obj_id) -> Dict:
        """
        Get the best (highest confidence) classification for a tracked object.
        
        Args:
            obj_id: Object ID from tracker
        
        Returns:
            Dict with class_name, class_id, confidence
        """
        if obj_id in self.tracked_classes:
            return self.tracked_classes[obj_id]
        return {'class_name': 'Unknown', 'class_id': -1, 'confidence': 0.0}
    
    def get_class_distribution(self, obj_id) -> Dict:
        """
        Get distribution of classifications for an object (majority voting).
        
        Args:
            obj_id: Object ID from tracker
        
        Returns:
            Dict with vote counts: {'Auto': 5, 'Truck': 2, ...}
        """
        if obj_id not in self.classification_history:
            return {}
        
        votes = {}
        for entry in self.classification_history[obj_id]:
            class_id = entry['class_id']
            class_name = self.classifier.classes[class_id]
            votes[class_name] = votes.get(class_name, 0) + 1
        
        return votes
    
    def reset(self):
        """Reset tracking state."""
        self.tracked_classes.clear()
        self.classification_history.clear()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_sample_vehicle_image(vehicle_type='auto', size=(224, 224)):
    """
    Create a synthetic vehicle image for testing.
    
    Args:
        vehicle_type: 'auto', 'truck', 'bus', 'motorcycle'
        size: Output image size
    
    Returns:
        BGR image (numpy array)
    """
    image = np.ones((size[0], size[1], 3), dtype=np.uint8) * 200
    
    if vehicle_type == 'auto':
        # Draw simple car shape
        cv2.rectangle(image, (50, 100), (170, 150), (100, 100, 200), -1)  # body
        cv2.circle(image, (80, 160), 15, (50, 50, 50), -1)  # wheel
        cv2.circle(image, (140, 160), 15, (50, 50, 50), -1)  # wheel
    elif vehicle_type == 'truck':
        # Draw truck shape (larger, boxy)
        cv2.rectangle(image, (30, 80), (180, 160), (150, 100, 100), -1)  # body
        cv2.circle(image, (60, 170), 18, (40, 40, 40), -1)  # wheel
        cv2.circle(image, (140, 170), 18, (40, 40, 40), -1)  # wheel
        cv2.rectangle(image, (160, 100), (190, 140), (100, 80, 80), -1)  # cabin
    elif vehicle_type == 'bus':
        # Draw bus shape (tall, long)
        cv2.rectangle(image, (20, 70), (190, 160), (200, 150, 100), -1)  # body
        cv2.circle(image, (50, 170), 15, (30, 30, 30), -1)  # wheel
        cv2.circle(image, (170, 170), 15, (30, 30, 30), -1)  # wheel
        # Windows
        for x in [40, 80, 120, 160]:
            cv2.rectangle(image, (x, 85), (x+20, 105), (100, 180, 200), -1)
    elif vehicle_type == 'motorcycle':
        # Draw motorcycle shape (narrow, small)
        cv2.circle(image, (70, 140), 15, (50, 50, 50), -1)  # front wheel
        cv2.circle(image, (150, 140), 15, (50, 50, 50), -1)  # rear wheel
        cv2.rectangle(image, (100, 80), (130, 130), (100, 100, 150), -1)  # seat
        cv2.line(image, (115, 80), (80, 110), (100, 100, 150), 2)  # handlebar
    
    return image


if __name__ == '__main__':
    print("VehicleClassifier module loaded")
    
    # Test instantiation
    classifier = VehicleClassifier(device='cpu')
    print(f"✅ Classifier initialized with classes: {classifier.classes}")
    
    # Test classification
    sample_image = create_sample_vehicle_image('auto')
    class_name, confidence, class_id = classifier.classify(sample_image)
    print(f"✅ Sample classification: {class_name} ({confidence:.2%})")
    
    # Test with tracker integration
    classifier_tracker = VehicleClassifierWithTracking(classifier=classifier)
    print(f"✅ Classifier+Tracker initialized")
    
    print("\n✅ Vehicle classifier (Phase 3) ready for integration")
