"""

Options:
 --not_mount_service_ports
                            Use this flag to not mount service ports for given services in the config. This can be
                            useful if the services should only be available within the docker network.
 --pull_always              If given, it will always use 'docker pull' command to pull docker images from specified
                            docker registries."""
import typer

from fastiot.cli.typer_app import app, DEFAULT_CONTEXT_SETTINGS


@app.command('config', context_settings=DEFAULT_CONTEXT_SETTINGS)
def config_cmd(config: str = typer.Argument()):
    """
    This command generates configs. Per default it builds all configs. Optionally, you can specify a config to built
    only a single config. The generated configs will be placed inside the build dir in your project.

    For each config the docker images will be executed to import the manifest.yaml file. Therefore, if you want to build
    one or more configs you have to be logged in and connected to the corresponding docker registries.
    """
    args, left = getopt(argv, "t:r:h", ["tag=", "docker_registry=", "docker_net_name=",
                                        "not_override_configs_with_env_variables", "not_mount_service_ports",
                                        "pull_always", "help"])
    config = None
    if len(left) > 0:
        config = left[-1]
        left = left[:-2]

    if len(left) > 0:
        print(f'Unrecognized program options: "{left.join(", ")}"')
        print(_HELP)
        exit(1)

    if config is not None and config not in make_context.all_config_names:
        config_names = [f"'{name}'" for name in make_context.all_config_names]
        print(f"Config '{config}' is invalid. Valid configs are: {', '.join(config_names)}")
        print(_HELP)
        exit(1)

    is_help = False
    tag = None
    docker_registry = os.getenv(SAM_DOCKER_REGISTRY)
    docker_net_name = _DEFAULT_DOCKER_NET_NAME
    do_override_configs_with_env_variables = True
    do_mount_service_ports = True
    do_pull_always = False
    for arg, option in args:
        if arg == '-h' or arg == '--help':
            is_help = True
        elif arg == '-t' or arg == '--tag':
            tag = option
        elif arg == '-r' or arg == '--docker_registry':
            docker_registry = option
        elif arg == '--docker_net_name':
            docker_net_name = option
        elif arg == '--not_override_configs_with_env_variables':
            do_override_configs_with_env_variables = False
        elif arg == '--not_mount_service_ports':
            do_mount_service_ports = False
        elif arg == '--pull_always':
            do_pull_always = True

    if is_help:
        print(_HELP)
        return

    config_cmd(
        make_context=make_context,
        config=config,
        tag=tag,
        docker_registry=docker_registry,
        docker_net_name=docker_net_name,
        do_override_configs_with_env_variables=do_override_configs_with_env_variables,
        do_mount_service_ports=do_mount_service_ports,
        do_pull_always=do_pull_always
    )


def config_cmd(make_context: MakeContext,
               config: Optional[str] = None,
               tag: Optional[str] = None,
               docker_registry: Optional[str] = None,
               docker_net_name: str = _DEFAULT_DOCKER_NET_NAME,
               do_override_configs_with_env_variables: bool = True,
               do_mount_service_ports: bool = True,
               do_pull_always: bool = False):
    if config is None:
        config_names = make_context.all_config_names
    else:
        config_names = [config]

    for config_name in config_names:
        config = make_context.get_config(
            config_name=config_name,
            docker_registry=docker_registry,
            tag=tag,
            do_override_configs_with_env_variables=do_override_configs_with_env_variables
        )

        output_dir = os.path.join(make_context.generated_root_dir, "configs", config_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        module_manifests: Dict[ModuleManifestId, ModuleManifest] = {}
        for module in config.modules:
            module_manifest_id, module_manifest = make_context.get_manifest_with_module_config(
                module=module,
                do_pull_always=do_pull_always
            )
            module_manifests[module_manifest_id] = module_manifest

        _copy_other_files_to_generated_config(
            make_context=make_context,
            config_name=config_name,
            output_dir=output_dir
        )
        write_docker_compose(
            config_name=config_name,
            config=config,
            output_dir=output_dir,
            docker_net_name=docker_net_name,
            module_manifests=module_manifests,
            do_mount_service_ports=do_mount_service_ports
        )

        if make_context.do_use_generated_py and config_name == make_context.test_config:
            imports_for_test_config_environment_variables = make_context.imports_for_test_config_environment_variables
            generate_test_env(
                output_dir_of_config=output_dir,
                test_environment_name=config_name,
                gen_filename=make_context.generated_py_filename,
                environment=config.environment,
                imports_for_test_config_environment_variables=imports_for_test_config_environment_variables,
                config_dir=config.config_dir
            )

        if config.deployment:
            write_ansible_playbook(config_name=config_name,
                                   config=config.deployment,
                                   output_dir=output_dir)


def _copy_other_files_to_generated_config(make_context: MakeContext, config_name: str, output_dir: str):
    for name in os.listdir(os.path.join(make_context.configs_dir, config_name)):
        if name == sam_compose_filename:
            continue
        src_filename = os.path.join(make_context.configs_dir, config_name, name)
        if os.path.isfile(src_filename):
            dst_filename = os.path.join(output_dir, name)
            copyfile(src_filename, dst_filename)
        elif os.path.isdir(src_filename):
            dst_filename = os.path.join(output_dir, name)
            if os.path.isdir(dst_filename) is True:
                rmtree(dst_filename)
            copytree(src_filename, dst_filename)
