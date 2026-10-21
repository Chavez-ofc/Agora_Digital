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


res = sb.table("str_bank").select("ID, Critics, c_vectors").execute()
    
registros = res.data

textos_para_resumo = []
for reg in registros:
    similares_res = sb.rpc("similares", {"target_id": reg["ID"], "match_count": 5, "similarity_threshold": 0.7}).execute()
    
    textos_grupo = [reg["Critics"]] + [s["conteudo"] for s in similares_res.data]
    textos_para_resumo.extend(textos_grupo)

    textos_unicos = list(dict.fromkeys(textos_para_resumo))
textos_unicos = str(textos_unicos)

summ = sb.functions.invoke("hyper-endpoint", invoke_options={"body": {"texto": textos_unicos}})


resposta_bytes = summ
texto_json = resposta_bytes.decode('utf-8')
dados = json.loads(texto_json)
resumo_formatado = dados.get("resumo")


print(resumo_formatado)




"""
response = sb.table("str_bank").select("c_vectors", count = False).limit(1).execute()
response = response.data[0]
response = response[0]["c_vectors"]
model.encode()
"""



