from typing import List, Optional

from pydantic.main import BaseModel


class ModulePackageConfig(BaseModel):
    """
    Definition of modules via a package name and a list of modules inside the package. Modules, which are not specified
    in the list, but are in the package are ignored.
    """
    package_name: str
    """The package name of the modules"""
    module_names: List[str]
    """The module names as a list of strings"""
    cache_name: str = ''
    """
    The name to use as the cache. If empty, no cache is used for building. It will use the first given tag for building 
    to append it and also use the docker registry cache as a prefix. So you only need to specify the base name. 
    Example: mypackage-cache
    """
    extra_caches: Optional[List[str]] = None
    """
    A list of extra caches used to speed up building. It is intended if you want to read from other caches or different 
    tags. Each extra cache must match a cache name extended by ':' followed by the tag for the cache. Per default no
    extra caches are used. You might find it useful to always include the cache name of the current module package 
    followed by tag latest to always use latest cache for feature branches.
    Examples: mypackage-cache:latest, sam-cache:latest, sam-cache:mybranch
    """

    def __post_init__(self):
        if self.extra_caches is None:
            self.extra_caches = []




class ProjectConfiguration(BaseModel):
    """ This class holds all variables reade from :file:`configure.py` in the project root directory. """

    project_root_dir: str
    project_namespace: str
    library_package: Optional[str]
    library_setup_py_dir: Optional[str] = None
    module_packages: Optional[List[ModulePackageConfig]] = None
    deploy_configs: List[str]
    test_config: Optional[str]
    test_package: Optional[str]
    imports_for_test_config_environment_variables: Optional[List[str]] = None
    npm_test_dir: Optional[str] = None
