from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import tensorflow as tf
import numpy as np
import cv2
import pickle
import requests
import json
import base64
import math

def euclidean_distance(vec1, vec2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

def get_plant_stress_condition(species: str, features: list, species_vectors: dict) -> str:
    if species not in species_vectors:
        return "Species not recognized"
    
    rep_vectors = species_vectors[species]
    best_condition = None
    best_distance = float('inf')
    
    for condition, rep_vector in rep_vectors.items():
        dist = euclidean_distance(features, rep_vector)
        # Debug: print(f"Distance to {condition}: {dist}")
        if dist < best_distance:
            best_distance = dist
            best_condition = condition
    return best_condition

def plant_status(species_input,features):
    species_list = [
        "African Violet (Saintpaulia ionantha)",
        "Aloe Vera",
        "Anthurium (Anthurium andraeanum)",
        "Areca Palm (Dypsis lutescens)",
        "Asparagus Fern (Asparagus setaceus)",
        "Begonia (Begonia spp.)",
        "Bird of Paradise (Strelitzia reginae)",
        "Birds Nest Fern (Asplenium nidus)",
        "Boston Fern (Nephrolepis exaltata)",
        "Calathea",
        "Cast Iron Plant (Aspidistra elatior)",
        "Chinese Money Plant (Pilea peperomioides)",
        "Chinese Evergreen (Aglaonema)",
        "Christmas Cactus (Schlumbergera bridgesii)",
        "Chrysanthemum",
        "Ctenanthe",
        "Daffodils (Narcissus spp.)",
        "Dracaena",
        "Dumb Cane (Dieffenbachia spp.)",
        "Elephant Ear (Alocasia spp.)",
        "English Ivy (Hedera helix)",
        "Hyacinth (Hyacinthus orientalis)",
        "Iron Cross Begonia (Begonia masoniana)",
        "Jade Plant (Crassula ovata)",
        "Kalanchoe",
        "Lilium (Hemerocallis)",
        "Lily of the Valley (Convallaria majalis)",
        "Money Tree (Pachira aquatica)",
        "Monstera Deliciosa (Monstera deliciosa)",
        "Orchid",
        "Parlor Palm (Chamaedorea elegans)",
        "Peace Lily",
        "Poinsettia (Euphorbia pulcherrima)",
        "Polka Dot Plant (Hypoestes phyllostachya)",
        "Ponytail Palm (Beaucarnea recurvata)",
        "Pothos (Ivy Arum)",
        "Prayer Plant (Maranta leuconeura)",
        "Rattlesnake Plant (Calathea lancifolia)",
        "Rubber Plant (Ficus elastica)",
        "Sago Palm (Cycas revoluta)",
        "Schefflera",
        "Snake Plant (Sansevieria)",
        "Tradescantia",
        "Tulip",
        "Venus Flytrap",
        "Yucca",
        "ZZ Plant (Zamioculcas zamiifolia)"
    ]
    
    # ------------------------------------------------------------------
    # Group species based on their characteristics.
    # (Adjust these lists as needed for your particular classification.)
    ferns = [
        "Asparagus Fern (Asparagus setaceus)",
        "Birds Nest Fern (Asplenium nidus)",
        "Boston Fern (Nephrolepis exaltata)"
    ]
    
    succulents = [
        "Aloe Vera",
        "Christmas Cactus (Schlumbergera bridgesii)",
        "Jade Plant (Crassula ovata)",
        "Kalanchoe",
        "Snake Plant (Sansevieria)",
        "ZZ Plant (Zamioculcas zamiifolia)"
    ]
    
    palms = [
        "Areca Palm (Dypsis lutescens)",
        "Parlor Palm (Chamaedorea elegans)",
        "Ponytail Palm (Beaucarnea recurvata)",
        "Sago Palm (Cycas revoluta)"
    ]
    
    # All species not in the above groups will be assigned to "ornamental" or general houseplants.
    ornamental = [sp for sp in species_list if sp not in ferns + succulents + palms]
    
    # ------------------------------------------------------------------
    # Ornamental (general houseplants)
    ornamental_healthy   = [36.66, 22.80, 20.15, 42.96, 872.32]
    ornamental_high      = [19.16, 22.81, 20.03, 61.28, 268.73]
    ornamental_moderate  = [24.68, 19.16, 17.51, 63.83, 760.43]
    
    # Ferns – typically more delicate, so you might have slightly lower values, etc.
    ferns_healthy   = [35.00, 23.00, 19.50, 45.00, 800.00]
    ferns_high      = [18.00, 22.00, 18.00, 60.00, 250.00]
    ferns_moderate  = [25.00, 20.00, 17.00, 65.00, 700.00]
    
    # Succulents/Cacti – they often have higher Feature1 (e.g., water retention) and other differences.
    succulents_healthy   = [40.00, 25.00, 21.00, 40.00, 900.00]
    succulents_high      = [22.00, 21.00, 19.00, 55.00, 300.00]
    succulents_moderate  = [28.00, 20.00, 18.00, 60.00, 800.00]
    
    # Palms – may have their own distinctive values.
    palms_healthy   = [38.00, 24.00, 20.00, 43.00, 850.00]
    palms_high      = [20.00, 23.00, 19.00, 62.00, 280.00]
    palms_moderate  = [26.00, 21.00, 18.00, 64.00, 780.00]  
    # ------------------------------------------------------------------
    species_vectors = {}
    
    for sp in species_list:
        if sp in ferns:
            species_vectors[sp] = {
                "Healthy": ferns_healthy,
                "High Stress": ferns_high,
                "Moderate Stress": ferns_moderate
            }
        elif sp in succulents:
            species_vectors[sp] = {
                "Healthy": succulents_healthy,
                "High Stress": succulents_high,
                "Moderate Stress": succulents_moderate
            }
        elif sp in palms:
            species_vectors[sp] = {
                "Healthy": palms_healthy,
                "High Stress": palms_high,
                "Moderate Stress": palms_moderate
            }
        elif sp in ornamental:
            species_vectors[sp] = {
                "Healthy": ornamental_healthy,
                "High Stress": ornamental_high,
                "Moderate Stress": ornamental_moderate
            }
        else:
            # In case a species doesn't match any group (shouldn't happen)
            species_vectors[sp] = {
                "Healthy": ornamental_healthy,
                "High Stress": ornamental_high,
                "Moderate Stress": ornamental_moderate
            }
    

    condition = get_plant_stress_condition(species_input, features, species_vectors)
    return condition




IMG_SIZE = 128

# Model load ---------
model_img = tf.keras.models.load_model("base_model.keras")
with open("image_classifier.pkl", "rb") as f:
    label_encoder_img = pickle.load(f)

# -------

model_hlt = tf.keras.models.load_model("plant_health_model.keras")
with open("planthealth.pkl", "rb") as f:
    label_encoder_hlt = pickle.load(f)
with open("scaler.pkl", "rb") as f:
    scaler_hlt = pickle.load(f)

# --------------------



def preprocess_base64_image(base64_str):
    image_bytes = base64.b64decode(base64_str)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    img = img / 255.0  
    return img
def predict_base64_image(base64_str):
    img = preprocess_base64_image(base64_str)
    img = np.expand_dims(img, axis=0)  
    pred = model_img.predict(img)
    pred_label = np.argmax(pred, axis=1)[0]
    class_name = label_encoder_img.inverse_transform([pred_label])[0]
    return class_name

def predict_health(soil_moisture, ambient_temp, soil_temp, humidity, light_intensity):
    input_data = np.array([[soil_moisture, ambient_temp, soil_temp, humidity, light_intensity]])
    input_data = scaler_hlt.transform(input_data) 
    prediction = model_hlt.predict(input_data)
    predicted_class = np.argmax(prediction, axis=1)[0]
    return label_encoder_hlt.inverse_transform([predicted_class])[0]


app = FastAPI()



@app.get("/")
async def read_root():
    return {"Master": "Start the image classification backend","Assistant":"yes senpai I am going to start"}

@app.post("/image-classify/")
async def image_classify(
        request: Request
    ):
    raw_body = await request.body()
    decoded_body = raw_body.decode("utf-8", errors="replace")
    image_base64 = json.loads(decoded_body).get("image")
    prediction = predict_base64_image(image_base64)
    output = {"name": prediction}
    print(output)
    return output

@app.post("/health-detect/")
async def health_detect(
        request: Request
    ):
    raw_body = await request.body()
    decoded_body = raw_body.decode("utf-8", errors="replace")
    data = json.loads(decoded_body)
    species = int(data.get("Species"))
    soil_moisture = int(data.get("Soil_Moisture"))
    ambient_temp = int(data.get("Ambient_Temperature"))
    humidity = int(data.get("Humidity"))
    light_intensity = int(data.get("Light_Intensity"))

    predicted_status = plant_status(species,[soil_moisture, ambient_temp, humidity, light_intensity])
    return {"Predicted_Health_Status": predicted_status}