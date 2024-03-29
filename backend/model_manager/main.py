import os
import torch
import json 
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

labels_filepath = f"label_mapping.json"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    # Initialize model, tokenizer and labels
    with open(labels_filepath, 'r') as labels:
        label_mapping = json.load(labels)  

    model = AutoModelForSequenceClassification.from_pretrained("beny2000/store_type_classifyer")
    tokenizer = AutoTokenizer.from_pretrained("beny2000/store_type_classifyer")
    model.eval()
    logging.info(f"Model initialized")
except Exception as ex:
    logging.error(f"Error: Failed to initialize model, tokenizer and labels. {ex}")
    raise ex



@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url='/docs')
    
@app.get("/api/tag_item")
async def get_list(item: str):
    """
    Tag item using a pre-trained model.

    Parameters:
    - **item** (str): The item to be tagged.

    Returns:
    - **str**: The predicted tag for the item.
    """
    try:
        inputs = tokenizer(item, return_tensors="pt")

        # Forward pass through the model
        outputs = model(**inputs)

        # Get the predicted label
        predicted_label = torch.argmax(outputs.logits, dim=1).item()
        predicted_tag = label_mapping[str(predicted_label)]

        print(f"Top labels: {[label_mapping[str(i)] for i in torch.topk(outputs.logits, k=3, dim=1)[1].squeeze().tolist()]}")
        
        return predicted_tag
    except Exception as e:
        logging.error(f"Error: Failed to tag item. {e}")
        raise HTTPException(status_code=500, detail="Server error") from e
    
