import json
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client 
import main as m

url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"
sb: Client = create_client(url,key1)
#model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


#msg = "teste do meu código para enviar vetores a um banco de dados e resumí-los com IA"
#t = m.features(AI = SentenceTransformer, critic= msg, client = sb)
#t.send_critic()


res = sb.table("c_bank").update({"read":False}).eq("read",True).execute()
    
