from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from datetime import datetime as dt
import json


url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"

sb: Client = create_client(url,key1)

class features:
    def __init__(self,client: Client, AI = SentenceTransformer,J = json, critic:str="", sugg:str=""):
        self.sb = client
        self.ai = AI
        self.critic = critic
        self.sugg = sugg
        self.json = J

    def send_critic(self):
        """**Permite o envio de uma string a ser armazenada na coluna 'critics' da tabela c_bank na plataforma Supabase**
        """
        if not self.critic or not self.critic.strip():
            print("Formato não aceito")
            return

        try:
            model = self.ai("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            embed = model.encode(self.critic, normalize_embeddings=True)
            embed = embed.tolist()
                        
            response = self.sb.table("c_bank",).insert({"Critics": self.critic,"c_vectors":embed}, returning = "minimal")
            response.execute()
            return response
        

        except Exception as e:
            print(e)

    def send_suggestion(self):
        """**Permite o envio de uma string a ser armazenada na coluna 'suggestions' da tabela s_bank na plataforma Supabase**
        """
        
        if not self.sugg or not self.sugg.strip():
            print("Formato não aceito")
            return

        try:
            model = self.ai("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            embed = model.encode(self.sugg, normalize_embeddings=True)
            embed = embed.tolist()
                
            response = self.sb.table("s_bank",).insert({"Suggestions": self.sugg,"s_vectors":embed}, returning = "minimal")
            response.execute()
            return response

        except Exception as e:
            print(e)

    def c_summary(self):
        """**Solicita o resumo das informações da coluna 'Critics', da tabela c_bank, mediante à
        quantidade de strings armazenadas e ainda não resumidas**
        """
        falses = self.sb.table("c_bank").select("read", count="exact").eq("read",False).execute()

        if falses.count >=4:
            res = self.sb.table("c_bank").select("ID, Critics, c_vectors").eq("read",False).execute() 
            registros = res.data


            textos_para_resumo = []
            for reg in registros:
                c_similares_res = self.sb.rpc("c_similares", {"target_id": reg["ID"], "similarity_threshold": 0.7}).execute()
                
                textos_grupo = [reg["Critics"]] + [s["conteudo"] for s in c_similares_res.data]
                textos_para_resumo.extend(textos_grupo)

                textos_unicos = list(dict.fromkeys(textos_para_resumo))

            ids_read= [r["ID"] for r in registros]
            self.sb.table("c_bank").update({"read": True}).in_("ID", ids_read).execute()
            textos_unicos = str(textos_unicos)
            summ = self.sb.functions.invoke("hyper-endpoint", invoke_options={"body": {"texto": textos_unicos}})

            texto_json = summ.decode('utf-8')
            dados = self.json.loads(texto_json)
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
            return sent, resumo_formatado

        else:
            pass


    def s_summary(self):
        """**Solicita o resumo das informações da coluna 'Suggestion', da tabela s_bank, mediante à
            quantidade de strings armazenadas e ainda não resumidas. Informações armazenadas na tabela 's_summary'**
        """
        falses = self.sb.table("s_bank").select("read", count="exact").eq("read",False).execute()

        if falses.count >=4:
            res = self.sb.table("s_bank").select("ID, Suggestions, s_vectors").eq("read",False).execute() 
            registros = res.data


            textos_para_resumo = []
            for reg in registros:
                s_similares_res = self.sb.rpc("s_similares", {"target_id": reg["ID"], "similarity_threshold": 0.7}).execute()
                
                textos_grupo = [reg["Suggestions"]] + [s["conteudo"] for s in s_similares_res.data]
                textos_para_resumo.extend(textos_grupo)

                textos_unicos = list(dict.fromkeys(textos_para_resumo))

            ids_read= [r["ID"] for r in registros]
            self.sb.table("s_bank").update({"read": True}).in_("ID", ids_read).execute()
            textos_unicos = str(textos_unicos)
            summ = self.sb.functions.invoke("hyper-endpoint", invoke_options={"body": {"texto": textos_unicos}})

            texto_json = summ.decode('utf-8')
            dados = self.json.loads(texto_json)
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

            resumo_linha = [{"Suggestions": frase} for frase in resumo_pack]
            sent = sb.table("s_summary").insert(resumo_linha).execute()
            return sent, resumo_formatado

        else:
            pass


#Teste
#app = features(client = sb, AI = SentenceTransformer, J = json, sugg ="teste")
#app = features(client = sb)
#app.c_summary()