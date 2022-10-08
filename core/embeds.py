'''
Predefined embeds to use across scripts.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import random
import disnake


# Overwrite disnake.Embed class to form custom embeds.
class TypicalEmbed(disnake.Embed):
    '''
    Represents an embed common to all the normal commands.
    '''

    def __init__(
        self,
        inter: disnake.CommandInteraction,
        is_error: bool = False
    ) -> None:
        super().__init__(
            color=(3158326 if not is_error else 16608388)
        )

        self.set_footer(
            text=random.choice(
                [
                    'When pigs fly...',
                    'Stunned stork!',
                    'A perfect debugged life doesn\'t exist.',
                    'Haven\'t I made it obvious?',
                    'Hello World, from the other side!'
                ]
            ),
            icon_url=inter.author.avatar
        )

    def set_title(self, value: str) -> None:
        '''
        Sets the title for the embed content.
        '''
        self.title = value
        return self

    def set_description(self, value: str) -> None:
        '''
        Sets the description for the embed content.
        '''
        self.description = value
        return self
