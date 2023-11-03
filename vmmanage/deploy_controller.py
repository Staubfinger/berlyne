# Berlyne IT security trainings platform
# Copyright (C) 2016 Ruben Gonzalez <rg@ht11.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from glob import glob
import os
from os import path

from django.conf import settings

from uptomate import Deployment
from . import models
from . import tasks
from .models import (
    vagr_factory,
    FLAG_FILE_NAME,
    LEGAL_API_VM_ACTIONS
)

__AVAIL_VAGR_FILES = []


class IllegalAction(ValueError):
    pass


def get_avail_vagrant_files():
    return __AVAIL_VAGR_FILES


def install_deployment(vagr_depl: Deployment.Vagrant, vm):
    if isinstance(vm, str):
        vm = models.VirtualMachine.objects.get(slug=vm)

    # vagr_depl.set_ports(vm.get_port_list())
    # with vagr_depl.open_content_file(FLAG_FILE_NAME) as f:
    #     f.write(vm.problem.flag)


def _install_deployment_callback(vagr_depl, f, vm_db, **kwargs):
    install_deployment(vagr_depl, vm_db)


def create_problem(problem_path, vagrant_name):
    vagr = vagr_factory(problem_path)

    # Set name as work around, so unique contraint is not violated
    # in case two VMs get created at the same time
    # This raises an IntegretyError if the problem slug already exists
    problem = models.Problem.create(path=problem_path, config=vagr.get_config())
    vm = problem.vm

    if vm:
        t = tasks.run_on_vagr(
            vagr,
            'install',
            vm,
            _install_deployment_callback,
        )

        vm.add_task(t, 'install')
    return problem


def destroy_problem(problem):
    return tasks.destroy_problem(problem)


def _task_from_path(action, vm_path, vm_db=None, **kwargs):
    vagr = vagr_factory(vm_path)
    return tasks.run_on_vagr(vagr, action, vm_db, **kwargs)


def run_on_existing(action, vm_obj, **kwargs):
    if action not in LEGAL_API_VM_ACTIONS:
        raise IllegalAction("Illegal action '{}'".format(action))
    t = _task_from_path(action, vm_obj.problem.path, vm_obj, **kwargs)
    vm_obj.add_task(t, action)
    return t


def _find_directories_with_file(start_directory, file_name):
    docker_compose_directories = []

    for root, dirs, files in os.walk(start_directory):
        if file_name in files:
            docker_compose_directories.append(root)

    return docker_compose_directories


# Todo: make cheaper
def find_installable_problems():
    problems = []
    existing_paths = models.Problem.objects.all().values_list('path', flat=True)
    for task_dir in _find_directories_with_file(
            settings.PROBLEM_DEPLOYMENT_PATH,
            Deployment.CONFIG_FILE_NAME
    ):
        # We work with relative paths within the problem dir
        task_dir = os.path.relpath(
            task_dir,
            settings.PROBLEM_DEPLOYMENT_PATH
        )

        if task_dir not in existing_paths:
            problems.append(task_dir)

    return problems


def action_on_state(vms, action, states, **action_kwargs):
    for vm in vms:
        predicted_state = vm.predict_state()
        if predicted_state == Deployment.VAGRANT_UNKNOWN or \
                        predicted_state in states:
            run_on_existing(action, vm, **action_kwargs)


def vm_action_on_states(action, states, vms=None):
    """
    Iterate over VMs and apply an action to the ones, that are
    PREDICTED to be in one of the given states after finishing
    their TaskQueue.
    This is done asynchronously.
    :param vms: VMs to iterate over, if None, all VMs will be used instead
    :param action: action to apply
    :param states: states the VM should be in to apply action.
    :return: task object
    """
    if vms is None:
        vms = models.VirtualMachine.objects.all()
    action_on_state(vms, action, states)