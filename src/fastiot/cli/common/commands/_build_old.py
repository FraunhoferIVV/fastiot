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
