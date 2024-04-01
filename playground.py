import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

image_path = 'Photos-001/IMG_7325.PNG'
image = cv2.imread(image_path)

image = cv2.resize(image, (350, 600))

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

pose_results = pose.process(image_rgb)

# Print all the mapped points
for idx, landmark in enumerate(pose_results.pose_landmarks.landmark):
    height, width, _ = image.shape
    cx, cy = int(landmark.x * width), int(landmark.y * height)
    print(f"Landmark {idx}: ({cx}, {cy})")

mp_drawing.draw_landmarks(image, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

cv2.imshow('Output', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
