import flet as ft
import psutil
import shutil
import winreg
import zipfile
import os
import json
import assets.scripts.language as language

config_file = {'language':'ENG', 'theme': 'dark', 'fsltl_dir': '', 'cia_off': ''}

install_directory = 'C:\\'
language_type = 'ENG'
text_language = language.language[language_type]
languages_options = []
for lang in language.language.keys():
    languages_options.append(ft.dropdown.Option(text=language.language[lang][0], key=lang))

def get_config_locate():
    return os.path.join(os.path.expanduser('~'), 'fsltl_config.cfg')

def get_desktop_path():
    return os.path.join(os.path.expanduser('~'), 'Desktop')

def create_shortcut(target_path, shortcut_name):
    desktop_path = get_desktop_path()
    shortcut_path = os.path.join(desktop_path, shortcut_name + ".lnk")
    app_path = os.path.join(target_path, '\\FSLTL Editor\\fsltleditor.lnk')

    # Cria o atalho
    try:
        shutil.copy(app_path, shortcut_path)
        print(f"Atalho '{shortcut_name}' criado com sucesso em '{shortcut_path}'")
    except Exception as e:
        print(f"Erro ao criar atalho: {e} na pasta padrão")
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders')
            desktop_path, _ = winreg.QueryValueEx(key, "Desktop")
            shortcut_path = os.path.join(desktop_path, shortcut_name + ".lnk")
            shutil.copy(app_path, shortcut_path)
        except Exception as e:
            print(f"Erro ao obter o caminho do desktop: {e}")
            

def unzip(zip_file_path, dest_dir):
    if os.path.exists(dest_dir):
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(dest_dir)
                return True
        except Exception as e:
            print(f"Erro:{str(e)}")
            return False
    else:
        print('Diretório não existe')
        return False

def save_config():
    '''
    Salva as configurações no disco.
    '''
    try:  
        with open(get_config_locate(), 'w') as file:
            json.dump(config_file, file)
        print('Configs salvas')
        
    except Exception as e:
        print(f'Erro: {str(e)}')

def read_config():
    '''
    Faz a leitura das configurações que estão salvas no disco.

    Returns:
    -
    bool
        True, se conseguiu ler as configs no disco.

        False, se NÃO conseguiu ler as configs no disco.
    '''
    global config_file

    if not os.path.exists(get_config_locate()):
        save_config()
    else:
        with open(get_config_locate(), 'r') as file:
            config_file = json.load(file)
        print('Configuração carregada com sucesso.')
        if config_file['fsltl_dir'] == '':
            return False
        else:
            return True
    return False

def get_free_space(drive):
    usage = psutil.disk_usage(drive)
    return round(usage.free / (1024.0 ** 2))

read_config()

# MAIN APP --------------------------------------------------------------------------------------------------------------------------------------
def main(page: ft.Page):
    page.window_width = 800
    page.window_height = 500
    page.window_center()
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.title = 'FSLTL Editor Setup 1.4'
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=ft.colors.GREEN, tertiary=ft.colors.AMBER_700),
        scrollbar_theme=ft.ScrollbarTheme(
            track_color={
                ft.MaterialState.HOVERED: '#33000000',
                ft.MaterialState.DEFAULT: '#33000000',
            },
            track_visibility=True,
            track_border_color=ft.colors.TRANSPARENT,
            thumb_visibility=True,
            thumb_color={
                ft.MaterialState.HOVERED: '#FFFFFFFF',
                ft.MaterialState.DEFAULT: '#44FFFFFF',
            },
            thickness=10,
            radius=100,
            main_axis_margin=0,
            cross_axis_margin=0,
        ), 
    )

    directory_path = ft.TextField(value=f"{install_directory}", color=ft.colors.BLACK, bgcolor=ft.colors.GREY_400, content_padding=3, read_only=True)
    free_space = ft.Text(text_language[1], size=10)
    

    def get_directory_result(e: ft.FilePickerResultEvent):
        global install_directory
        if e.path:
            install_directory = e.path
        else:
            install_directory = "C:\\"
        directory_path.value = install_directory
        directory_path.update()

        espace_free = get_free_space(install_directory[:3])
        free_space.value = f"{text_language[1]} {espace_free} MB"
        free_space.update()

    get_directory_dialog = ft.FilePicker(on_result=get_directory_result)
    page.overlay.extend([get_directory_dialog])

    def install_app(e):
        global config_file
        
        progress_ring.visible = True
        progress_ring.update()
        print("Instalando...")
        
        config_file['language'] = language_type
        config_file['fsltl_dir'] = ''
        save_config()
        
        caminho_atual = os.getcwd()
        zipFile = caminho_atual + '\\setup'
        if unzip(zipFile, install_directory):
            create_shortcut(install_directory, 'FSLTL Editor')
            print("Programa instalado com sucesso!")            
            progress_ring.visible = False
            page.go('/pg5')


    next_button = ft.ElevatedButton(text_language[6], on_click=lambda _: page.go('/pg1'))
    cancel_button = ft.ElevatedButton(text_language[7], on_click=lambda _: page.window_destroy())
    progress_ring = ft.ProgressRing(width=30, height=30, stroke_width = 2, visible=False)

    def change_language(e):
        global text_language
        global language_type

        language_type = e.control.value
        text_language = language.language[language_type]
        e.control.label = text_language[3]
        e.control.hint_text = text_language[4]
        e.control.data.value = text_language[2]
        next_button.text = text_language[6]
        cancel_button.text = text_language[7]

        page.update()

