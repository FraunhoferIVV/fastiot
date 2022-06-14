from fastiot.cli.configuration.plugin import Plugin


def provide_plugin() -> Plugin:
    return Plugin(
        commands=[
            Build
        ]
    )
