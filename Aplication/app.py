import asyncio as asy
import time
import flet as ft
from supabase import create_client, Client
import main as m


url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"

sb: Client = create_client(url, key1)


def com_retry(fn, tentativas=5, espera=1.5):
    """Executa fn() e tenta de novo se o Supabase responder 'JWT issued at future'.

    Esse erro (PGRST303) acontece quando o token recém-emitido no login tem um
    horário de emissão (iat) alguns instantes à frente do relógio do PostgREST.
    Costuma sumir sozinho em poucos segundos, então esperamos e repetimos.
    Roda dentro de asy.to_thread, por isso time.sleep não trava a interface.
    """
    for i in range(tentativas):
        try:
            return fn()
        except Exception as ex:
            if "issued at future" in str(ex) and i < tentativas - 1:
                time.sleep(espera)
                continue
            raise


async def main(page: ft.Page):

    page.title = "Ágora Digital"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#FFFFFF"
    #page.scroll = ft.ScrollMode.ADAPTIVE

    page.views.clear()
    page.route = "/login"

    # Estado da aplicação (substitui page.current_user, que não é um atributo oficial da Page).
    #   user: nome do usuário logado (None = ninguém logado)
    #   gen:  contador que invalida as atualizações periódicas de telas antigas
    state = {"user": None, "gen": 0}


    async def go_registry(e):
        await page.push_route("/registry")

    async def go_login(e):
        await page.push_route("/login")


    async def route_change(e):

        # Cada mudança de rota invalida os loops de atualização das rotas anteriores.
        state["gen"] += 1
        my_gen = state["gen"]

        # Proteção: sem login, só /login e /registry são acessíveis.
        if page.route not in ("/login", "/registry") and state["user"] is None:
            await page.push_route("/login")
            return

        page.views.clear()
        start_loops = False

        login_email = ft.TextField(label="Email", align=ft.Alignment.TOP_CENTER)
        login_pswd = ft.TextField(label="Senha", password=True, can_reveal_password=True, align=ft.Alignment.TOP_CENTER)
        login_msg = ft.Text("", color=ft.Colors.RED)

        reg_user = ft.TextField(label="Nome de usuário", align=ft.Alignment.TOP_CENTER)
        reg_email = ft.TextField(label="Email", align=ft.Alignment.TOP_CENTER)
        reg_pswd1 = ft.TextField(label="Senha", password=True, can_reveal_password=True, align=ft.Alignment.TOP_CENTER)
        reg_pswd2 = ft.TextField(label="Confirme a senha", password=True, can_reveal_password=True, align=ft.Alignment.TOP_CENTER)
        reg_msg = ft.Text("", color=ft.Colors.RED)

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
            columns=[ft.DataColumn(ft.Text("Envios")), ft.DataColumn(ft.Text("Resolvido"))],
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

        def caixa(texto):
            return ft.Container(
                content=ft.Text(str(texto)),
                padding=5,
                margin=5,
                width=500,
                border=ft.Border.all(1, color=ft.Colors.GREY_300),
                border_radius=ft.BorderRadius.all(5)
            )

        # ---- Busca de dados (funções síncronas, executadas em thread) ----

        def _fetch_summary():
            c = sb.table("c_summary").select("Critics").gte(column="id", value=0).execute().data
            s = sb.table("s_summary").select("Suggestions").gte(column="id", value=0).execute().data
            return c, s

        def _fetch_sent():
            c = sb.table("c_bank").select("ID,Critics").gte(column="ID", value=0).order("ID").execute().data
            st = sb.table("c_status").select("id,check_problem").execute().data
            s = sb.table("s_bank").select("Suggestions").gte(column="ID", value=0).execute().data
            return c, st, s

        async def load_data_1(e=None):
            try:
                res, res1 = await asy.to_thread(com_retry, _fetch_summary)
            except Exception as ex:
                print("Erro:", ex)
                return False

            criticas_lista.controls.clear()
            sugestoes_lista.controls.clear()
            for item in res:
                criticas_lista.controls.append(caixa(item.get("Critics")))
            for item in res1:
                sugestoes_lista.controls.append(caixa(item.get("Suggestions")))
            page.update()
            return True

        # ---- Checkbox "Resolvido": grava o valor exibido na tela direto em c_status ----

        def _salvar_status(id_critica, marcado):
            resp = (
                sb.table("c_status")
                .update({"check_problem": marcado})
                .eq("id", id_critica)
                .execute()
            )
            # update sem linhas afetadas (id inexistente ou sem permissão/RLS) não gera erro
            # no Supabase; aqui transformamos isso em erro para o checkbox poder voltar atrás.
            if not resp.data:
                raise Exception("Nenhuma linha atualizada em c_status (id inexistente ou sem permissão)")

        def make_on_change(id_critica):
            # função separada para cada linha: cada checkbox guarda o seu próprio id
            async def on_change(e):
                marcado = e.control.value      # valor DEPOIS do clique (True/False)
                try:
                    await asy.to_thread(com_retry, lambda: _salvar_status(id_critica, marcado))
                except Exception as ex:
                    print("Erro ao salvar status:", ex)
                    e.control.value = not marcado   # desfaz na tela se não gravou
                    page.update()
            return on_change

        async def load_data_sent(e=None):
            try:
                res2, state2, res3 = await asy.to_thread(com_retry, _fetch_sent)
            except Exception as ex:
                print("Erro:", ex)
                return False

            # associa cada crítica ao seu status pelo id (e não pela posição na lista)
            check_por_id = {row["id"]: bool(row["check_problem"]) for row in state2}

            data_table2.rows.clear()
            data_table3.rows.clear()
            for item in res2:
                data_table2.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Container(margin=5, content=ft.Text(str(item.get("Critics"))), width=300)),
                            ft.DataCell(ft.Container(content=ft.Checkbox(
                                value=check_por_id.get(item.get("ID"), False),
                                on_change=make_on_change(item.get("ID")),
                            )))
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
            page.update()
            return True

        # ---- Atualização periódica: só enquanto esta tela (my_gen) for a atual ----

        async def update_table1(e=None):
            while state["gen"] == my_gen:
                ok = await load_data_1()
                await asy.sleep(300 if ok else 15)

        async def update_table2(e=None):
            while state["gen"] == my_gen:
                ok = await load_data_sent()
                await asy.sleep(120 if ok else 15)

        # ---- Envio de críticas e sugestões ----

        def _processar_critica(t):
            app = m.features(client=sb, critic=t)
            app.send_critic()
            app.c_summary()

        def _processar_sugestao(t):
            app = m.features(client=sb, sugg=t)
            app.send_suggestion()
            app.s_summary()

        async def c_click(e):
            t = c_field.value
            if not t or not t.strip():
                return
            c_field.value = ""
            page.update()
            try:
                await asy.to_thread(_processar_critica, t)
            except Exception as ex:
                print("Erro ao enviar crítica:", ex)
            await load_data_1()
            await load_data_sent()

        async def s_click(e):
            t = s_field.value
            if not t or not t.strip():
                return
            s_field.value = ""
            page.update()
            try:
                await asy.to_thread(_processar_sugestao, t)
            except Exception as ex:
                print("Erro ao enviar sugestão:", ex)
            await load_data_1()
            await load_data_sent()


        logo = ft.Image(src="Images/Logotipo1.png", width=220, fit=ft.BoxFit.COVER, align=ft.Alignment.TOP_CENTER)

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
                    content=ft.Column(width=400, controls=[resumo_criticas, resumo_sugestoes], scroll=ft.ScrollMode.ADAPTIVE),
                ),
                ft.Container(
                    align=ft.Alignment.TOP_CENTER,
                    content=ft.Column(width=400, controls=[critics, c_field, c_send, data_table2], scroll=ft.ScrollMode.ADAPTIVE),
                ),
                ft.Container(
                    align=ft.Alignment.TOP_CENTER,
                    content=ft.Column(width=400, controls=[suggestions, s_field, s_send, data_table3], scroll=ft.ScrollMode.ADAPTIVE),
                ),
            ],
        )

        tabs = ft.Tabs(length=3, expand=True, content=ft.Column(expand=True, controls=[tabbar, inside_tabs]))


        # ---- Sidebar (menu lateral) com opção de sair ----

        async def do_logout(e):
            try:
                # encerra a sessão no Supabase (chamada bloqueante, fora do loop do Flet)
                await asy.to_thread(sb.auth.sign_out)
            except Exception as ex:
                print(f"Erro ao deslogar: {ex}")
            state["user"] = None
            # a mudança de rota invalida os loops de atualização e mostra a tela de login
            await page.push_route("/login")

        async def open_drawer(e):
            await page.show_drawer()

        drawer = ft.NavigationDrawer(
            controls=[
                ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text("Ágora Digital", weight=ft.FontWeight.BOLD, size=18),
                            ft.Text(str(state["user"] or "")),
                        ]
                    ),
                ),
                ft.Divider(),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOGOUT),
                    title=ft.Text("Sair"),
                    on_click=do_logout,
                ),
            ],
        )


        # ---- Login e cadastro ----

        async def do_login(e):
            login_msg.value = ""
            try:
                # chamada bloqueante do Supabase fora do loop do Flet
                resposta = await asy.to_thread(
                    sb.auth.sign_in_with_password,
                    {"email": login_email.value, "password": login_pswd.value},
                )
                meta = resposta.user.user_metadata or {}
                # guarda o usuário logado; se não houver nome, usa o email
                state["user"] = meta.get("display_name") or resposta.user.email
                await page.push_route("/home")

            except Exception as ex:
                print(f"Erro ao fazer login: {ex}")
                login_msg.value = "Não foi possível entrar. Verifique email e senha."
                page.update()


        async def do_register(e):
            reg_msg.value = ""
            if reg_pswd1.value != reg_pswd2.value:
                reg_msg.value = "As duas senhas devem ser iguais."
                page.update()
                return
            try:
                resposta = await asy.to_thread(
                    sb.auth.sign_up,
                    {"email": reg_email.value,
                     "password": reg_pswd1.value,
                     "options": {
                         "data": {
                             "display_name": reg_user.value
                         }
                     }
                     }
                )
                print(f"Cadastro realizado com sucesso! Metadados: {resposta.user.user_metadata}")
                await page.push_route("/login")
            except Exception as ex:
                print(f"Erro ao cadastrar: {ex}")
                reg_msg.value = "Não foi possível cadastrar. Tente novamente."
                page.update()


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
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("Login com email:", align=ft.Alignment.BOTTOM_LEFT),
                                            login_email,
                                            login_pswd,
                                            login_msg,
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
                                            ft.Text("Usuário:", align=ft.Alignment.BOTTOM_LEFT),
                                            reg_user,
                                            ft.Text("Email:", align=ft.Alignment.BOTTOM_LEFT),
                                            reg_email,
                                            ft.Text("Senha:", align=ft.Alignment.BOTTOM_LEFT),
                                            reg_pswd1,
                                            reg_pswd2,
                                            reg_msg,
                                            ft.Row(
                                                controls=[
                                                    ft.Button(content="Registrar-se", on_click=do_register),
                                                    ft.Button(content="voltar", on_click=go_login)
                                                ],
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
                    appbar=ft.AppBar(
                        leading=ft.IconButton(icon=ft.Icons.MENU, on_click=open_drawer),
                        title=ft.Text("Ágora Digital"),
                    ),
                    drawer=drawer,
                    controls=[
                        ft.Container(content=logo, padding=5, align=ft.Alignment.TOP_CENTER),
                        ft.Container(content=ft.Text(f"Olá, {state['user']}!", weight=ft.FontWeight.BOLD), align=ft.Alignment.TOP_CENTER),
                        tabs,
                    ]
                )
            )
            start_loops = True

        page.update()

        # Os loops só começam depois que a tela já está montada, e só na /home.
        if start_loops:
            page.run_task(update_table1)
            page.run_task(update_table2)

    page.on_route_change = route_change
    await route_change(None)


ft.run(main, assets_dir="assets")