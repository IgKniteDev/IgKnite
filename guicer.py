'''
The GUI tool for configuring IgKnite!
---

MIT License

Copyright (c) 2022 IgKnite

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


# Imports.
import os

import flet
from flet import Page, Text, TextField, UserControl, Column, IconButton, Row


# The App class for setting up the UI.
class App(UserControl):
    def build(self) -> Column:
        self.bot_token = TextField(
            hint_text='Enter your bot token'
        )
        self.owner_id = TextField(
            hint_text='Enter your Discord user ID'
        )
        self.spotify_client_secret = TextField(
            hint_text='Enter your Spotify client secret'
        )
        self.spotify_client_id = TextField(
            hint_text='Enter your Spotify client ID'
        )
        self.error_viewer = Text(
            value='Please fill in all the text fields!',
            color='red',
            visible=False
        )
        self.success_viewer = Text(
            value='Successfully Generated Config Files for IgKnite! You\'re good to go :)',
            color='green',
            visible=False
        )

        return Column(
            width=400,
            controls=[
                Row([Text(value='Guicer', style='headlineMedium')], alignment='center'),
                Text(value='Bot Token', size=20),
                self.bot_token,
                Text(value='Owner ID', size=20),
                self.owner_id,
                Text(value='Spotify Client Secet', size=20),
                self.spotify_client_secret,
                Text(value='Spotify Client ID', size=20),
                self.spotify_client_id,
                IconButton(icon='check', bgcolor='white', icon_color='black', on_click=self.generate_config),
                self.error_viewer,
                self.success_viewer,
            ]
        )

    def generate_config(self, _) -> None:
        if (
            len(self.bot_token.value) == 0
            or len(self.owner_id.value) == 0
            or len(self.spotify_client_id.value) == 0
            or len(self.spotify_client_secret.value) == 0
        ):
            self.error_viewer.visible = True

        else:
            here = os.path.join(os.getcwd(), '.env')
            write_mode = 'w' if os.path.exists(here) else 'x'

            with open(here, write_mode) as f:
                f.write(f'''DISCORD_TOKEN={self.bot_token.value}\nDISCORD_OWNER_ID={self.owner_id.value}
SPOTIFY_CLIENT_SECRET={self.spotify_client_secret.value}
SPOTIFY_CLIENT_ID={self.spotify_client_id.value}''')
                self.success_viewer.visible = True
                self.update()

        self.update()


# The main entry point for Guicer's UI.
def main(page: Page) -> None:
    page.window_height = 700
    page.window_width = 600
    page.title = 'Guicer'

    page.horizontal_alignment = 'center'
    app = App()
    page.add(app)


# Run app.
flet.app(target=main)
