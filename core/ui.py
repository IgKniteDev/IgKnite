# SPDX-License-Identifier: MIT


# Imports.
import random
from typing import Self
import logging

import disnake
from disnake.ui.item import Item


# Set up logging.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Overwrite disnake.Embed class to form custom embeds.
class TypicalEmbed(disnake.Embed):
    """
    Represents an embed common to all the normal commands.
    """

    def __init__(
        self,
        *args,
        inter: disnake.CommandInter | None = None,
        disabled_footer: bool = False,
        is_error: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
            color=(2764081 if not is_error else 16608388),
        )

        if not disabled_footer and inter:
            self.set_footer(
                text=random.choice(
                    [
                        'When pigs fly...',
                        'Stunned stork!',
                        "A perfect debugged life doesn't exist.",
                        "Haven't I made it obvious?",
                        'Hello World, from the other side!',
                        'A computer is like air conditioning'
                        + '- it becomes useless when you open Windows.',
                        'Life is like a sine wave.',
                    ]
                ),
                icon_url=inter.author.avatar,
            )


# Overwrite disnake.ui.View class to form custom views.
class SmallView(disnake.ui.View):
    """
    Can be used for simple views with buttons.
    """

    def __init__(
        self, inter: disnake.CommandInter | None = None, *, timeout: float = 60
    ) -> None:
        super().__init__(timeout=timeout)
        self.inter = inter

    def add_button(
        self,
        *,
        label: str,
        url: str | None = None,
        style: disnake.ButtonStyle = disnake.ButtonStyle.gray,
        disabled: bool = False,
    ) -> Self:
        """
        Adds a button to the view.
        """

        self.add_item(
            disnake.ui.Button(
                label=label, url=url, style=style, disabled=disabled
            )
        )
        return self
    
    # async def disable_button(self,inter: disnake.CommandInter) -> None:
    #     """disables the button in the view
    #     """
        
    #     #check if interacted user is the author of the message
    #     logger.info(f"Interacted user: {inter.author}")

    #     if self.inter.author == inter.author:
    #         for child in self.children:
    #             if child.style != disnake.ButtonStyle.link:
    #                 child.disabled = True

    #         await inter.edit_original_message(view=self)
    #         logger.info("Button disabled")
        


    async def on_timeout(self) -> None:
        if self.inter:
            for child in self.children:
                if child.style != disnake.ButtonStyle.link:
                    child.disabled = True

            await self.inter.edit_original_message(view=self)


    # async def on_error(self, error: Exception, item: Item, interaction: disnake.MessageInteraction) -> None:
    #     logger.error(f"Error in button click: {error}")
    #     return await super().on_error(error, item, interaction)
        


