from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

#start server
app = FastAPI()

#pydatic model
class Item(BaseModel):
    id: int
    nome: str
    cognome: str
    codice_fiscale: str

CSV_FILE_PATH = "data.csv"

#from file to dataframe
def read_csv():
    return pd.read_csv(CSV_FILE_PATH)

#from dataframe to csv
def write_csv(df):
    df.to_csv(CSV_FILE_PATH, index = False) #no indexes

#count elements endpoint
@app.get("/items/count")
def get_count():
    df = read_csv()
    return {f"count {len(df)}"}

#create new item endpoint
@app.post("/items/", status_code = 201) #create status code
def create_item(item: Item):
    df = read_csv()
    if item.id in df['id'].values:
        raise HTTPException(status_code=400, detail=f"id {item.id} already existing")
    new_record = pd.DataFrame([item.model_dump()]) #turn into 1 line string and create new record
    df = pd.concat([df, new_record])
    write_csv(df)
    return item

#get all records endpoint
@app.get("/items/")
def get_items():
    df = read_csv()
    return df.to_dict(orient="records") 

#get single entity endpoint
@app.get("/items/{id}")
def get_item(id: int):
    df = read_csv()
    record = df[df['id'] == id]
    if record.empty:
        raise HTTPException(status_code=404, detail=f"record {id} not found")
    return record.to_dict(orient="records")

#update existing record endpoint
@app.put("/items/{id}")
def update_item(id: str, item: Item):
    df = read_csv()
    if id not in df['id'].values:
        raise HTTPException(status_code=404, detail=f"record {id} not found")
    #df.loc -> [condition, colums to change]
    df.loc[df['id'] == id, ['nome', 'cognome', 'codice_fiscale']] = [item.nome, item.cognome, item.codice_fiscale]
    write_csv(df)
    return item

#delete record endpoint
@app.delete("/items/{id}")
def delete_item(id: str):
    df = read_csv()
    if id not in df['id'].values:
        raise HTTPException(status_code=404, detail=f"record {id} not found")
    df = df[df['id'] != id]
    write_csv(df)
    return {"message": "Item deleted successfully"}
