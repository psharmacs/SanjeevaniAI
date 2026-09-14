import cv2

def draw_bbox(frame, bbox, object_id, fall_status, color=(0,255,0)):
    x1, y1, x2, y2 = bbox
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    label = f"ID:{object_id} {'FALL' if fall_status else ''}"
    cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
