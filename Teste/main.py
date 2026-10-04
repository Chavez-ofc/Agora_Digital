from sentence_transformers import SentenceTransformer
from supabase import create_client, Client

from datetime import datetime as dt



url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"

sb: Client = create_client(url,key1)

class features:
    def __init__(self,client: Client, AI, critic:str="", sugg:str=""):
        self.sb = client
        self.ai = AI
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
            model = self.ai("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            embed = model.encode(self.critic, normalize_embeddings=True)
            embed = embed.tolist()
            vec = self.sb.table("Vectors").insert({"C_Vectors": embed},returning = "minimal")
        
            vec.execute()
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
            model = self.ai("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            embed = model.encode(self.sugg, normalize_embeddings=True)
            embed = embed.tolist()
            vec = self.sb.table("Vectors").insert({"S_Vectors": embed},returning = "minimal")
            vec.execute()
            return response

        except Exception as e:
            print(e)

#Teste
app = features(client = sb, AI = SentenceTransformer, critic ="teste um",sugg="teste um")
app.send_critic()
app.send_suggestion()