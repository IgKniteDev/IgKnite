from pkgutil import walk_packages

EXTENTIONS = set(
    module.name for module in walk_packages(__path__, f'{__package__}.')
)
