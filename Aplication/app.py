import asyncio as asy
import time
import flet as ft
from supabase import create_client, Client
import main as m


url = "https://xdmqojzrjnicaoxxnmdf.supabase.co"
key1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhkbXFvanpyam5pY2FveHhubWRmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc2ODYzMTcsImV4cCI6MjEwMzI2MjMxN30.RwC39eVuaAVaWmtVEIbdzTcrdHr7Y5-KGTcAvaReUqo"

sb: Client = create_client(url, key1)

# Chaves para persistência da sessão no dispositivo (SharedPreferences)
KEY_ACCESS_TOKEN = "agora_digital.access_token"
KEY_REFRESH_TOKEN = "agora_digital.refresh_token"


def retry_call(fn, attempts=5, delay=1.5):
    """Executa fn() e tenta de novo se o Supabase responder 'JWT issued at future'.

    Esse erro (PGRST303) acontece quando o token recém-emitido no login tem um
    horário de emissão (iat) alguns instantes à frente do relógio do PostgREST.
    Costuma sumir sozinho em poucos segundos, então esperamos e repetimos.
    Roda dentro de asy.to_thread, por isso time.sleep não trava a interface.
    """
    for i in range(attempts):
        try:
            return fn()
        except Exception as ex:
            if "issued at future" in str(ex) and i < attempts - 1:
                time.sleep(delay)
                continue
            raise


