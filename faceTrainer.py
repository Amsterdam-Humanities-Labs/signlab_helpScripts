import os
import json
import pandas as pd
from deepface import DeepFace
import shutil
import numpy as np
from deepface.basemodels import Facenet
from sklearn.neighbors import KDTree
import joblib

# Paths
uploads_path = "/web/uploads"
db_path = "/web/faceDb"

# Initialize FaceNet model
model = Facenet.loadModel()

# Function to compute embedding
def compute_embedding(img_path):
    img = DeepFace.detectFace(img_path, detector_backend='mtcnn')
    embedding = model.predict(img)[0]
    return embedding

# Function to save face image to the database
def save_face(img_path, person_name):
    person_dir = os.path.join(db_path, person_name)
    os.makedirs(person_dir, exist_ok=True)
    img_name = os.path.basename(img_path)
    target_path = os.path.join(person_dir, img_name)
    shutil.copy(img_path, target_path)
    print(f"Saved {img_path} as {target_path}")

# Precompute and store embeddings for the face database
def precompute_embeddings():
    embeddings = []
    labels = []
    for person_name in os.listdir(db_path):
        person_dir = os.path.join(db_path, person_name)
        for img_file in os.listdir(person_dir):
            img_path = os.path.join(person_dir, img_file)
            embedding = compute_embedding(img_path)
            embeddings.append(embedding)
            labels.append(person_name)
    return np.array(embeddings), np.array(labels)

# Load JSON data
with open('refilmChecker.json', 'r') as file:
    faces_data = json.load(file)

# Limit faces_data to 50 items
faces_data = dict(list(faces_data.items())[:50])

# Precompute embeddings and build KD-tree
embeddings, labels = precompute_embeddings()
kdtree = KDTree(embeddings, leaf_size=30, metric='euclidean')
joblib.dump((kdtree, labels), 'face_kdtree.joblib')

# Function to find the nearest neighbor using KD-tree
def find_nearest_face(img_path):
    embedding = compute_embedding(img_path).reshape(1, -1)
    dist, ind = kdtree.query(embedding, k=1)
    return labels[ind[0][0]], dist[0][0]

# Loop through JSON data and compare faces
for img_file, details in faces_data.items():
    img_path = os.path.join(uploads_path, img_file)
    try:
        person_name, distance = find_nearest_face(img_path)
        if distance < 0.2:
            # Check if img_file is already in /web/faceDb/person_name
            person_dir = os.path.join(db_path, person_name)
            if os.path.exists(person_dir):
                person_files = os.listdir(person_dir)
                if img_file not in person_files:
                    save_face(img_path, person_name)
            details['label'] = person_name
        else:
            details['label'] = "unknown"
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
        details['label'] = "unknown"

# Save the updated JSON data
with open('faces_updated.json', 'w') as file:
    json.dump(faces_data, file, indent=4)

print("JSON file updated and saved as faces_updated.json")
