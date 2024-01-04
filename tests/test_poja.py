import poja
from filecmp import dircmp
import shutil
import tempfile
import os.path
import platform


def test_base():
    output_dir = "test-poja-base"
    poja.gen(
        app_name="poja-base",
        region="eu-west-3",
        with_own_vpc="true",
        ssm_sg_id="/poja/sg/id",
        ssm_subnet1_id="/poja/subnet/private1/id",
        ssm_subnet2_id="/poja/subnet/private2/id",
        ses_source="lou@hei.school",
        with_database="postgres",
        package_full_name="com.company.base",
        output_dir=output_dir,
        jacoco_min_coverage="0.5",
        custom_java_deps="custom-java-deps-justice.txt",
        with_snapstart="true",
    )
    assert is_dir_superset_of("oracle-poja-base", output_dir)


def test_base_without_own_vpc():
    output_dir = "test-poja-base-without-own-vpc"
    poja.gen(
        app_name="poja-base",
        region="eu-west-3",
        with_own_vpc="false",
        package_full_name="com.company.base",
        with_database="postgres",
        output_dir=output_dir,
        with_gen_clients="true",
        jacoco_min_coverage="0.9",
        with_snapstart="true",
    )
    assert is_dir_superset_of("oracle-poja-base-without-own-vpc", output_dir)


def test_base_without_postgres():
    output_dir = "test-poja-base-without-postgres"
    poja.gen(
        app_name="poja-base-without-postgres",
        region="eu-west-3",
        with_own_vpc="true",
        ssm_sg_id="/poja/sg/id",
        ssm_subnet1_id="/poja/subnet/private1/id",
        ssm_subnet2_id="/poja/subnet/private2/id",
        package_full_name="com.company.base",
        with_database="non-poja-managed-postgres",
        output_dir=output_dir,
        with_gen_clients="false",
        jacoco_min_coverage="0.9",
        with_snapstart="true",
    )
    assert is_dir_superset_of("oracle-poja-base-without-postgres", output_dir)


def test_base_with_custom_java_repos_and_sqlite():
    output_dir = "test-poja-sqlite"
    poja.gen(
        app_name="poja-sqlite",
        region="eu-west-3",
        with_own_vpc="true",
        ssm_sg_id="/poja/sg/id",
        ssm_subnet1_id="/poja-sqlite/subnet/public1/id",
        ssm_subnet2_id="/poja-sqlite/subnet/public2/id",
        package_full_name="com.company.base",
        with_database="sqlite",
        custom_java_repositories="custom-java-repositories.txt",
        output_dir=output_dir,
        jacoco_min_coverage="0.5",
    )
    assert is_dir_superset_of("oracle-poja-sqlite", output_dir)


def test_gen_with_all_cmd_args_is_equivalent_to_gen_with_poja_conf():
    oracle_dir = "oracle-poja-sqlite"

    temp_dir = (
        tempfile.TemporaryDirectory()
    )  # do NOT use with-as, as Python will prematurely rm the dir
    output_dir = shutil.copytree(oracle_dir, temp_dir.name, dirs_exist_ok=True)

    os.system(
        "pip uninstall -y poja && pip install -r requirements.txt -r requirements-dev.txt && python setup.py install"
    )
    if "Windows" in platform.system():
        poja_cmd_code = os.system(
            "cd /D %s && python -m poja --poja-conf poja.yml --output-dir=."
            % output_dir
        )
    else:
        poja_cmd_code = os.system(
            "cd %s && python -m poja --poja-conf poja.yml --output-dir=." % output_dir
        )

    assert poja_cmd_code == 0
    assert is_dir_superset_of(oracle_dir, output_dir)


def test_base_with_custom_java_env_vars_and_swagger_ui():
    output_dir = "test-poja-base-with-java-env-vars"
    poja.gen(
        app_name="poja-base-with-java-env-vars",
        region="eu-west-3",
        with_own_vpc="true",
        ssm_sg_id="/poja/sg/id",
        ssm_subnet1_id="/poja/subnet/private1/id",
        ssm_subnet2_id="/poja/subnet/private2/id",
        package_full_name="com.company.base",
        with_swagger_ui="true",
        with_database="postgres",
        custom_java_env_vars="custom-java-env-vars.txt",
        output_dir=output_dir,
        with_gen_clients="true",
        jacoco_min_coverage="0.9",
        with_snapstart="true",
    )
    assert is_dir_superset_of("oracle-poja-base-with-java-env-vars", output_dir)


def test_base_with_script_to_publish_to_npm_registry():
    output_dir = "test-poja-base-with-publication-to-npm-registry"
    poja.gen(
        app_name="poja-base-with-publication-to-npm-registry",
        region="eu-west-3",
        with_own_vpc="true",
        ssm_sg_id="/poja/sg/id",
        ssm_subnet1_id="/poja/subnet/private1/id",
        ssm_subnet2_id="/poja/subnet/private2/id",
        package_full_name="com.company.base",
        custom_java_env_vars="custom-java-env-vars.txt",
        output_dir=output_dir,
        jacoco_min_coverage="0.9",
        with_database="postgres",
        with_publish_to_npm_registry="true",
        with_gen_clients="true",
        ts_client_default_openapi_server_url="http://localhost",
        ts_client_api_url_env_var_name="CLIENT_API_URL",
        with_snapstart="true",
    )
    assert is_dir_superset_of(
        "oracle-poja-base-with-publication-to-npm-registry", output_dir
    )


def is_dir_superset_of(superset_dir, subset_dir):
    compared = dircmp(superset_dir, subset_dir)
    print(
        "superset_only=%s, subset_only=%s, both=%s, incomparables=%s"
        % (
            compared.left_only,
            compared.right_only,
            compared.diff_files,
            compared.funny_files,
        ),
    )
    if compared.right_only or compared.diff_files or compared.funny_files:
        return False
    for subdir in compared.common_dirs:
        if not is_dir_superset_of(
            os.path.join(superset_dir, subdir), os.path.join(subset_dir, subdir)
        ):
            return False
    return True
