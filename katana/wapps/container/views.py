import pkgutil
import importlib
import sys
def import_submodules(package, recursive=True):
    """ Import all submodules of a package, recursively, including subpackages
    Arguments:
    1. package    = (string) name of the package
                    (module) loader of the package
    2. recrusive  = (bool) True = load packages and modules from all sub-packages as well.
                    (bool) False = load only first level of packages and modules, do not load modules from sub packages
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
        print("{} : imported".format(package))
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        print(full_name)
        results[full_name] = importlib.import_module(full_name)
        print(results[full_name])
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    print(results)
    return results
# import pdb
# pdb.set_trace()
path = "katana/wapps/container/custom_views"
#path = "/home/apathapa/v3/lib/python3.5/site-packages/katana/wapps/cases/custom_files"
# path = path[1:]
path = path.replace("/",".")
results = import_submodules(path)

for key in results:
    exec("from {} import *".format(key))