async def main(page: ft.Page):

    page.title = "Ágora Digital"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#FFFFFF"

    page.views.clear()

    # Instância mantida viva durante toda a vida da página para persistir dados no Android/Desktop
    prefs = ft.SharedPreferences()
    state = {"user": None, "gen": 0}

    async def save_session(session):
        if session and session.access_token and session.refresh_token:
            await prefs.set(KEY_ACCESS_TOKEN, session.access_token)
            await prefs.set(KEY_REFRESH_TOKEN, session.refresh_token)

    async def clear_session():
        await prefs.remove(KEY_ACCESS_TOKEN)
        await prefs.remove(KEY_REFRESH_TOKEN)

    async def restore_session():
        """Tenta recuperar a sessão salva no aparelho e renovar o token no Supabase."""
        try:
            access_token = await prefs.get(KEY_ACCESS_TOKEN)
            refresh_token = await prefs.get(KEY_REFRESH_TOKEN)
            if not access_token or not refresh_token:
                return False

            response = await asy.to_thread(
                retry_call,
                lambda: sb.auth.set_session(access_token, refresh_token),
            )
            if response and response.user:
                meta = response.user.user_metadata or {}
                state["user"] = meta.get("display_name") or response.user.email
                # Atualiza os tokens salvos caso o Supabase tenha emitido um novo par
                await save_session(response.session)
                return True
        except Exception as ex:
            print(f"Sessão salva expirada ou inválida: {ex}")
            await clear_session()
        return False


    async def go_register(e):
        await page.push_route("/registry")

    async def go_login(e):
        await page.push_route("/login")


    async def handle_route_change(e):

        # Cada mudança de rota invalida os loops de atualização das rotas anteriores.
        state["gen"] += 1
        my_gen = state["gen"]

        # Proteção: sem login, só /login e /registry são acessíveis.
        if page.route not in ("/login", "/registry") and state["user"] is None:
            await page.push_route("/login")
            return

        page.views.clear()
        start_loops = False

        width = min(600, int((page.width or 600) - 32))

        login_email = ft.TextField(label="Email", align=ft.Alignment.TOP_CENTER)
        login_pswd = ft.TextField(label="Senha", password=True, can_reveal_password=True, align=ft.Alignment.TOP_CENTER)
        login_msg = ft.Text("", color=ft.Colors.RED)

        register_user = ft.TextField(label="Nome de usuário", align=ft.Alignment.TOP_CENTER)
        register_email = ft.TextField(label="Email", align=ft.Alignment.TOP_CENTER)
        register_password = ft.TextField(label="Senha", password=True, can_reveal_password=True, align=ft.Alignment.TOP_CENTER)
        confirm_password = ft.TextField(label="Confirme a senha", password=True, can_reveal_password=True, align=ft.Alignment.TOP_CENTER)
        register_message = ft.Text("", color=ft.Colors.RED)

        critics_list = ft.Column(spacing=0)
        critics_summary = ft.Column(
            controls=[
                ft.Text("Resumo das críticas", weight=ft.FontWeight.BOLD),
                critics_list,
            ],
        )

        # Resumo das sugestões: também é uma Column (sem divisórias de tabela)
        suggestions_list = ft.Column(spacing=0)

        suggestions_summary = ft.Column(
            controls=[
                ft.Text("Resumo das sugestões", weight=ft.FontWeight.BOLD),
                suggestions_list,
            ]
        )

        # envios de críticas
        data_table2 = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Envios")),
                ft.DataColumn(ft.Text("Resolvido")),
            ],
            rows=[],
            column_spacing=12,
            horizontal_margin=10,
            data_row_max_height=float("inf"),
            border=ft.Border.all(1, ft.Colors.GREY_500),
            border_radius=ft.BorderRadius.all(5),
        )

        # envios de sugestões
        data_table3 = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Envios"))],
            rows=[],
            horizontal_margin=10,
            data_row_max_height=float("inf"),
            border=ft.Border.all(1, ft.Colors.GREY_500),
            border_radius=ft.BorderRadius.all(5),
        )

        def create_text_box(text):
            return ft.Container(
                content=ft.Text(str(text)),
                padding=5,
                margin=5,
                width=width - 10,
                border=ft.Border.all(1, color=ft.Colors.GREY_300),
                border_radius=ft.BorderRadius.all(5),
            )

        # ---- Busca de dados (funções síncronas, executadas em thread) ----

        def _fetch_summaries():
            c = sb.table("c_summary").select("Critics").gte(column="id", value=0).execute().data
            s = sb.table("s_summary").select("Suggestions").gte(column="id", value=0).execute().data
            return c, s

        def _fetch_submissions():
            c = sb.table("c_bank").select("ID,Critics").gte(column="ID", value=0).order("ID").execute().data
            status_data = sb.table("c_status").select("id,check_problem").execute().data
            s = sb.table("s_bank").select("Suggestions").gte(column="ID", value=0).execute().data
            return c, status_data, s

        async def load_summaries(e=None):
            try:
                critics_data, suggestions_data = await asy.to_thread(retry_call, _fetch_summaries)
            except Exception as ex:
                print("Erro:", ex)
                return False

            critics_list.controls.clear()
            suggestions_list.controls.clear()
            for item in critics_data:
                critics_list.controls.append(create_text_box(item.get("Critics")))
            for item in suggestions_data:
                suggestions_list.controls.append(create_text_box(item.get("Suggestions")))
            page.update()
            return True

        # ---- Checkbox "Resolvido": grava o valor exibido na tela direto em c_status ----

        def _save_status(critic_id, is_checked):
            resp = (
                sb.table("c_status")
                .update({"check_problem": is_checked})
                .eq("id", critic_id)
                .execute()
            )
            # update sem linhas afetadas (id inexistente ou sem permissão/RLS) não gera erro
            # no Supabase; aqui transformamos isso em erro para o checkbox poder voltar atrás.
            if not resp.data:
                raise Exception("Nenhuma linha atualizada em c_status (id inexistente ou sem permissão)")

        def create_status_handler(critic_id):
            # função separada para cada linha: cada checkbox guarda o seu próprio id
            async def on_change(e):
                is_checked = e.control.value      # valor DEPOIS do clique (True/False)
                try:
                    await asy.to_thread(retry_call, lambda: _save_status(critic_id, is_checked))
                except Exception as ex:
                    print("Erro ao salvar status:", ex)
                    e.control.value = not is_checked   # desfaz na tela se não gravou
                    page.update()
            return on_change

        async def load_data_sent(e=None):
            try:
                critics_submissions, statuses, suggestions_submissions = await asy.to_thread(retry_call, _fetch_submissions)
            except Exception as ex:
                print("Erro:", ex)
                return False

            # associa cada crítica ao seu status pelo id (e não pela posição na lista)
            checked_by_id = {row["id"]: bool(row["check_problem"]) for row in statuses}

            text_width = max(120, width - 150)

            data_table2.rows.clear()
            data_table3.rows.clear()
            for item in critics_submissions:
                data_table2.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(str(item.get("Critics"))),
                                    width=text_width,
                                    padding=ft.Padding.symmetric(vertical=6),
                                )
                            ),
                            ft.DataCell(
                                ft.Container(
                                    width=64,
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Checkbox(
                                        value=checked_by_id.get(item.get("ID"), False),
                                        on_change=create_status_handler(item.get("ID")),
                                    ),
                                )
                            ),
                        ]
                    )
                )
            for item in suggestions_submissions:
                data_table3.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                ft.Container(
                                    padding=ft.Padding.symmetric(vertical=6),
                                    content=ft.Text(str(item.get("Suggestions"))),
                                    width=max(160, width - 60),
                                )
                            )
                        ]
                    )
                )
            page.update()
            return True

        # ---- Atualização periódica: só enquanto esta tela (my_gen) for a atual ----

        async def update_summaries(e=None):
            while state["gen"] == my_gen:
                ok = await load_summaries()
                await asy.sleep(300 if ok else 15)

        async def update_submissions(e=None):
            while state["gen"] == my_gen:
                ok = await load_data_sent()
                await asy.sleep(120 if ok else 15)

        # ---- Envio de críticas e sugestões ----

        def _process_critic(t):
            app = m.features(client=sb, critic=t)
            app.send_critic()
            app.c_summary()

        def _process_suggestion(t):
            app = m.features(client=sb, sugg=t)
            app.send_suggestion()
            app.s_summary()

        async def c_click(e):
            t = f"{state['user']}: {c_field.value}"
            if not t or not t.strip():
                return
            c_field.value = ""
            page.update()
            try:
                await asy.to_thread(_process_critic, t)
            except Exception as ex:
                print("Erro ao enviar crítica:", ex)
            await load_summaries()
            await load_data_sent()

        async def s_click(e):
            t = f"{state['user']}: {s_field.value}"
            if not t or not t.strip():
                return
            s_field.value = ""
            page.update()
            try:
                await asy.to_thread(_process_suggestion, t)
            except Exception as ex:
                print("Erro ao enviar sugestão:", ex)
            await load_summaries()
            await load_data_sent()


        logo = ft.Image(src="Images/Logotipo1.png", width=220, fit=ft.BoxFit.COVER, align=ft.Alignment.BOTTOM_CENTER)

        critics = ft.Text("Críticas", weight=ft.FontWeight.BOLD)
        c_field = ft.TextField(label="Escreva suas críticas", multiline=True, text_align="LEFT", max_length=300)
        c_send = ft.Button(content="Enviar", on_click=c_click)

        suggestions = ft.Text("Sugestões", weight=ft.FontWeight.BOLD)
        s_field = ft.TextField(label="Escreva suas sugestões", multiline=True, text_align="LEFT", max_length=300)
        s_send = ft.Button(content="Enviar", on_click=s_click)

        tab_1 = ft.Tab(label="Agora")
        tab_2 = ft.Tab(label="Críticas")
        tab_3 = ft.Tab(label="Sugestões")

        home_content = ft.Container(
            width=width,
            padding=15,
            content=ft.Column(width=width, controls=[critics_summary, suggestions_summary]),
        )
        critics_content = ft.Container(
            width=width,
            padding=15,
            content=ft.Column(width=width, controls=[critics, c_field, c_send, data_table2]),
        )
        suggestions_content = ft.Container(
            width=width,
            padding=15,
            content=ft.Column(width=width, controls=[suggestions, s_field, s_send, data_table3]),
        )

        current_tab_content = ft.Container(content=home_content)

        async def handle_tab_change(e):
            index = e.control.selected_index
            if index == 0:
                current_tab_content.content = home_content
            elif index == 1:
                current_tab_content.content = critics_content
            else:
                current_tab_content.content = suggestions_content
            page.update()

        tabbar = ft.TabBar(tabs=[tab_1, tab_2, tab_3], tab_alignment=ft.TabAlignment.CENTER)
        tabs_header = ft.Tabs(
            length=3,
            selected_index=0,
            on_change=handle_tab_change,
            content=ft.Column(controls=[tabbar]),
        )


        # ---- Sidebar (menu lateral) com opção de sair ----

        async def do_logout(e):
            try:
                # encerra a sessão no Supabase (chamada bloqueante, fora do loop do Flet)
                await asy.to_thread(sb.auth.sign_out)
            except Exception as ex:
                print(f"Erro ao deslogar: {ex}")
            await clear_session()
            state["user"] = None
            # a mudança de rota invalida os loops de atualização e mostra a tela de login
            await page.push_route("/login")

        async def open_navigation_drawer(e):
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
                response = await asy.to_thread(
                    sb.auth.sign_in_with_password,
                    {"email": login_email.value, "password": login_pswd.value},
                )
                meta = response.user.user_metadata or {}
                # guarda o usuário logado; se não houver nome, usa o email
                state["user"] = meta.get("display_name") or response.user.email
                # persiste os tokens no dispositivo para manter o login nas próximas aberturas
                await save_session(response.session)
                await page.push_route("/home")

            except Exception as ex:
                print(f"Erro ao fazer login: {ex}")
                login_msg.value = "Não foi possível entrar. Verifique email e senha."
                page.update()


        async def register_user_account(e):
            register_message.value = ""
            if register_password.value != confirm_password.value:
                register_message.value = "As duas senhas devem ser iguais."
                page.update()
                return
            try:
                response = await asy.to_thread(
                    sb.auth.sign_up,
                    {"email": register_email.value,
                     "password": register_password.value,
                     "options": {
                         "data": {
                             "display_name": register_user.value
                         }
                     }
                     }
                )
                print(f"Cadastro realizado com sucesso! Metadados: {response.user.user_metadata}")
                await page.push_route("/login")
            except Exception as ex:
                print(f"Erro ao cadastrar: {ex}")
                register_message.value = "Não foi possível cadastrar. Tente novamente."
                page.update()


        if page.route == "/login":

            page.views.append(
                ft.View(
                    route="/login",
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Container(content=logo, padding=25, align=ft.Alignment.BOTTOM_CENTER),
                                ft.Container(
                                    content=ft.Text("Bem Vindo!", weight=ft.FontWeight.BOLD, align=ft.Alignment.TOP_CENTER),
                                    padding=15
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
                                        ft.Button(content="Registrar-se", on_click=go_register)
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
                                ft.Container(content=logo, padding=25, align=ft.Alignment.BOTTOM_CENTER),
                                ft.Container(
                                    content=ft.Text("Cadastro", weight=ft.FontWeight.BOLD, align=ft.Alignment.TOP_CENTER),
                                    padding=15
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        controls=[
                                            ft.Text("Usuário:", align=ft.Alignment.BOTTOM_LEFT),
                                            register_user,
                                            ft.Text("Email:", align=ft.Alignment.BOTTOM_LEFT),
                                            register_email,
                                            ft.Text("Senha:", align=ft.Alignment.BOTTOM_LEFT),
                                            register_password,
                                            confirm_password,
                                            register_message,
                                            ft.Row(
                                                controls=[
                                                    ft.Button(content="Registrar-se", on_click=register_user_account),
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
                    scroll=ft.ScrollMode.ADAPTIVE,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    drawer=drawer,
                    controls=[
                        ft.Container(
                            content = ft.Row(
                                controls=[
                                    ft.IconButton(icon=ft.Icons.MENU, on_click=open_navigation_drawer),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                
                            ),
                            padding= 20
                        ),
                        ft.Container(content=logo, align=ft.Alignment.BOTTOM_CENTER),
                        ft.Container(
                            content=ft.Text(f"Olá, {state['user']}!", weight=ft.FontWeight.BOLD),
                            align=ft.Alignment.TOP_CENTER,
                            padding=10,
                        ),
                        ft.Container(content=tabs_header, width=width),
                        current_tab_content,
                    ]
                )
            )
            start_loops = True

        page.update()

        # Os loops só começam depois que a tela já está montada, e só na /home.
        if start_loops:
            page.run_task(update_summaries)
            page.run_task(update_submissions)

    page.on_route_change = handle_route_change

    # Se existir uma sessão válida salva no dispositivo, vai direto para /home
    if await restore_session():
        page.route = "/home"
    else:
        page.route = "/login"

    await handle_route_change(None)


ft.run(main, assets_dir="assets")