# LAYOUTS -----------------------------------------------------------------------------------------------------------------------------------------
    def layout(e):
        page.views.clear()
        page.views.append(
            ft.View(
                '/',
                [
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Container(
                                            content=ft.Image(src='assets\\icon.png'), bgcolor=ft.colors.BLACK, height=420, width=200,
                                        ),
                                    ],
                                    width=200,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Column(
                                    controls=[
                                        titulo := ft.Text(
                                            text_language[2], size=24, weight=ft.FontWeight.W_400,),
                                        ft.Divider(thickness=1, height=1),
                                        ft.Column(
                                            [   
                                                ft.Container(
                                                    content=ft.Dropdown(
                                                                label=text_language[3],
                                                                border_color=ft.colors.INVERSE_SURFACE,
                                                                hint_text=text_language[4],
                                                                options=languages_options,
                                                                on_change=change_language,
                                                                data=titulo,
                                                                width=300,
                                                            ),
                                                            alignment=ft.alignment.center,
                                                            width=600,
                                                            height=310,
                                                ),
                                            ],
                                            height=310,
                                        ),
                                        ft.Divider(thickness=1, height=1),
                                        ft.Row(
                                            [
                                                ft.Container(content=next_button,
                                                ),
                                                ft.Container(content=cancel_button,
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.END
                                        ),
                                    ],
                                    width=540,
                                ),
                            ],
                        ),
                        padding=ft.Padding(10, 10, 10, 10),
                        width=page.window_width,
                        height=page.window_height,
                    )
                ]
            )
        )

        if page.route == '/pg1':
            page.views.append(
                ft.View(
                    'pg1',
                    [
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Container(
                                                content=ft.Image(src='assets\\icon.png'), bgcolor=ft.colors.BLACK, height=420, width=200,
                                            ),
                                        ],
                                        width=200,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                text_language[10], size=24, weight=ft.FontWeight.W_400,),
                                            ft.Divider(thickness=1, height=1),
                                            ft.Column(
                                                [
                                                    ft.Text(text_language[11]),
                                                    ft.Text(text_language[12]),
                                                    ft.Text(text_language[13]),
                                                    ft.Text(text_language[14]),
                                                ],
                                                height=310,
                                                scroll=ft.ScrollMode.AUTO,

                                            ),
                                            ft.Divider(thickness=1, height=1),
                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        content=ft.ElevatedButton(text_language[5], on_click=lambda _: page.go('/')),
                                                    ),
                                                    ft.Container(
                                                        content=ft.ElevatedButton(text_language[6], on_click=lambda _: page.go('/pg2')),
                                                    ),
                                                    ft.Container(
                                                        content=ft.ElevatedButton(text_language[7], on_click=lambda _: page.window_destroy()),
                                                    ),
                                                ],
                                                alignment=ft.MainAxisAlignment.END
                                            ),
                                        ],
                                        width=540,
                                    ),
                                ],
                            ),
                            padding=ft.Padding(10, 10, 10, 10),
                            width=page.window_width,
                            height=page.window_height,
                        )
                    ]
                )
            )

        if page.route == '/pg2':
            page.views.append(
                ft.View(
                    'pg2',
                    [
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Container(
                                                content=ft.Image(src='assets\\icon.png'), bgcolor=ft.colors.BLACK, height=420, width=200,
                                            ),
                                        ],
                                        width=200,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                text_language[15], size=24, weight=ft.FontWeight.W_400,),
                                            ft.Divider(thickness=1, height=1),
                                            ft.Container(
                                                content=ft.Container(
                                                    content=ft.Column(
                                                        [
                                                            ft.Text(text_language[16], width=500, text_align=ft.TextAlign.JUSTIFY),
                                                            ft.Text(text_language[17], width=500, text_align=ft.TextAlign.JUSTIFY),
                                                            ft.Text(text_language[18], width=500, text_align=ft.TextAlign.JUSTIFY),
                                                            ft.Text(text_language[19], width=500, text_align=ft.TextAlign.JUSTIFY),
                                                            ft.Text(text_language[20], width=500, text_align=ft.TextAlign.JUSTIFY),
                                                            ft.Text(text_language[21], width=500, text_align=ft.TextAlign.JUSTIFY),
                                                            ft.Text(text_language[22], width=500, text_align=ft.TextAlign.JUSTIFY),
                                                            ft.Text(text_language[23], width=500, text_align=ft.TextAlign.JUSTIFY),
                                                            ft.Text(text_language[24], width=500, text_align=ft.TextAlign.JUSTIFY),
                                                            ft.Text(text_language[25], width=500, text_align=ft.TextAlign.JUSTIFY),
                                                        ],
                                                        height=290,
                                                        width=540,
                                                        scroll=ft.ScrollMode.ALWAYS,
                                                    ),
                                                ),
                                                border=ft.border.all(1,ft.colors.GREY_800),
                                                padding=ft.Padding(10,10,10,10), 
                                                border_radius=ft.border_radius.all(8)
                                            ),
                                            ft.Divider(thickness=1, height=1),
                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        content=ft.ElevatedButton(text_language[5], on_click=lambda _: page.go('/pg1')),
                                                    ),
                                                    ft.Container(
                                                        content=ft.ElevatedButton(text_language[8], on_click=lambda _: page.go('/pg3')),
                                                    ),
                                                    ft.Container(
                                                        content=ft.ElevatedButton(text_language[7], on_click=lambda _: page.window_destroy()),
                                                    ),
                                                ],
                                                alignment=ft.MainAxisAlignment.END
                                            ),
                                        ],
                                        width=540,
                                    ),
                                ],
                            ),
                            padding=ft.Padding(10, 10, 10, 10),
                            width=page.window_width,
                            height=page.window_height,
                        )
                    ]
                )
            )

        if page.route == '/pg3':
            page.views.append(
                ft.View(
                    'pg3',
                    [
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Container(
                                                content=ft.Image(src='assets\\icon.png'), bgcolor=ft.colors.BLACK, height=420, width=200,
                                            ),
                                        ],
                                        width=200,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                text_language[26], size=24, weight=ft.FontWeight.W_400,),
                                            ft.Divider(thickness=1, height=1),
                                            ft.Column(
                                                [
                                                    ft.Text(text_language[27]),
                                                    ft.Text(text_language[28]),
                                                    ft.Text(text_language[29]),
                                                    ft.Text(text_language[30]),
                                                    ft.Divider(thickness=1, height=1),
                                                    ft.Container(height=10),
                                                    ft.Text(text_language[31]),

                                                    ft.Container(content=ft.Row(
                                                        [
                                                            ft.Container(content=directory_path, width=380, height=30,
                                                                         alignment=ft.alignment.center_left,),
                                                            ft.ElevatedButton(
                                                                text_language[32], on_click=lambda _: get_directory_dialog.get_directory_path()),
                                                        ]
                                                    ), 
                                                    border=ft.border.all(1, ft.colors.GREY_800), 
                                                    padding=ft.Padding(20, 20, 20, 20), 
                                                    border_radius=ft.border_radius.all(8)),
                                                    ft.Row(
                                                        [
                                                            ft.Column(
                                                                [
                                                                    ft.Text(text_language[33], size=10),
                                                                    free_space
                                                                ],
                                                            ),
                                                            ft.Container(expand=True),
                                                            progress_ring,
                                                        ],
                                                    ),
                                                ],
                                                height=310,
                                            ),
                                            ft.Divider(thickness=1, height=1),
                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        content=ft.ElevatedButton(text_language[5], on_click=lambda _: page.go('/pg2')),
                                                    ),
                                                    ft.Container(
                                                        content=ft.ElevatedButton(text_language[9], on_click=install_app),
                                                    ),
                                                    ft.Container(
                                                        content=ft.ElevatedButton(text_language[7], on_click=lambda _: page.window_destroy()),
                                                    ),
                                                ],
                                                alignment=ft.MainAxisAlignment.END
                                            ),
                                        ],
                                        width=540,
                                    ),
                                ],
                            ),
                            padding=ft.Padding(10, 10, 10, 10),
                            width=page.window_width,
                            height=page.window_height,
                        )
                    ]
                )
            )

        if page.route == '/pg5':
            page.views.append(
                ft.View(
                    'pg5',
                    [
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Column(
                                        controls=[
                                            ft.Container(
                                                content=ft.Image(src='assets\\icon.png'), bgcolor=ft.colors.BLACK, height=420, width=200,
                                            ),
                                        ],
                                        width=200,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                text_language[34], size=24, weight=ft.FontWeight.W_400,),
                                            ft.Divider(thickness=1, height=1),
                                            ft.Column(
                                                [
                                                    ft.Text(text_language[35]),
                                                    ft.Text(text_language[36]),
                                                    ft.Text(text_language[37]),
                                                    ft.Text(text_language[38]),
                                                ],
                                                height=310,
                                                scroll=ft.ScrollMode.AUTO,

                                            ),
                                            ft.Divider(thickness=1, height=1),
                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        content=ft.ElevatedButton(text_language[39], on_click=lambda _: page.window_destroy()),
                                                    ),
                                                ],
                                                alignment=ft.MainAxisAlignment.END
                                            ),
                                        ],
                                        width=540,
                                    ),
                                ],
                            ),
                            padding=ft.Padding(10, 10, 10, 10),
                            width=page.window_width,
                            height=page.window_height,
                        )
                    ]
                )
            )

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = layout
    page.on_view_pop = view_pop
    page.go(page.route)


ft.app(main)
