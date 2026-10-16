from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
import main as m

url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"

sb: Client = create_client(url,key1)

msg = "preciso testar se meu código envia vetores a um banco de dados e resume meus envios com IA"
t = m.features(AI = SentenceTransformer, critic= msg, Client = sb)
t.send_critic()
