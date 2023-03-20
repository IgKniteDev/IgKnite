'''
Predefined embeds to use across scripts.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import random
from typing import Self

import disnake


# Overwrite disnake.Embed class to form custom embeds.
class TypicalEmbed(disnake.Embed):
    '''
    Represents an embed common to all the normal commands.
    '''

    def __init__(
        self,
        inter: disnake.CommandInteraction | None = None,
        *,
        disabled_footer: bool = False,
        is_error: bool = False
    ) -> None:
        super().__init__(color=(2764081 if not is_error else 16608388))

        if not disabled_footer and inter:
            self.set_footer(
                text=random.choice(
                    [
                        'When pigs fly...',
                        'Stunned stork!',
                        'A perfect debugged life doesn\'t exist.',
                        'Haven\'t I made it obvious?',
                        'Hello World, from the other side!',
                        'A computer is like air conditioning'
                        + '- it becomes useless when you open Windows.',
                        'Life is like a sine wave.',
                    ]
                ),
                icon_url=inter.author.avatar,
            )

    def set_title(self, value: str) -> Self:
        '''
        Sets the title for the embed.
        '''
        self.title = value
        return self

    def set_description(self, value: str) -> Self:
        '''
        Sets the description for the embed.
        '''
        self.description = value
        return self


# Overwrite disnake.ui.View class to form custom views.
class SmallView(disnake.ui.View):
    '''
    Can be used for simple views with buttons.
    '''

    def __init__(
        self, inter: disnake.CommandInteraction | None = None, *, timeout: float = 60
    ) -> None:
        super().__init__(timeout=timeout)
        self.inter = inter

    def add_button(
        self,
        *,
        label: str,
        url: str | None = None,
        style: disnake.ButtonStyle = disnake.ButtonStyle.gray,
        disabled: bool = False
    ) -> Self:
        '''
        Adds a button to the view.
        '''

        self.add_item(disnake.ui.Button(label=label, url=url, style=style, disabled=disabled))
        return self

    async def on_timeout(self) -> None:
        if self.inter:
            for children in self.children:
                if children.style != disnake.ButtonStyle.link:
                    children.disabled = True

            await self.inter.edit_original_message(view=self)
