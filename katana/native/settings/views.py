"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

# -*- coding: utf-8 -*-


import os
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from katana.native.settings.settings import Settings
from katana.utils.navigator_util import Navigator
from katana.utils.json_utils import read_json_data
import ast
import json

nav_obj = Navigator()
REF_FILE = os.path.join(
    nav_obj.get_katana_dir(),
    "katana.native",
    "assembler",
    "static",
    "assembler",
    "base_templates",
    "empty.xml",
)
config_json_path = os.path.join(nav_obj.get_katana_dir(), "config.json")

controls = Settings()


def index(request):
    return render(request, "settings/index.html", {"data": controls.get_location()})


def email_setting_handler(request):
    return render(
        request,
        "settings/email_setting_handler.html",
        {"setting": controls.email_setting_handler(request)},
    )


def secret_handler(request):
    return render(
        request, "settings/secret.html", {"secret": controls.secret_handler(request)}
    )


def jira_setting_handler(request):
    return render(
        request,
        "settings/jira_setting_handler.html",
        {"jira": controls.jira_setting_handler(request)},
    )


def general_setting_handler(request):
    return render(
        request,
        "settings/general_setting_handler.html",
        {"data": controls.general_setting_handler(request)},
    )


def profile_setting_handler(request):
    return render(
        request,
        "settings/profile_setting_handler.html",
        {"data": controls.profile_setting_handler(request)},
    )


def smart_analysis_handler(request):
    return render(
        request,
        "settings/smart_analysis_handler.html",
        {"data": controls.smart_analysis_handler(request)},
    )


def prerequisites_handler(request):
    return render(
        request,
        "settings/prerequisites_handler.html",
        {"data": controls.prerequisites_handler(request)},
    )


def install_prerequisite(request):
    return JsonResponse(controls.prereq_installation_handler(request))


def validate_input_repo(request):
    paths_string = request.POST.get("paths")
    paths_list = ast.literal_eval(paths_string)
    in_valid = False
    for i in paths_list:
        if os.path.exists(i):
            in_valid = False
        else:
            in_valid = True
            break
    if in_valid:
        return HttpResponse(1)
    else:
        return HttpResponse(0)


def myajaxtestview(request):
    return HttpResponse(request.POST["text"])


