'''
Copyright 2017, Fujitsu Network Communications, Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import os
import shutil
import json
import sys
import select
import base64
import zipfile
from termcolor import colored
from os.path import abspath, dirname
from git import Repo

try:
    import katana

# except ModuleNotFoundError as error:
except:
    WARRIORDIR = dirname(dirname(abspath(__file__)))
    sys.path.append(WARRIORDIR)
    try:
        import katana
    except:
        raise
from katana.utils.navigator_util import Navigator
from katana.utils.json_utils import read_json_data
from datetime import datetime

nav_obj = Navigator()
BASE_DIR = nav_obj.get_katana_dir()
wapps_dir_path = BASE_DIR + "/wapps/"
native_dir_path = BASE_DIR + "/native/"
wapps_dir = BASE_DIR + "/wapps"
settings_file = BASE_DIR + "/wui/settings.py"
urls_file = BASE_DIR + "/wui/urls.py"
check_ok = 'true'
DONE = False
app_config_data = ""


def create_log(message):
    """ this function appends the log"""
    with open(os.path.join(nav_obj.get_katana_dir(),"log.txt"), "a") as f:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        log_line = dt_string + "     " + message + "\n"
        f.writelines(log_line)
        f.close()


def __appmanager__(deleted_Apps_list):
    """this function is used to perform the primary checks before starting the app installation process"""
    if len(deleted_Apps_list) > 0:
        for uapp in deleted_Apps_list:
            if uapp in ["settings", "microservice_store", "wappstore"]:
                remove_appurl_from_urls_custom(uapp, "native")
                remove_app_from_settings_custom(uapp, "native")
                remove_cust_app_source(uapp, "native")
            else:
                remove_appurl_from_urls_custom(uapp, "wapps")
                remove_app_from_settings_custom(uapp, "wapps")
                remove_cust_app_source(uapp, "wapps")


def install_default_apps(default_branch):
    """this function is used to install default apps"""
    repo_url = "https://github.com/warriorframework/warrior-apps.git"
    directory = "temp_apps"
    tempdirr = os.path.join(BASE_DIR, directory)
    if os.path.exists(tempdirr):
        shutil.rmtree(tempdirr)
    os.mkdir(tempdirr)
    if default_branch == '':
        branch = "master"
    else:
        branch = default_branch
    try:
        Repo.clone_from(repo_url, tempdirr, branch=branch)
    except:
        print("The given repo does not exists")
        exit()
    _ignore = ["README.md", ".git"]
    temp_apps_dir_list = list(set(os.listdir(tempdirr)) - set(_ignore))
    for apps_dir in temp_apps_dir_list:
        if apps_dir == "wapps":
            for sub_dir in os.listdir(os.path.join(tempdirr, apps_dir)):
                if os.path.isdir(os.path.join(tempdirr, os.path.join(apps_dir, sub_dir)))\
                     and not sub_dir.startswith("."):
                    source = os.path.join(
                        tempdirr, os.path.join(apps_dir, sub_dir))
                    destination = os.path.join(wapps_dir_path, sub_dir)
                    if os.path.exists(destination):
                        shutil.rmtree(destination)
                    shutil.move(source, destination)
                    configure_settings_file(sub_dir, "wapps")
                    configure_urls_file(sub_dir, "wapps")
        elif apps_dir == "native":
            for sub_dir in os.listdir(os.path.join(tempdirr, apps_dir)):
                if os.path.isdir(os.path.join(tempdirr, os.path.join(apps_dir, sub_dir)))\
                     and not sub_dir.startswith("."):
                    source = os.path.join(
                        tempdirr, os.path.join(apps_dir, sub_dir))
                    destination = os.path.join(native_dir_path, sub_dir)
                    if os.path.exists(destination):
                        shutil.rmtree(destination)
                    shutil.move(source, destination)
                    configure_settings_file(sub_dir, "native")
                    configure_urls_file(sub_dir, "native")
    shutil.rmtree(tempdirr)


def install_custom_app(app, app_url, app_trigger = "False"):
    """this function is used to install custom apps"""
    if app.endswith(".zip"):
        app = app.split(".")[0]
    if app.endswith(".git"):
        app = app.split(".")[0]
    if not os.path.exists(wapps_dir_path):
        os.mkdir(wapps_dir)
    app_url = app_url.split(" ")
    directory = app
    if app_url[0].endswith(".git"):
        if len(app_url) == 3:
            repo_url = app_url[0]
            user_branch = app_url[2]
        else:
            repo_url = app_url[0]
            user_branch = 'master'
        tempdir = os.path.join(BASE_DIR, directory)
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
        os.mkdir(tempdir)
        try:
            Repo.clone_from(repo_url, tempdir, branch=user_branch)
        except:
               try:
                   print(colored("\nFailed to fetch "+app+" app data from git due to poor internet connection, retrying in a moment...", "red"))
                   time.sleep(4)
                   Repo.clone_from(repo_url, tempdir, branch=user_branch)
               except:
                     raise
        #check if app already exists then compare version and ask for user input
        existing_app_path = os.path.join(BASE_DIR, "wapps", directory)
        new_app_path = os.path.join(tempdir)
        if os.path.exists(existing_app_path):
            usr_choice, message = pre_install_checks(app, existing_app_path, new_app_path, app_trigger)
            if usr_choice not in ["y", "Y", "yes", "YES", "n", "N", "NO", "no"]:
                if message != "Reinstall":
                    print(colored("Invalid choice!, continuing with the default choice: (Y)", "yellow"))
                    usr_choice = "Y"
                else:
                    print(colored("Invalid choice!, continuing with the default choice: (N)", "yellow"))
                    usr_choice = "N"
            if usr_choice in ["Y", "y", "yes", "YES"]:
                if message == "Reinstall":
                    print("Reinstalling the " + app + " app")
                elif message == "Upgrade":
                    print("Upgrading the " + app + " app")
                elif message == "Downgrade":
                    print("Downgrading the " + app + " app")
                remove_appurl_from_urls_custom(app, "wapps")
                remove_app_from_settings_custom(app, "wapps")
                remove_cust_app_source(app, "wapps")
                source = os.path.join(tempdir)
                destination = os.path.join(wapps_dir_path, directory)
                shutil.move(source, destination)
                configure_urls_file_custom(app, "wapps")
                configure_settings_file_custom_app(app)
                return "True"
            else:
                print(colored(message +": Skipped", "yellow"))
                return "False"
        else:
            print("Installing: " + app)
            create_log("Installing: " + app)
            source = os.path.join(tempdir)
            destination = os.path.join(wapps_dir_path, directory)
            if os.path.exists(destination):
                shutil.rmtree(destination)
            shutil.move(source, destination)
            configure_urls_file_custom(app, "wapps")
            configure_settings_file_custom_app(app)
            return "True"
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
    else:
        #check if app already exists then compare version and ask for user input
        existing_app_path = os.path.join(wapps_dir_path, directory)
        new_app_path = app_url[0]
        destination = existing_app_path
        app_path = app_url[0]
        tempdir = os.path.join(BASE_DIR, directory)
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
        os.mkdir(tempdir)
        if app_path.endswith(".zip"):
            if os.path.exists(app_path):
                zip_ref = zipfile.ZipFile(app_path, 'r')
                zip_ref.extractall(tempdir)
                zip_ref.close()
                app_path = new_app_path = os.path.join(tempdir, app)
        if os.path.exists(existing_app_path):
            usr_choice, message = pre_install_checks(app, existing_app_path, new_app_path, app_trigger)
            if usr_choice not in ["y", "Y", "yes", "YES", "n", "N", "NO", "no"]:
                print(colored("Invalid choice!, it must be (y/n)", "yellow"))
                usr_choice, message = pre_install_checks(app, existing_app_path, new_app_path, app_trigger)
            if usr_choice not in ["y", "Y", "yes", "YES", "n", "N", "NO", "no"]:
                print(colored("Invalid choice!, continuing with the default choice: (y)", "yellow"))
                usr_choice = "Y"
            if usr_choice in ["Y", "y", "yes", "YES"]:
                if message == "Reinstall":
                    print("Reinstalling the " + app + " app")
                elif message == "Upgrade":
                    print("Upgrading the " + app + " app")
                elif message == "Downgrade":
                    print("Downgrading the " + app + " app")
                remove_appurl_from_urls_custom(app, "wapps")
                remove_app_from_settings_custom(app, "wapps")
                remove_cust_app_source(app, "wapps")
                if os.path.isdir(app_path):
                    shutil.copytree(app_path, destination)
                    configure_urls_file_custom(app, "wapps")
                    configure_settings_file_custom_app(app)
                    if os.path.exists(tempdir):
                        shutil.rmtree(tempdir)
                    return "True"
            else:
                print(colored(message +": Skipped", "yellow"))
                if os.path.exists(tempdir):
                    shutil.rmtree(tempdir)
                return "False"
        else:
            print("Installing: " + app)
            create_log("Installing: " + app)
            if os.path.isdir(app_path):
                shutil.copytree(app_path, destination)
                configure_urls_file_custom(app, "wapps")
                configure_settings_file_custom_app(app)
                return "True"

def remove_cust_app_source(uapp, category):
    """this function removes custom app source code"""
    if category == "wapps":
        app_src_dir = os.path.join(wapps_dir, uapp)
        if os.path.exists(app_src_dir):
            shutil.rmtree(app_src_dir)
    elif category == "native":
        app_src_dir = os.path.join(native_dir_path, uapp)
        if os.path.exists(app_src_dir):
            shutil.rmtree(app_src_dir)


def configure_settings_file(app_name, category):
    """this function configure the settings for default apps"""
    with open(settings_file, "r") as f:
        settings_file_content = f.readlines()
    with open(settings_file, "w") as f:
        if "    'katana."+category+"."+app_name+"',\n" not in settings_file_content:
            for line in settings_file_content:
                if line == "    'katana.wui.core',\n":
                    f.writelines(line)
                    f.writelines("    'katana."+category+"."+app_name+"',\n")
                else:
                    f.writelines(line)
        else:
            for line in settings_file_content:
                f.writelines(line)


def configure_settings_file_custom_app(app):
    """this function configure the settings for custom apps"""
    with open(settings_file, "r") as f:
        settings_file_content = f.readlines()
    with open(settings_file, "w") as f:
        if "    'katana.wapps."+app+"',\n" not in settings_file_content:
            for line in settings_file_content:
                if line == "    'katana.wui.core',\n":
                    f.writelines(line)
                    f.writelines("    'katana.wapps."+app+"',\n")
                else:
                    f.writelines(line)
        else:
            for line in settings_file_content:
                f.writelines(line)


def configure_urls_file(app_name, category):
    """this function configure the url for default apps"""
    app_main_folder = os.path.join(BASE_DIR, category)
    app_folder = os.path.join(app_main_folder, app_name)
    wf_config_file = os.path.join(app_folder, "wf_config.json")
    data = read_json_data(wf_config_file)
    if data["app"]["url"].startswith("/"):
        app_url = data["app"]["url"][1:]
    else:
        app_url = data["app"]["url"]
    with open(urls_file, "r") as f:
        url_file_content = f.readlines()
    with open(urls_file, "w") as f:
        if "    url(r'^"+app_url+"', include('katana."+category+"."+app_name+".urls')),\n" not in url_file_content:
            for line in url_file_content:
                if line == "    url(r'^$', RedirectView.as_view(url='/katana/')),\n":
                    f.writelines(line)
                    f.writelines(
                        "    url(r'^"+app_url+"', include('katana."+category+"."+app_name+".urls')),\n")
                else:
                    f.writelines(line)
        else:
            for line in url_file_content:
                f.writelines(line)


def configure_urls_file_custom(app, category):
    """this function configure the url for custom apps"""
    app_main_folder = os.path.join(BASE_DIR, category)
    app_folder = os.path.join(app_main_folder, app)
    wf_config_file = os.path.join(app_folder, "wf_config.json")
    data = read_json_data(wf_config_file)
    if data["app"]["url"].startswith("/"):
        app_url = data["app"]["url"][1:]
    else:
        app_url = data["app"]["url"]
    with open(urls_file, "r") as f:
        url_file_content = f.readlines()
    with open(urls_file, "w") as f:
        if "    url(r'^"+app_url+"', include('katana.wapps."+app+".urls')),\n" \
            not in url_file_content:
            for line in url_file_content:
                if line == "    url(r'^$', RedirectView.as_view(url='/katana/')),\n":
                    f.writelines(line)
                    f.writelines(
                        "    url(r'^"+app_url+"', include('katana.wapps."+app+".urls')),\n")
                else:
                    f.writelines(line)
        else:
            for line in url_file_content:
                f.writelines(line)


def remove_app_from_settings_custom(app, category):
    """this function reverts settings for custom app"""
    if category == "wapps":
        with open(settings_file, "r") as f:
            settings_file_content = f.readlines()
        with open(settings_file, "w") as f:
            if "    'katana.wapps."+app+"',\n" in settings_file_content:
                for line in settings_file_content:
                    if line != "    'katana.wapps."+app+"',\n":
                        f.writelines(line)
            else:
                for line in settings_file_content:
                    f.writelines(line)
    elif category == "native":
        with open(settings_file, "r") as f:
            settings_file_content = f.readlines()
        with open(settings_file, "w") as f:
            if "    'katana.native."+app+"',\n" in settings_file_content:
                for line in settings_file_content:
                    if line != "    'katana.native."+app+"',\n":
                        f.writelines(line)
            else:
                for line in settings_file_content:
                    f.writelines(line)


def remove_appurl_from_urls_custom(app, category):
    """this function reverts urls for custom app"""
    app_main_folder = os.path.join(BASE_DIR, category)
    app_folder = os.path.join(app_main_folder, app)
    wf_config_file = os.path.join(app_folder, "wf_config.json")
    data = read_json_data(wf_config_file)
    if data["app"]["url"].startswith("/"):
        app_url = data["app"]["url"][1:]
    else:
        app_url = data["app"]["url"]
    with open(urls_file, "r") as f:
        url_file_content = f.readlines()
    if category == "wapps":
        with open(urls_file, "r") as f:
            url_file_content = f.readlines()
        with open(urls_file, "w") as f:
            if "    url(r'^"+app_url+"', include('katana.wapps."+app+".urls')),\n" \
                in url_file_content:
                for line in url_file_content:
                    if line != "    url(r'^"+app_url+"', include('katana.wapps."+app+".urls')),\n":
                        f.writelines(line)
            else:
                for line in url_file_content:
                    f.writelines(line)
    elif category == "native":
        with open(urls_file, "r") as f:
            url_file_content = f.readlines()
        with open(urls_file, "w") as f:
            if "    url(r'^katana/"+app+"/', include('katana.native."+app+".urls')),\n" \
                in url_file_content:
                for line in url_file_content:
                    if line != "    url(r'^katana/"+app+"/', include('katana.native."+app+".urls')),\n":
                        f.writelines(line)
            else:
                for line in url_file_content:
                    f.writelines(line)


def update_logo(img):
    """"this function update the warrior logo"""
    try:
        with open(img, "rb") as image_file:
            encoded_img = base64.b64encode(image_file.read())
        img_path = os.path.join(
            BASE_DIR, "wui/core/static/core/images/logo.png")
        fh = open(img_path, "wb")
        fh.write(base64.b64decode(encoded_img))
        fh.close()
    except:
        create_log(
            "Error: Unable to upload logo, please provide the valid image path.")


def update_fname(fname):
    """this function update the framework name """
    fname_file = os.path.join(
        BASE_DIR, "wui/core/static/core/framework_name.json")
    data = read_json_data(fname_file)
    data["fr_name"] = fname
    with open(fname_file, "w") as f:
        f.write(json.dumps(data, indent=4))


def update_panel_color(panel_color):
    """this function update the panel color"""
    css_file = os.path.join(
        BASE_DIR, "wui/core/static/core/css/panel_color.css")
    with open(css_file, "r") as f:
        css_data = f.readlines()
    with open(css_file, "w") as f:
        f.writelines(".header {background:"+panel_color+"}")

def check_app_version(existing_app, new_app):
    """This function will compare the versions of the existing app and the new app"""
    wf_config_extng = os.path.join(existing_app, "wf_config.json")
    wf_config_new = os.path.join(new_app, "wf_config.json")
    data_extng = read_json_data(wf_config_extng)
    data_new = read_json_data(wf_config_new)
    existing_version = data_extng["version"]
    new_version = data_new["version"]
    if existing_version == new_version:
        message = "Reinstall"
    elif existing_version < new_version:
        message = "Upgrade"
    else:
        message = "Downgrade"
    return existing_version, new_version, message

def get_user_input(appname, message, existing_version, new_version):
    """This function is used to get the user input(y/n)"""
    if message == "Reinstall":
        print("{0} app with the same version ({1}) already exists, Do you want to {2} (Y/n)?".format(appname, existing_version, message))
    else:
        print("{0} app with {1} version already exists, Do you want to {2} to {3} (Y/n)?".format(appname, existing_version, message, new_version))
    i, o, e = select.select( [sys.stdin], [], [], 10 )
    if (i):
        return sys.stdin.readline().strip()
    else:
        if message == "Reinstall":
            return "N"
        else:
            return "Y"

def pre_install_checks(appname, extng_app_path, new_app_path, app_trigger):
    """This function is used to perfrom prechecks before installing an app"""
    existing_version, new_version, message = check_app_version(extng_app_path, new_app_path)
    if app_trigger == "False":
        if message == "Reinstall":
            user_choice = get_user_input(appname, message, existing_version, new_version)
            return user_choice, message
        elif message == "Upgrade":
            user_choice = get_user_input(appname, message, existing_version, new_version)
            return user_choice, message
        elif message == "Downgrade":
            user_choice = get_user_input(appname, message, existing_version, new_version)
            return user_choice, message
    elif app_trigger == "True":
        user_choice = "Y"
        return user_choice, message
