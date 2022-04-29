def main():
    context = _import_configuration()
    commands = _import_extensions(context=context)
    # execute command


def _import_configuration():
    try:
        import configure
    except ImportError:
        pass


def _import_extensions(context) -> commands:
    plugins = []
    for ext in extensions:
        try:
            a = importlib.load('ext')
            plugins.append(a.provide_plugin())
        except ImportError:
            pass

    commands = {}
    for plugin in plugins:
        commands.update(plugin.commands)


if __name__ == '__main__':
    # entry point for fastiot command
    main()