def populate_paths(request):
    test_case_folder = "Testcases"
    suites_folder = "Suites"
    project_folder = "Projects"
    data_folder = "Data"
    config_folder = "Config_files"
    wrapper_folder = "wrapper_files"
    returned_json = read_json_data(config_json_path)
    list_of_files = os.listdir(returned_json["pythonsrcdir"])
    if list_of_files:

        if (
            "warriorspace" not in list_of_files
            and "Warriorspace" not in list_of_files
            and "Projects" not in list_of_files
            and "projects" not in list_of_files
            and "Suites" not in list_of_files
            and "suites" not in list_of_files
            and "Testcases" not in list_of_files
            and "testcases" not in list_of_files
            and "Data" not in list_of_files
            and "data" not in list_of_files
            and "Wrapper_files" not in list_of_files
            and "wrapper_files" not in list_of_files
            and "Config_files" not in list_of_files
            and "config_files" not in list_of_files
        ):
            os.mkdir(returned_json["pythonsrcdir"] + "/Warriorspace")
            sub_folders = {
                "Testcases": "xmldir",
                "Suites": "testsuitedir",
                "Projects": "projdir",
                "Data": "idfdir",
                "Config_files": "testdata",
                "wrapper_files": "testwrapper",
            }
            for folder in [
                "Testcases",
                "Suites",
                "Data",
                "wrapper_files",
                "Config_files",
                "Projects",
            ]:
                os.mkdir(returned_json["pythonsrcdir"] + "/Warriorspace/" + folder)
                returned_json[sub_folders[folder]] = (
                    returned_json["pythonsrcdir"] + "/Warriorspace/" + folder
                )
            with open(config_json_path, "w") as f:
                f.write(json.dumps(returned_json, indent=4))
            return HttpResponse(request)

    if os.path.isdir(returned_json["pythonsrcdir"]):
        if (
            returned_json["pythonsrcdir"].split("/")[-1].lower() == "warriorspace"
            or returned_json["pythonsrcdir"].split("/")[-2].lower() == "warriorspace"
        ):
            child_dirs = os.listdir(returned_json["pythonsrcdir"])
            if "Testcases" in child_dirs:
                test_case_folder = "Testcases"
                returned_json["xmldir"] = returned_json["pythonsrcdir"] + "/Testcases"

            elif "testcases" in child_dirs:
                test_case_folder = "testcases"
                returned_json["xmldir"] = returned_json["pythonsrcdir"] + "/testcases"
            else:
                test_case_folder = "Testcases"
                os.mkdir(returned_json["pythonsrcdir"] + "/Testcases")
                returned_json["xmldir"] = returned_json["pythonsrcdir"] + "/Testcases"

            if "Suites" in child_dirs:
                suites_folder = "Suites"
                returned_json["testsuitedir"] = (
                    returned_json["pythonsrcdir"] + "/Suites"
                )
            elif "suites" in child_dirs:
                suites_folder = "suites"
                returned_json["testsuitedir"] = (
                    returned_json["pythonsrcdir"] + "/suites"
                )
            else:
                suites_folder = "Suites"
                os.mkdir(returned_json["pythonsrcdir"] + "/Suites")
                returned_json["testsuitedir"] = (
                    returned_json["pythonsrcdir"] + "/Suites"
                )

            if "Projects" in child_dirs:
                project_folder = "Projects"
                returned_json["projdir"] = returned_json["pythonsrcdir"] + "/Projects"
            elif "projects" in child_dirs:
                project_folder = "projects"
                returned_json["projdir"] = returned_json["pythonsrcdir"] + "/projects"
            else:
                project_folder = "Projects"
                os.mkdir(returned_json["pythonsrcdir"] + "/Projects")
                returned_json["projdir"] = returned_json["pythonsrcdir"] + "/Projects"

            if "Data" in child_dirs:
                data_folder = "Data"
                returned_json["idfdir"] = returned_json["pythonsrcdir"] + "/Data"
            elif "data" in child_dirs:
                data_folder = "data"
                returned_json["idfdir"] = returned_json["pythonsrcdir"] + "/data"
            else:
                data_folder = "Data"
                os.mkdir(returned_json["pythonsrcdir"] + "/Data")
                returned_json["idfdir"] = returned_json["pythonsrcdir"] + "/Data"

            if "Config_files" in child_dirs:
                config_folder = "Config_files"
                returned_json["testdata"] = (
                    returned_json["pythonsrcdir"] + "/Config_files"
                )
            elif "config_files" in child_dirs:
                config_folder = "config_files"
                returned_json["testdata"] = (
                    returned_json["pythonsrcdir"] + "/config_files"
                )
            else:
                config_folder = "Config_files"
                os.mkdir(returned_json["pythonsrcdir"] + "/Config_files")
                returned_json["testdata"] = (
                    returned_json["pythonsrcdir"] + "/Config_files"
                )

            if "wrapper_files" in child_dirs:
                wrapper_folder = "wrapper_files"
                returned_json["testwrapper"] = (
                    returned_json["pythonsrcdir"] + "/wrapper_files"
                )
            elif "Wrapper_files" in child_dirs:
                wrapper_folder = "Wrapper_files"
                returned_json["testwrapper"] = (
                    returned_json["pythonsrcdir"] + "/Wrapper_files"
                )
            else:
                wrapper_folder = "wrapper_files"
                os.mkdir(returned_json["pythonsrcdir"] + "/wrapper_files")
                returned_json["testwrapper"] = (
                    returned_json["pythonsrcdir"] + "/wrapper_files"
                )
        elif os.listdir(returned_json["pythonsrcdir"]):

            base_tree = os.listdir(returned_json["pythonsrcdir"])
            for element in base_tree:
                if element == "warriorspace":
                    warrior_path = "/warriorspace"
                elif element == "Warriorspace":
                    warrior_path = "/Warriorspace"
            if "warriorspace" in [x.lower() for x in base_tree]:
                child_dirs = os.listdir(returned_json["pythonsrcdir"]+ "/" + warrior_path)

                if "Testcases" in child_dirs:
                    test_case_folder = "Testcases"
                    returned_json["xmldir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Testcases"
                    )

                elif "testcases" in child_dirs:
                    test_case_folder = "testcases"
                    returned_json["xmldir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/testcases"
                    )
                else:
                    test_case_folder = "Testcases"
                    if not os.path.exists(
                        returned_json["pythonsrcdir"] + warrior_path + "/Testcases"
                    ):
                        os.mkdir(
                            returned_json["pythonsrcdir"] + warrior_path + "/Testcases"
                        )
                    returned_json["xmldir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Testcases"
                    )

                if "Suites" in child_dirs:
                    suites_folder = "Suites"
                    returned_json["testsuitedir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Suites"
                    )
                elif "suites" in child_dirs:
                    suites_folder = "suites"
                    returned_json["testsuitedir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/suites"
                    )
                else:
                    suites_folder = "Suites"
                    if not os.path.exists(
                        returned_json["pythonsrcdir"] + warrior_path + "/Suites"
                    ):
                        os.mkdir(
                            returned_json["pythonsrcdir"] + warrior_path + "/Suites"
                        )
                    returned_json["testsuitedir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Suites"
                    )

                if "Projects" in child_dirs:
                    project_folder = "Projects"
                    returned_json["projdir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Projects"
                    )
                elif "projects" in child_dirs:
                    project_folder = "projects"
                    returned_json["projdir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/projects"
                    )
                else:
                    project_folder = "Projects"
                    if not os.path.exists(
                        returned_json["pythonsrcdir"] + warrior_path + "/Projects"
                    ):
                        os.mkdir(
                            returned_json["pythonsrcdir"] + warrior_path + "/Projects"
                        )
                    returned_json["projdir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Projects"
                    )

                if "Data" in child_dirs:
                    data_folder = "Data"
                    returned_json["idfdir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Data"
                    )
                elif "data" in child_dirs:
                    data_folder = "data"
                    returned_json["idfdir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/data"
                    )
                else:
                    data_folder = "Data"
                    if not os.path.exists(
                        returned_json["pythonsrcdir"] + warrior_path + "/Data"
                    ):
                        os.mkdir(returned_json["pythonsrcdir"] + warrior_path + "/Data")
                    returned_json["idfdir"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Data"
                    )

                if "Config_files" in child_dirs:
                    config_folder = "Config_files"
                    returned_json["testdata"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Config_files"
                    )
                elif "config_files" in child_dirs:
                    config_folder = "config_files"
                    returned_json["testdata"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/config_files"
                    )
                else:
                    config_folder = "Config_files"
                    if not os.path.exists(
                        returned_json["pythonsrcdir"] + warrior_path + "/Config_files"
                    ):
                        os.mkdir(
                            returned_json["pythonsrcdir"]
                            + warrior_path
                            + "/Config_files"
                        )
                    returned_json["testdata"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Config_files"
                    )

                if "wrapper_files" in child_dirs:
                    wrapper_folder = "wrapper_files"
                    returned_json["testwrapper"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/wrapper_files"
                    )
                elif "Wrapper_files" in child_dirs:
                    wrapper_folder = "Wrapper_files"
                    returned_json["testwrapper"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/Wrapper_files"
                    )
                else:
                    wrapper_folder = "wrapper_files"
                    if not os.path.exists(
                        returned_json["pythonsrcdir"] + warrior_path + "/wrapper_files"
                    ):
                        os.mkdir(
                            returned_json["pythonsrcdir"]
                            + warrior_path
                            + "/wrapper_files"
                        )
                    returned_json["testwrapper"] = (
                        returned_json["pythonsrcdir"] + warrior_path + "/wrapper_files"
                    )
            else:

                if "Testcases" in base_tree:
                    test_case_folder = "Testcases"

                elif "testcases" in base_tree:
                    test_case_folder = "testcases"

                if "Suites" in base_tree:
                    suites_folder = "Suites"

                elif "suites" in base_tree:
                    suites_folder = "suites"

                if "Projects" in base_tree:
                    project_folder = "Projects"

                elif "projects" in base_tree:
                    project_folder = "projects"

                if "Data" in base_tree:
                    data_folder = "Data"

                elif "data" in base_tree:
                    data_folder = "data"

                if "Config_files" in base_tree:
                    config_folder = "Config_files"

                elif "config_files" in base_tree:
                    config_folder = "config_files"

                if "wrapper_files" in base_tree:
                    wrapper_folder = "wrapper_files"

                elif "Wrapper_files" in base_tree:
                    wrapper_folder = "Wrapper_files"

                sub_folders = {
                    test_case_folder: "xmldir",
                    suites_folder: "testsuitedir",
                    project_folder: "projdir",
                    data_folder: "idfdir",
                    config_folder: "testdata",
                    wrapper_folder: "testwrapper",
                }
                list_of_keys = list(sub_folders.keys())
                for folder in list_of_keys:
                    try:
                        os.mkdir(returned_json["pythonsrcdir"] + "/" + folder)
                        returned_json[sub_folders[folder]] = (
                            returned_json["pythonsrcdir"] + "/" + folder
                        )
                    except FileExistsError:
                        returned_json[sub_folders[folder]] = (
                            returned_json["pythonsrcdir"] + "/" + folder
                        )
        else:
            os.mkdir(returned_json["pythonsrcdir"] + "/Warriorspace")
            sub_folders = {
                "Testcases": "xmldir",
                "Suites": "testsuitedir",
                "Projects": "projdir",
                "Data": "idfdir",
                "Config_files": "testdata",
                "wrapper_files": "testwrapper",
            }
            for folder in [
                "Testcases",
                "Suites",
                "Data",
                "wrapper_files",
                "Config_files",
                "Projects",
            ]:
                os.mkdir(returned_json["pythonsrcdir"] + "/Warriorspace/" + folder)
                returned_json[sub_folders[folder]] = (
                    returned_json["pythonsrcdir"] + "/Warriorspace/" + folder
                )

    with open(config_json_path, "w") as f:
        f.write(json.dumps(returned_json, indent=4))
    return HttpResponse(request)
