import subprocess
import sys
from importlib import import_module, invalidate_caches

import pytest


def install_package(package):
    """Install the supplied package into the current environment."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    
def bake_install_and_get_app_module(cookies, project_name="test_app"):
    """Bake the recipe, install the package, and return the `app` module"""
    result = cookies.bake(extra_context={"project_name": project_name})
    install_package(result.project)
    invalidate_caches()
    app_module = import_module(".app", package=project_name)
    return app_module


def test_bake_project(cookies, project_name="test_app"):
    """Test that the cookiecutter recipe is baked."""
    result = cookies.bake(extra_context={"project_name": project_name})

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project.isdir()
    assert result.project.basename == project_name


def test_baked_project_runs(cookies, dash_thread_server):
    """Test that app in the baked project runs and all routes are accessible."""
    app_module = bake_install_and_get_app_module(cookies)
    dash_thread_server.start(app_module.app)

    for route, _layout in app_module.index.urls:
        url = f"{dash_thread_server.url}/{route}"
        assert dash_thread_server.accessible(url), f"Loading route '{route}' failed" 
    

@pytest.mark.webdriver
def test_baked_project_runs_webdriver(cookies, dash_duo):
    """Test that the Dash app in the baked project runs."""
    app_module = bake_install_and_get_app_module(cookies)
    dash_duo.start_server(app_module.app)

    assert dash_duo.get_logs() == [], "browser console should contain no error"
    # TODO:
    # - add tests to check for presence of main content ID element
    # - add tests to check for all css/js/png/jpg/jpeg/svg present being reachable

