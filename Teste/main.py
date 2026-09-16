from supabase import create_client, Client
import pandas as pd
from datetime import datetime as dt
import numpy as np

url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"


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
