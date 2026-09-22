import json

def lookupGlos(glos):
    #we open /web/glosses_transformed.json
    with open("/web/glosses_transformed.json", "r") as file:
        data = json.load(file)

    for obj in data:
    # Get the keys of the object (e.g., "3808", "3809", etc.)
        keys = obj.keys()
        if len(keys) > 0:
            key = list(keys)[0]
            # Extract the desired fields from the object
            signbank_id = key
            annotation_id = obj[key].get("Annotation ID Gloss: Dutch")
            if annotation_id == glos:
                #we return glos id
                return signbank_id
    
    
def process_morphology(morphology):
    #we get morphology in this form:             "Sequential Morphology": "VRAGEN-A + SCHRIJVEN-B", they are going
    #to be transformed to this form:             [{"glos": "VRAGEN-A", "id": to be found}, {"glos": "SCHRIJVEN-B""id": to be found}]
    
    #we split the morphology by + sign
    morphologies = morphology.split(" + ")
    #we create a list where we are going to store the morphologies
    morphologies_list = []
    #we loop through the morphologies
    for morph in morphologies:
        #we create a dictionary with glos and id
        lala = lookupGlos(morph)
        morph_dict = {"glos": morph, "id": lala}
        #we append the dictionary to the list
        morphologies_list.append(morph_dict)
        
        
    return morphologies_list
        
        
        
print(process_morphology("VRAGEN-A + SCHRIJVEN-B"))