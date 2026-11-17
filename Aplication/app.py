import asyncio as asy
from datetime import datetime
import flet as ft
from supabase import create_client, Client
import json
import main as m


url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"

sb: Client = create_client(url, key1)


async def main(page: ft.Page):

    page.title = "Ágora Digital"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#FFFFFF"
    #page.scroll = ft.ScrollMode.ADAPTIVE

    page.views.clear()
    page.route = "/login"


    criticas_lista = ft.Column(spacing=0)
    resumo_criticas = ft.Column(
        controls=[
            ft.Text("Resumo das críticas", weight=ft.FontWeight.BOLD),
            criticas_lista,
        ],
    )

    # Resumo das sugestões: também é uma Column (sem divisórias de tabela)
    sugestoes_lista = ft.Column(spacing=0)

    resumo_sugestoes = ft.Column(
        controls=[
            ft.Text("Resumo das sugestões", weight=ft.FontWeight.BOLD),
            sugestoes_lista,
        ]
    )
    # envios de críticas
    data_table2 = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Envios"))],
        rows=[],
        data_row_max_height=float("inf"),
        border=ft.Border.all(1, ft.Colors.GREY_500),
        border_radius=ft.BorderRadius.all(5)
    )
    # envios de sugestões
    data_table3 = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Envios"))],
        rows=[],
        data_row_max_height=float("inf"),
        border=ft.Border.all(1, ft.Colors.GREY_500),
        border_radius=ft.BorderRadius.all(5)
    )

    def load_data_1(e=None):

        criticas_lista.controls.clear()
        sugestoes_lista.controls.clear()
        page.update()
        try:
            res = sb.table("c_summary").select("Critics").gte(column="id", value=0).execute()
            res = res.data
            res1 = sb.table("s_summary").select("Suggestions").gte(column="id", value=0).execute()
            res1 = res1.data

            for item in res:
                criticas_lista.controls.append(
                    ft.Container(
                        content=ft.Text(str(item.get("Critics"))),
                        padding=5,
                        margin=5,
                        width=500,
                        border=ft.Border.all(1, color=ft.Colors.GREY_300),
                        border_radius=ft.BorderRadius.all(5)
                    )
                )
            for item in res1:
                sugestoes_lista.controls.append(
                    ft.Container(
                        content=ft.Text(str(item.get("Suggestions"))),
                        padding=5,
                        margin=5,
                        width=500,
                        border=ft.Border.all(1, color=ft.Colors.GREY_300),
                        border_radius=ft.BorderRadius.all(5)
                    )
                )

        except Exception as ex:
            print("Erro:", ex)

        page.update()

    def load_data_sent(e=None):

        data_table2.rows.clear()
        data_table3.rows.clear()
        page.update()
        try:
            res2 = sb.table("c_bank").select("Critics").gte(column="ID", value=0).execute()
            res2 = res2.data
            res3 = sb.table("s_bank").select("Suggestions").gte(column="ID", value=0).execute()
            res3 = res3.data

            for item in res2:
                data_table2.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Container(margin=5, content=ft.Text(str(item.get("Critics")))))
                        ]
                    )
                )
            for item in res3:
                data_table3.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Container(margin=5, content=ft.Text(str(item.get("Suggestions")))))
                        ]
                    )
                )

        except Exception as ex:
            print("Erro:", ex)

        page.update()

    load_data_1()
    load_data_sent()

    async def update_table1(e=None):
        while True:
            load_data_1()

            await asy.sleep(300)

    async def update_table2(e=None):
        while True:
            load_data_sent()

            await asy.sleep(120)

    page.run_task(update_table1)
    page.run_task(update_table2)

    def c_mensagem(e):
        print(c_field.value)
        t = c_field.value
        c_field.value = ""
        app = m.features(client=sb, critic=t)
        app.send_critic()
        app.c_summary()

    def s_mensagem(e):
        print(s_field.value)
        t = s_field.value
        s_field.value = ""
        app = m.features(client=sb, sugg=t)
        app.send_suggestion()
        app.s_summary()

    def c_click(e):
        c_mensagem(e)
        load_data_1(e)
        load_data_sent(e)

    def s_click(e):
        s_mensagem(e)
        load_data_1(e)
        load_data_sent(e)


    logo = ft.Image(src="Images/Logotipo1.png", width=250, fit=ft.BoxFit.COVER, align=ft.Alignment.TOP_CENTER)

    critics = ft.Text("Críticas", weight=ft.FontWeight.BOLD)
    c_field = ft.TextField(label="Escreva suas críticas", multiline=True, text_align="LEFT", max_length=300)
    c_send = ft.Button(content="Enviar", on_click=c_click)

    suggestions = ft.Text("Sugestões", weight=ft.FontWeight.BOLD)
    s_field = ft.TextField(label="Escreva suas sugestões", multiline=True, text_align="LEFT", max_length=300)
    s_send = ft.Button(content="Enviar", on_click=s_click)

    tab_1 = ft.Tab(label="Agora")
    tab_2 = ft.Tab(label="Críticas")
    tab_3 = ft.Tab(label="Sugestões")

    tabbar = ft.TabBar(tabs=[tab_1, tab_2, tab_3], tab_alignment=ft.TabAlignment.CENTER)
    inside_tabs = ft.TabBarView(
        width=600,
        expand=True,
        align=ft.Alignment.TOP_CENTER,
        controls=[
            ft.Container(
                align=ft.Alignment.TOP_CENTER,
                content=ft.Column(width=600, controls=[resumo_criticas, resumo_sugestoes], scroll=ft.ScrollMode.ADAPTIVE),
            ),
            ft.Container(
                align=ft.Alignment.TOP_CENTER,
                content=ft.Column(width=600, controls=[critics, c_field, c_send, data_table2], scroll=ft.ScrollMode.ADAPTIVE),
            ),
            ft.Container(
                align=ft.Alignment.TOP_CENTER,
                content=ft.Column(width=600, controls=[suggestions, s_field, s_send, data_table3], scroll=ft.ScrollMode.ADAPTIVE),
            ),
        ],
    )

    tabs = ft.Tabs(length=3, expand=True, content=ft.Column(expand=True, controls=[tabbar, inside_tabs]))


    async def go_home(e):
        await page.push_route("/home")

    async def go_registry(e):
        await page.push_route("/registry")

    async def go_login(e):
        await page.push_route("/login")


    def route_change(e):

        
        page.views.clear()

        login_google = ft.Button(
            content=ft.Text(
                value="          Entrar com Google",
                align=ft.Alignment.CENTER_LEFT),
            width=300,
            height=60,
            align=ft.Alignment.TOP_CENTER,
            icon=ft.Image(src="Images/Google_Symbol_1.png", align=ft.Alignment.CENTER_LEFT, width=35, height=35))

        login_email = ft.TextField(label="Email", align=ft.Alignment.TOP_CENTER)
        login_pswd = ft.TextField(label="Senha", password=True, can_reveal_password=True, align=ft.Alignment.TOP_CENTER)


        reg_user = ft.TextField(label = "Nome de usuário", align=ft.Alignment.TOP_CENTER)
        reg_email = ft.TextField(label="Email", align=ft.Alignment.TOP_CENTER)
        reg_pswd1 = ft.TextField(label="Senha", password=True, align=ft.Alignment.TOP_CENTER)
        reg_pswd2 = ft.TextField(label="Confirme a senha", password=True, align=ft.Alignment.TOP_CENTER)

        

        async def do_login(e):
            try:
                # chamada bloqueante do Supabase fora do loop do Flet
                resposta = await asy.to_thread(
                    sb.auth.sign_in_with_password,
                    {"email": login_email.value, "password": login_pswd.value},
                )
                login_user = resposta.user.user_metadata.get("display_name")
                print(f"Login bem-sucedido. Bem-vindo, {login_user}!")
                await page.push_route("/home")
                return login_user
            
            except Exception as ex:
                print(f"Erro ao fazer login: {ex}")
        

        async def do_register(e):
            if reg_pswd1.value != reg_pswd2.value:
                print("As duas senhas devem ser iguais.")
                return
            try:
                resposta = await asy.to_thread(
                    sb.auth.sign_up,
                    {"email": reg_email.value,
                     "password": reg_pswd1.value,
                     "options" :{
                         "data":{
                             "display_name":reg_user.value
                         }
                     }

                     }
                )
                print(f"Cadastro realizado com sucesso! ID do Usuário: {resposta.user.user_metadata}")
                await page.push_route("/login")
            except Exception as ex:
                print(f"Erro ao cadastrar: {ex}")


        if page.route == "/login":
            page.views.append(
                ft.View(
                    route="/login",
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            controls=[
                                logo,
                                ft.Container(
                                    content=ft.Text("Bem Vindo!", weight=ft.FontWeight.BOLD, align=ft.Alignment.TOP_CENTER),
                                    padding=25
                                ),
                                login_google,

                                ft.Container(
                                    content=ft.Text("ou", align=ft.Alignment.TOP_CENTER),
                                    padding=15
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("Login com email:", align=ft.Alignment.BOTTOM_LEFT),
                                            login_email,
                                            login_pswd,
                                        ],
                                    ),
                                    align=ft.Alignment.CENTER,
                                    width=300
                                ),
                                ft.Row(
                                    controls=[
                                        ft.Button(content="Entrar", on_click=do_login),
                                        ft.Button(content="Registrar-se", on_click=go_registry)
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                )
                            ],
                            align=ft.Alignment.TOP_CENTER
                        )
                    ]
                )
            )

        elif page.route == "/registry":
            page.views.append(
                ft.View(
                    route="/registry",
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            controls=[
                                logo,
                                ft.Container(
                                    content=ft.Text("Cadastro", weight=ft.FontWeight.BOLD, align=ft.Alignment.TOP_CENTER),
                                    padding=25
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("Usuário:", align= ft.Alignment.BOTTOM_LEFT),
                                            reg_user,
                                            ft.Text("Email:", align=ft.Alignment.BOTTOM_LEFT),
                                            reg_email,
                                            ft.Text("Senha:", align=ft.Alignment.BOTTOM_LEFT),
                                            reg_pswd1,
                                            reg_pswd2,
                                            ft.Row(controls = [ft.Button(content="Registrar-se", on_click=do_register), ft.Button(content="voltar", on_click = go_login)],
                                                   alignment=ft.MainAxisAlignment.CENTER
                                                   )
                                        ]
                                    ),
                                    align=ft.Alignment.CENTER,
                                    width=300
                                ),
                            ]
                        )
                    ]
                )
            )

        else:
            
            page.views.append(
                ft.View(
                    route="/home",
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(content=logo, padding=15, align=ft.Alignment.TOP_CENTER),
                        tabs
                    ]
                )
            )

        # update fora do if/elif/else: atualiza em qualquer rota
        page.update()

    page.on_route_change = route_change
    route_change(None)


ft.run(main, assets_dir="assets")