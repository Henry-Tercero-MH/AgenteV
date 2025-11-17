"""
Pure Python Vehicle Tracker using Centroid Tracking and IOU Matching
No external compilation dependencies - works with scipy only
Inspired by DeepSORT but simplified for vehicle tracking
"""

import numpy as np
from scipy.spatial.distance import cdist
from collections import defaultdict
import time


class VehicleTracker:
    """
    Centroid-based vehicle tracker with IOU (Intersection over Union) matching.
    Tracks vehicles across frames using:
    1. Centroid location
    2. Bounding box overlap (IOU)
    3. Temporal information
    """
    
    def __init__(self, max_disappeared=30, max_distance=50, iou_threshold=0.3):
        """
        Initialize tracker.
        
        Args:
            max_disappeared: Frames before object is forgotten
            max_distance: Max pixel distance for centroid matching
            iou_threshold: Min IOU for box matching (0-1)
        """
        self.next_object_id = 0
        self.objects = {}  # {object_id: {"centroid": (x,y), "bbox": (x1,y1,x2,y2), "frames": int}}
        self.disappeared = defaultdict(int)
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.iou_threshold = iou_threshold
        self.frame_count = 0
        self.track_history = defaultdict(list)  # Store detection history per object
        
    def _compute_iou(self, box1, box2):
        """
        Compute Intersection over Union between two boxes.
        Box format: (x1, y1, x2, y2)
        """
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Compute intersection
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        # Compute union
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        if union_area == 0:
            return 0.0
        
        return inter_area / union_area
    
    def _compute_centroid(self, bbox):
        """Compute centroid from bounding box."""
        x1, y1, x2, y2 = bbox
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        return (cx, cy)
    
    def _match_detections(self, detections):
        """
        Match current detections to tracked objects.
        Uses combination of centroid distance and IOU.
        
        Returns:
            matched_pairs: List of (object_id, detection_idx)
            unmatched_detections: Indices of detections without match
            unmatched_objects: IDs of objects without match
        """
        if len(self.objects) == 0:
            return [], list(range(len(detections))), []
        
        # Handle case with no detections
        if len(detections) == 0:
            return [], [], list(self.objects.keys())
        
        # Extract current object info
        obj_ids = list(self.objects.keys())
        obj_centroids = np.array([self.objects[oid]["centroid"] for oid in obj_ids])
        obj_boxes = [self.objects[oid]["bbox"] for oid in obj_ids]
        
        # Extract detection boxes and centroids
        det_centroids = np.array([self._compute_centroid(det["bbox"]) for det in detections])
        det_boxes = [det["bbox"] for det in detections]
        
        # Compute centroid distances
        centroid_dist = cdist(obj_centroids, det_centroids, metric='euclidean')
        
        # Compute IOU matrix
        iou_matrix = np.zeros((len(obj_ids), len(detections)))
        for i, obj_box in enumerate(obj_boxes):
            for j, det_box in enumerate(det_boxes):
                iou_matrix[i, j] = self._compute_iou(obj_box, det_box)
        
        # Combined distance: centroid distance + (1 - IOU) penalty
        # Lower is better
        combined_dist = centroid_dist.copy().astype(float)
        for i in range(len(obj_ids)):
            for j in range(len(detections)):
                if iou_matrix[i, j] < self.iou_threshold:
                    combined_dist[i, j] += 100  # Penalize low IOU matches
        
        # Match objects to detections using greedy approach
        matched_pairs = []
        unmatched_detections = set(range(len(detections)))
        unmatched_objects = set(obj_ids)
        
        # Sort matches by distance
        matches = []
        for i in range(len(obj_ids)):
            for j in range(len(detections)):
                if combined_dist[i, j] < self.max_distance:
                    matches.append((combined_dist[i, j], i, j))
        
        matches.sort()
        
        # Greedy assignment
        used_dets = set()
        used_objs = set()
        for dist, obj_idx, det_idx in matches:
            if obj_idx not in used_objs and det_idx not in used_dets:
                matched_pairs.append((obj_ids[obj_idx], det_idx))
                used_objs.add(obj_idx)
                used_dets.add(det_idx)
        
        unmatched_detections -= used_dets
        unmatched_objects -= set(o for o, _ in matched_pairs)
        
        return matched_pairs, list(unmatched_detections), list(unmatched_objects)
    
    def update(self, detections):
        """
        Update tracker with new detections.
        
        Args:
            detections: List of dicts with keys:
                - "bbox": (x1, y1, x2, y2)
                - "plate": plate text
                - "confidence": detection confidence
        
        Returns:
            List of dicts with tracked objects (includes object_id)
        """
        self.frame_count += 1
        
        # Match detections to objects
        matched, unmatched_dets, unmatched_objs = self._match_detections(detections)
        
        # Update matched objects
        for obj_id, det_idx in matched:
            det = detections[det_idx]
            self.objects[obj_id]["centroid"] = self._compute_centroid(det["bbox"])
            self.objects[obj_id]["bbox"] = det["bbox"]
            self.objects[obj_id]["frames"] += 1
            self.objects[obj_id]["plate"] = det.get("plate", "")
            self.objects[obj_id]["confidence"] = det.get("confidence", 0)
            self.disappeared[obj_id] = 0
            
            # Store in history
            self.track_history[obj_id].append({
                "frame": self.frame_count,
                "plate": det.get("plate", ""),
                "confidence": det.get("confidence", 0)
            })
        
        # Register new detections
        for det_idx in unmatched_dets:
            det = detections[det_idx]
            obj_id = self.next_object_id
            self.next_object_id += 1
            
            self.objects[obj_id] = {
                "centroid": self._compute_centroid(det["bbox"]),
                "bbox": det["bbox"],
                "frames": 1,
                "plate": det.get("plate", ""),
                "confidence": det.get("confidence", 0),
                "birth_frame": self.frame_count
            }
            self.track_history[obj_id].append({
                "frame": self.frame_count,
                "plate": det.get("plate", ""),
                "confidence": det.get("confidence", 0)
            })
        
        # Mark unmatched objects as disappeared
        for obj_id in unmatched_objs:
            self.disappeared[obj_id] += 1
        
        # Remove disappeared objects
        to_remove = [oid for oid in unmatched_objs if self.disappeared[oid] > self.max_disappeared]
        for obj_id in to_remove:
            del self.objects[obj_id]
            del self.disappeared[obj_id]
        
        # Return tracked objects
        return [
            {
                "object_id": obj_id,
                "bbox": obj_info["bbox"],
                "centroid": obj_info["centroid"],
                "plate": obj_info.get("plate", ""),
                "confidence": obj_info.get("confidence", 0),
                "frames_tracked": obj_info["frames"]
            }
            for obj_id, obj_info in self.objects.items()
        ]
    
    def get_best_plate_for_object(self, obj_id, min_frames=3):
        """
        Get the best (highest confidence) plate reading for a tracked object.
        Only returns if object has been tracked for minimum frames.
        
        Args:
            obj_id: Object ID to query
            min_frames: Minimum frames before returning result
        
        Returns:
            Plate text or None if criteria not met
        """
        if obj_id not in self.track_history:
            return None
        
        if obj_id not in self.objects:
            return None
        
        # Only return if tracked for enough frames
        if self.objects[obj_id]["frames"] < min_frames:
            return None
        
        # Get best plate from history
        history = self.track_history[obj_id]
        valid_readings = [h for h in history if h["plate"] and h["plate"].strip()]
        
        if not valid_readings:
            return None
        
        # Return highest confidence reading
        best = max(valid_readings, key=lambda x: x["confidence"])
        return best["plate"]
    
    def reset(self):
        """Reset tracker state."""
        self.objects.clear()
        self.disappeared.clear()
        self.track_history.clear()
        self.next_object_id = 0
        self.frame_count = 0
