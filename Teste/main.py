from supabase import create_client, Client
import pandas as pd
from datetime import datetime as dt
import numpy as np


url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"
sb: Client = create_client(url,key)
class features:
    def __init__(self,client: Client, critic:str="", sugg:str=""):
        self.sb = client
        self.critic = critic
        self.sugg = sugg

    def send_critic(self):
        """Enables to send a string that will be saved in the column 'Critics' from str_bank project at Supabase
            \nARG: str -> "Text to be sent"

        """
        if not self.critic or not self.critic.strip():
            print("Formato não aceito")
            return

        try:
            response = self.sb.table("str_bank",).insert({"Critics": self.critic}, returning = "minimal")
            #a propriedade returning = "minimal" evita que o python tente ler a linha inserida
        
            response.execute()
            return response

        except Exception as e:
            print(e)

    def send_suggestion(self):

        if not self.sugg or not self.sugg.strip():
            print("Formato não aceito")
            return

        try:
             response = self.sb.table("str_bank",).insert({"Suggestions": self.sugg}, returning = "minimal")
             response.execute()
             return response

        except Exception as e:
            print(e)

app = features(client = sb, critic ="teste1")
app.send_critic()

"""
    def func_buttons(self):
        s = supabase.table("str_bank").select("string",count = "exact").execute() 
        """

