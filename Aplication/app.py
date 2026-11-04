import asyncio as asy
from datetime import datetime
import flet as ft
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
import json
import main as m

url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"

sb: Client = create_client(url, key1)


def main(page: ft.Page):

    page.title = "Ágora Digital"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#FFFFFF"
    page.scroll = ft.ScrollMode.ADAPTIVE

    # ---------------------------------------------------------------
    # Resumo das críticas: agora é uma Column (sem divisórias de tabela).
    # Cada crítica é um Container com borda própria.
    # ---------------------------------------------------------------
    criticas_lista = ft.Column(spacing=0)

    resumo_criticas = ft.Column(
        controls=[
            ft.Text("Resumo das críticas", weight=ft.FontWeight.BOLD),
            criticas_lista,
        ]
    )

    # Row que agrupa as colunas do resumo. Para adicionar outra coluna ao lado
    # no futuro, basta incluir outra ft.Column em "controls".
    # Com wrap=True, em telas estreitas a coluna nova desce para baixo.
    resumo_row = ft.Row(
        controls=[resumo_criticas],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        wrap=True,
        spacing=20,
        run_spacing=20,
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
        border=ft.Border.all(1,ft.Colors.GREY_500),
        border_radius=ft.BorderRadius.all(5)
        
    )
    # envios de sugestões
    data_table3 = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Envios"))],
        rows=[],
        data_row_max_height=float("inf"),
        border=ft.Border.all(1,ft.Colors.GREY_500),
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
                            ft.DataCell(ft.Container(margin = 5,content=ft.Text(str(item.get("Critics")))))
                        ]
                    )
                )
            for item in res3:
                data_table3.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Container(margin = 5,content=ft.Text(str(item.get("Suggestions")))))
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

    logo = ft.Image(src="Aplication/Logotipo.png", width=250, fit=ft.BoxFit.COVER, align=ft.Alignment.TOP_CENTER)

    critics = ft.Text("Críticas", weight= ft.FontWeight.BOLD)
    c_field = ft.TextField(label="Escreva suas críticas", multiline=True, text_align="LEFT", max_length=300)
    c_send = ft.Button(content="Enviar", on_click=c_click)

    suggestions = ft.Text("Sugestões", weight= ft.FontWeight.BOLD)
    s_field = ft.TextField(label="Escreva suas sugestões", multiline=True, text_align="LEFT", max_length=300)
    s_send = ft.Button(content="Enviar", on_click=s_click)

    tab_1 = ft.Tab(label="Agora")
    tab_2 = ft.Tab(label="Críticas")
    tab_3 = ft.Tab(label="Sugestões")

    tabbar = ft.TabBar(tabs=[tab_1, tab_2, tab_3], tab_alignment= ft.TabAlignment.CENTER)
    inside_tabs = ft.TabBarView(
        width=1080,
        height=1920,
        align=ft.Alignment.CENTER,
        controls=[
            ft.Container(
                align=ft.Alignment.CENTER,
                content=ft.Column(width=600, controls=[resumo_row, resumo_sugestoes]),
            ),
            ft.Container(
                align=ft.Alignment.CENTER,
                content=ft.Column(width=600, controls=[critics, c_field, c_send, data_table2]),
            ),
            ft.Container(
                align=ft.Alignment.CENTER,
                content=ft.Column(width=600, controls=[suggestions, s_field, s_send, data_table3]),
            ),
        ],
    )

    tabs = ft.Tabs(length=3, expand=True, content=ft.Column(width=1080, controls=[tabbar, inside_tabs]))

    page.add(
        logo,
        tabs,
    )


ft.run(main)