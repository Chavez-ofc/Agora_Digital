from dotenv import load_dotenv
import os
from supabase import create_client, Client
import pandas as pd
from datetime import datetime as dt
import numpy as np

load_dotenv()
url = os.getenv("URL")
key = os.getenv("KEY")
#ainda preciso transformar as variáveis acima em variáveis ambientes


supabase: Client = create_client(url,key)

def send(text:str):
    
    if not text or not text.strip():
        print("burro")
        return

    try:
        
        response = supabase.table("str_bank",).insert({"string": text},returning = "minimal")
        #a propriedade returning = "minimal" evita que o python tente ler a linha inserida
    
        response.execute()
        return response

    except Exception as e:
        print(f"deu pobrema: {e}")

if __name__ == "__main__":

    user_str = input("fala ae: ")
    send(user_str)

#s = supabase.table("str_bank").select("string",count = "exact").execute() 
#print(s)