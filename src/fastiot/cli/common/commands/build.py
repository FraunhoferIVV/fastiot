"""
Usage: fastcli build [<options>] [<module>]

This command builds images.

Per default it builds all images. Optionally, you can specify a single image to build.

If you want to use experimental features like platform tag, use the flag -e to indicate it.

Options:

 -h, --help                 Print help
"""
from typing import List

from fastiot.cli.configuration.command import Command
from fastiot.cli.configuration.context import Context
from fastiot.cli.typer_app import app


class BuildCommand(Command):
    @property
    def name(self) -> str:
        return 'build'

    def execute(self, context: Context, vargs: List[str]):
        pass

    def print_help(self, context: Context):
        print(__file__.__docs__)


 -m <mode>, --mode=<mode>   The build mode for docker images. Can be 'debug' (default) or 'release'. No compilation of
                            python code will happen if chosen 'debug'. Nuitka compilation will be applied if chosen
                            'release'.
 -e, --experimental         Enable experimental features.
 -t <list(tag1,tag2,...,tagn)>, --tag=<list(tag1,tag2,...,tagn)>
                            The tags to use for building as a comma ',' separated list. Defaults to 'latest'.
 -r <docker_registry>, --docker_registry=<docker_registry>
                            The docker registry to be used for tagging. If docker_registry is unspecified, it will look
                            for a process environment variable SAM_DOCKER_REGISTRY. If docker registry is not empty,
                            the built image names will begin with the docker registry followed by a slash.
 -c <docker_registry_cache>, --docker_registry_cache=<docker_registry_cache>
                            Experimental feature. The docker registry cache. If docker registry cache is unspecified and
                            buildx is used, it will look for a process environment variable SAM_DOCKER_REGISTRY_CACHE.
                            If docker registry cache is not empty, it will use it as a cache for intermediate image
                            layers.
 -p <list(amd64,arm64,armv6,armv7)>, --platform=<list(amd64,arm64,armv6,armv7)>
                            Experimental feature. The platform to compile for given as a comma ',' separated list.
                            Possible values are 'amd64', 'arm64', 'armv6' and 'armv7'. Currently, it is only supported
                            in combination with the '--push' flag. Per default, the platform of the current OS
                            is used. If multiple platforms are specified, they will be included into the resulting
                            image.
                            It will also look in the manifest.yaml and check if each module can be built for the
                            selected platform. If not, the platform builds will be skipped where unspecified. If nothing
                            can be built, it will exit with 2.
 --push                     Experimental feature. Instead of using --load for buildx, it uses --push which outputs the
                            image to a registry. Push is only allowed if a docker registry is specified. Additionally,
                            if a docker registry cache is used, it will also push intermediate image layers.
 -d, --dry                  Instead of building, it will print the content of the dockerfile to stdout. If using this
                            flag, it is required to specify a module.

@app.command()
def build():
    pass


def build_default_module(project_root_dir: str,
                         project_namespace: str,
                         module_package_name: str,
                         module_name: str,
                         tags: List[str],
                         docker_registry_prefix: str,
                         docker_registry_cache_prefix: str,
                         extra_pypi: str,
                         enable_experimental: bool,
                         use_push: bool,
                         use_dry: bool,
                         platforms: List[str],
                         cache_name: str,
                         extra_caches: List[str],
                         healthcheck: str,
                         debug_flag: bool,
                         library_package: str,
                         library_setup_py_dir: str,
                         module_dirs_to_copy: List[str] = (),
                         vue: Optional[Vue] = None):
    with tempfile.TemporaryDirectory() as temp_dict:
        dockerfilename = os.path.join(temp_dict, "Dockerfile")
        with open(dockerfilename, "w") as temp_dockerfile:
            dockerfile_template = get_jinja_env().get_template('Dockerfile.template')
            temp_dockerfile.write(dockerfile_template.render(
                project_root_dir=project_root_dir,
                module_package_name=module_package_name,
                module_name=module_name,
                extra_pypi=extra_pypi,
                healthcheck=healthcheck,
                module_dirs_to_copy=module_dirs_to_copy,
                library_package=library_package,
                library_setup_py_dir=library_setup_py_dir,
                vue=vue,
            ))

        if use_dry is False:
            docker_cmd = _get_docker_cmd(
                project_namespace=project_namespace,
                module_name=module_name,
                tags=tags,
                docker_registry_prefix=docker_registry_prefix,
                docker_registry_cache_prefix=docker_registry_cache_prefix,
                enable_experimental=enable_experimental,
                use_push=use_push,
                platforms=platforms,
                cache_name=cache_name,
                extra_caches=extra_caches
            )
            docker_cmd.extend([
                "-f", f"{temp_dockerfile.name}"
            ])
            if debug_flag is True:
                docker_cmd.append(f"--target=debug")
            docker_cmd.append('.')
            docker_cmd = ' '.join(docker_cmd)
            _execute_docker_cmd(docker_cmd=docker_cmd, workdir=project_root_dir)
        else:
            with open(dockerfilename, "r") as file:
                print(file.read())


