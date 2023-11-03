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
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.db import IntegrityError
from django.db.models.functions import Lower
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import vmmanage.models
from uptomate.Deployment import (
    VAGRANT_RUNNING_STATES,
    VAGRANT_STOPPED_STATES
)
from . import deploy_controller
from . import forms
from . import models

_INSTALL_MSGS = {
    'formerror': _("The submitted form was invalid!"),
    'invalidconfig': _("The problem's config is invalid!"),
    'missingkey': _("The problem's config is missing a mandatory field."),
    'success': _("The problem is getting installed, this may take a while."),
    'exists': _("A problem with that slug is already installed!")
}


def start_used_vms(vms=None):
    deploy_controller.vm_action_on_states(settings.DEFAULT_USED_ACTION, VAGRANT_STOPPED_STATES, vms)


def stop_unused_vms(vms):
    # Check if really unused
    unused_vms = []
    for vm in vms:
        if not vm.problem.courseproblems_set.exists():
            unused_vms.append(vm)
    if unused_vms:
        deploy_controller.vm_action_on_states(settings.DEFAULT_UNUSED_ACTION, VAGRANT_RUNNING_STATES, unused_vms)


def stop_unused_problems(problems):
    vms = []
    for problem in problems:
        if problem.vm:
            vms.append(problem.vm)
    stop_unused_vms(vms)


def _run_task_on_existing_vm(action, problem_slug, **kwargs):
    vm = get_object_or_404(models.VirtualMachine, problem__slug=problem_slug)
    return deploy_controller.run_on_existing(action, vm, **kwargs)



# TODO: Make nicer, enhance usability in case of F-5s and get param
@permission_required("can_manage_vm")
def show_installable_problems(request):
    problems = deploy_controller.find_installable_problems()
    msgs = []
    if not problems:
        msgs.append(_("No problems are available for installation"))

    _msg = request.GET.get("m", "")
    if _msg:
        msgs.append(_INSTALL_MSGS[_msg])

    return render(
        request,
        "vms/installable.html",
        {
            "problems": problems,
            "vagrant_form": forms.VagrantFilesForm(),
            "errors": msgs,
        }
    )


@permission_required("can_manage_vm")
def problem_destroy(request, problem_slug):
    problem = get_object_or_404(models.Problem, slug=problem_slug)
    if request.POST:
        deploy_controller.destroy_problem(problem)
        return redirect('vmmanage_show_problems')
    return render(
        request,
        "vms/destroy_submission.html",
        {
            "problem": problem,
        }
    )


@permission_required("can_manage_vm")
def install_problem(request):
    if not request.POST:
        return redirect('vmmanage_show_installable')
    form = forms.VagrantFilesForm(request.POST)
    if form.is_valid():
        vagr_name = form.cleaned_data['vagrant_file']
        problem_name = request.POST['problem']
        try:
            deploy_controller.create_problem(problem_name, vagr_name)
        except (OSError, IntegrityError) as ex:
            print(ex)
            return redirect(reverse('vmmanage_show_installable') + '?m=exists')
        except ValueError as ex:
            return redirect(reverse('vmmanage_show_installable') + '?m=invalidconfig')
        except KeyError:
            return redirect(reverse('vmmanage_show_installable') + "?m=missingkey")
    else:
        return redirect(reverse('vmmanage_show_installable') + '?m=formerror')

    return redirect(
        reverse('vmmanage_show_installable') + '?m=success'
    )

@permission_required("can_manage_vm")
def problem_overview(request):
    return render(
        request,
        "vms/overview.html",
        {
            "problems": models.Problem.objects.all().order_by(Lower("name"))
        }
    )


@permission_required("can_manage_vm")
def perform_action(request, problem_slug, action_name):
    try:
        _run_task_on_existing_vm(action_name, problem_slug)
    except deploy_controller.IllegalAction as ex:
        return HttpResponseNotAllowed(str(ex))
    return redirect(
        'vmmanage_detail_problem',
        problem_slug=problem_slug
    )


@permission_required("can_manage_vm")
def problem_detail(request, problem_slug):
    return render(
        request,
        "vms/detail.html",
        {
            "problem": get_object_or_404(models.Problem,
                                         slug=problem_slug),
            "actions": vmmanage.models.LEGAL_API_VM_ACTIONS
        }
    )


@permission_required("can_manage_vm")
def edit_problem(request, problem_slug):
    problem = get_object_or_404(models.Problem, slug=problem_slug)

    if request.POST:
        form = forms.ProblemEditForm(request.POST,
                                     instance=problem)
        if form.is_valid():
            form.save()
    else:
        form = forms.ProblemEditForm(instance=problem)

    return render(
        request,
        "vms/edit.html",
        {
            "problem": problem,
            "form": form
        }
    )
