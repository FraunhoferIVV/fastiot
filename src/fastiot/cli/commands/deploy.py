""" Command for automatic deployments using ansible playbooks """
import logging
import os
from typing import Optional, List

import jinja2
import typer

from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR
from fastiot.cli.helper_fn import get_jinja_env
from fastiot.cli.model.project import ProjectContext
from fastiot.cli.typer_app import DEFAULT_CONTEXT_SETTINGS, app


def _deployment_completion(*_) -> List[str]:
    return ProjectContext.default.deployment_names


@app.command(context_settings=DEFAULT_CONTEXT_SETTINGS)
def deploy(deployments: Optional[List[str]] = typer.Argument(default=None, shell_complete=_deployment_completion,
                                                             help="Select the deployments to deploy"),
           ask_pass: bool = typer.Option(False, '--ask-pass', '-k', help="Use password instead of SSH publickey to connect to targets"),
           dry: bool = typer.Option(False, help="Only create playbooks but do not run actual deployment.")):
    """
    This command handles deployment of a config using an Ansible Playbook if you have configured any deployments based
    on :class:`fastiot.cli.model.deployment.DeploymentTargetSetup` in your :file:`deployment.yaml`. """
    context = ProjectContext.default

    if not deployments:
        deployments = []

    for deployment_name in deployments:
        if deployment_name not in context.deployment_names:
            typer.echo(f"Deployment {deployment_name} not in project deployments.")
            raise typer.Exit(code=1)

    for deployment_name in deployments:
        deployment = context.deployment_by_name(deployment_name)
        if deployment.deployment_target is None:
            typer.echo(f"Deployment {deployment_name} does not have a deployment_target configured.")
            raise typer.Exit(code=2)

        _write_ansible_playbook(deployment_name, deployment)

        if not dry:
            ask_pass = "-k" if ask_pass else ""
            os.system(f"cd {context.build_dir}/{DEPLOYMENTS_CONFIG_DIR}/{deployment_name};"
                      f"ansible-playbook {ask_pass} -i hosts --diff ansible-playbook.yaml")


def _write_ansible_playbook(deployment_name, deployment):
    """ Creates the actual playbook and inventory files"""
    context = ProjectContext.default
    output_dir = os.path.join(context.project_root_dir, context.build_dir, DEPLOYMENTS_CONFIG_DIR,
                              deployment_name)

    os.makedirs(output_dir, exist_ok=True)

    try:
        jinja_env = get_jinja_env()
        playbook_template = jinja_env.get_template('ansible-playbook.yaml.template')

        playbook_document = playbook_template.render(deployment_name=deployment_name,
                                                     deployment_target=deployment.deployment_target)

        with open(os.path.join(output_dir, "ansible-playbook.yaml"), "w") as playbook_file:
            playbook_file.write(playbook_document)

        jinja_env = get_jinja_env()
        inventory_template = jinja_env.get_template('ansible_hosts.template')
        inventory_document = inventory_template.render(deployment_target=deployment.deployment_target)

        with open(os.path.join(output_dir, "hosts"), "w") as inventory_file:
            inventory_file.write(inventory_document)

    except jinja2.exceptions.UndefinedError:
        logging.exception('Exception raised during transpiling of playbook %s', deployment_name)