def build_custom_module(project_namespace: str,
                        module_name: str,
                        tags: List[str],
                        docker_registry_prefix: str,
                        docker_registry_cache_prefix: str,
                        enable_experimental: bool,
                        use_push: bool,
                        use_dry: bool,
                        platforms: List[str],
                        cache_name: str,
                        extra_caches: List[str],
                        workdir: str,
                        dockerfile: str,
                        use_debug_target: bool):
    docker_cmd = _get_docker_cmd(
        project_namespace=project_namespace,
        module_name=module_name,
        tags=tags,
        docker_registry_prefix=docker_registry_prefix,
        docker_registry_cache_prefix=docker_registry_cache_prefix,
        enable_experimental=enable_experimental,
        use_push=use_push,
        platforms=platforms,
        cache_name=cache_name,
        extra_caches=extra_caches
    )
    docker_cmd.append(f"-f {dockerfile}")
    if use_debug_target is True:
        docker_cmd.append(f"--target=debug")
    docker_cmd.append(f".")
    docker_cmd = ' '.join(docker_cmd)
    if use_dry is False:
        _execute_docker_cmd(docker_cmd=docker_cmd, workdir=workdir)
    else:
        with open(os.path.join(workdir, dockerfile), "r") as file:
            print(file.read())


def _get_docker_cmd(project_namespace: str,
                    module_name: str,
                    tags: List[str],
                    docker_registry_prefix: str,
                    docker_registry_cache_prefix: str,
                    enable_experimental: bool,
                    use_push: bool,
                    platforms: List[str],
                    cache_name: str,
                    extra_caches: List[str],) -> List[str]:
    if enable_experimental:
        docker_cmd = [
            "DOCKER_CLI_EXPERIMENTAL=enabled",
            "DOCKER_BUILDKIT=1",
            "docker",
            "buildx",
            "build",
            f"--platform {','.join(platforms)}",
            "--push" if use_push else "--load",
            "--progress plain"
        ]

        if not use_push:
            docker_cmd.append(f"--cache-from=type=local,src={local_docker_cache}")
            docker_cmd.append(f"--cache-to=type=local,dest={local_docker_cache},mode=max")

        if docker_registry_cache_prefix:
            current_caches = set()
            if cache_name:
                for i_tag, tag in enumerate(tags):
                    fully_specified_cache_name = f"{docker_registry_cache_prefix}{cache_name}:{tag}"
                    current_caches.add(fully_specified_cache_name)
                    docker_cmd.append(f"--cache-from=type=registry,ref={fully_specified_cache_name}")
                    if use_push and i_tag == 0:  # currently only one cache-to registry is allowed
                        docker_cmd.append(f"--cache-to=type=registry,ref={fully_specified_cache_name},mode=max")

            for extra_cache in extra_caches:
                if extra_cache not in current_caches:
                    fully_specified_cache_name = f"{docker_registry_cache_prefix}{extra_cache}"
                    docker_cmd.append(f"--cache-from=type=registry,ref={fully_specified_cache_name}")
                    current_caches.add(fully_specified_cache_name)

    else:
        docker_cmd = [
            "DOCKER_BUILDKIT=1",
            "docker",
            "build",
            "--progress plain"
        ]
    for tag in tags:
        docker_cmd.append(f"--tag={docker_registry_prefix}{project_namespace}_{module_name}:{tag}")
    return docker_cmd


def _execute_docker_cmd(docker_cmd: str, workdir: str):
    get_buildtools_logger().info(f"Docker build command: {docker_cmd}")
    ret = os.system(f"cd {workdir}; {docker_cmd}")
    if ret != 0:
        raise RuntimeError("Docker build command exited with none-zero code.")
