
import flet as ft


def main(page: ft.Page):

    
    page.title = "Ágora Digital"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 700
    page.padding = 15
    page.bgcolor = "#FFFFFF"

    # Função para criar as abas de envio
    def criar_formulario(titulo, dica):

        campo = ft.TextField(
            hint_text=dica,
            multiline=True,
            min_lines=4,
            max_lines=8,
            expand=True,
            border_radius=10,
            bgcolor="white",
        )

        mensagem = ft.Text("", color="green")

        def enviar(e):
            texto = campo.value.strip()

            if texto:
                print(f"{titulo}: {texto}")

                mensagem.value = "Enviado com sucesso!"
                campo.value = ""
            else:
                mensagem.value = "Digite algo antes de enviar."
                mensagem.color = "red"

            page.update()

        return ft.Column(
            controls=[
                ft.Text(
                    titulo,
                    size=22,
                    weight=ft.FontWeight.BOLD
                ),
                campo,
                ft.Button(
                    content="Enviar",
                    icon=ft.Icons.SEND,
                    on_click=enviar,
                    width=150,
                ),
                mensagem,
            ],
            spacing=15,
            expand=True,
        )

    # Conteúdo da aba Agora
    agora = ft.Column(
        controls=[
            ft.Text(
                "Agora",
                size=24,
                weight=ft.FontWeight.BOLD
            ),
            ft.Text(
                "Acompanhe os principais acontecimentos "
                "e problemas da sua cidade."
            ),
        ],
        spacing=15,
    )

    # Conteúdo das outras abas
    criticas = criar_formulario(
        "Enviar uma crítica",
        "Descreva um problema ou uma reclamação..."
    )

    sugestoes = criar_formulario(
        "Enviar uma sugestão",
        "Compartilhe uma ideia para melhorar sua cidade..."
    )

    # Navegação inferior
    def mudar_aba(e):
        indice = e.control.selected_index

        conteudos.controls.clear()

        if indice == 0:
            conteudos.controls.append(agora)
        elif indice == 1:
            conteudos.controls.append(criticas)
        elif indice == 2:
            conteudos.controls.append(sugestoes)

        page.update()

    navegacao = ft.NavigationBar(
        selected_index=0,
        on_change=mudar_aba,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Agora",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.REPORT_OUTLINED,
                selected_icon=ft.Icons.REPORT,
                label="Críticas",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.LIGHTBULB_OUTLINE,
                selected_icon=ft.Icons.LIGHTBULB,
                label="Sugestões",
            ),
        ],
    )

    # Área principal
    conteudos = ft.Column(
        controls=[agora],
        expand=True,
    )

    page.add(
        ft.Container(
            content=conteudos,
            padding=20,
            expand=True,
        ),
        navegacao,
    )


ft.run(main)
