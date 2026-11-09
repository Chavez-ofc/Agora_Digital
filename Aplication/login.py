from supabase import create_client, Client
import json
import flet as ft
url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"

sb: Client = create_client(url,key1)



async def main(page:ft.Page):

    page.views.clear()
    page.route = "/login"
    async def go_home(e):
            await page.push_route("/home")
    
    def route_change(e):
        if page.route == "/login":
            page.views.append(
                ft.View(
                    route="/login",
                    controls= [
                        ft.Text("Tela de login"),
                        ft.Button(
                            content="Ir para home", 
                            on_click= go_home                        
                        )
                    ]
                )
            )

        else:
            page.views.append(
                ft.View(
                    route = "/home",
                    controls = [ft.Text("home")]
                )
            )
            page.update()

    page.on_route_change = route_change
    route_change(None)


ft.run(main)
