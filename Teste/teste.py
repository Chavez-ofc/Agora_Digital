import json
from supabase import create_client, Client 


url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"
sb: Client = create_client(url,key1)



def summary():
    falses = sb.table("c_bank").select("read", count="exact").eq("read",False).execute()

    if falses.count >=4:
        res = sb.table("c_bank").select("ID, Critics, c_vectors").eq("read",False).execute() 
        registros = res.data


        textos_para_resumo = []
        for reg in registros:
            c_similares_res = sb.rpc("c_similares", {"target_id": reg["ID"], "similarity_threshold": 0.7}).execute()
            
            textos_grupo = [reg["Critics"]] + [s["conteudo"] for s in c_similares_res.data]
            textos_para_resumo.extend(textos_grupo)

            textos_unicos = list(dict.fromkeys(textos_para_resumo))

        ids_read= [r["ID"] for r in registros]
        sb.table("c_bank").update({"read": True}).in_("ID", ids_read).execute()
        textos_unicos = str(textos_unicos)
        summ = sb.functions.invoke("hyper-endpoint", invoke_options={"body": {"texto": textos_unicos}})

        texto_json = summ.decode('utf-8')
        dados = json.loads(texto_json)
        resumo_formatado = dados.get("resumo")

        resumo_pack = [""]
        i = 0
        for k in resumo_formatado:
            if k != "§":
                resumo_pack[i] += k
            else:
                i+=1
                resumo_pack += [""]

        del resumo_pack[-1]

    resumo_linha = [{"Critics": frase} for frase in resumo_pack]
    sent = sb.table("c_summary").insert(resumo_linha).execute()
    return sent, resumo_formatado, resumo_linha

sent, res_form, res_linha = summary()

print(res_linha)
print("")
print(res_form)