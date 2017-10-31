import pytest
from ruamel.yaml.constructor import DuplicateKeyError

from zops.anatomy.assertions import assert_file_contents
from zops.anatomy.layers.feature import AnatomyFeatureRegistry
from zops.anatomy.layers.playbook import AnatomyPlaybook


def test_success(anatomy_checker):
    anatomy_checker.check(
        """
            anatomy-features:
              - name: ALPHA
                variables:
                  name: Alpha
                create-file:
                  filename: alpha.txt
                  contents: |
                    This is {{ ALPHA.name }}.
            anatomy-playbook:
              use-features:
                ALPHA: {}
            target:
                alpha.txt: |
                    This is Alpha.
        """
    )


def test_invalid_key(anatomy_checker):
    """
    Raise an error when a feature uses an invalid (YAML) key for anatomy-features.
    """
    with pytest.raises(KeyError):
        anatomy_checker.check(
            """
                anatomy-features:
                  - name: ALPHA
                    invalid:
                      - one
                      - two
                    variables:
                      name: Alpha
                    create-file:
                      filename: alpha.txt
                      contents: |
                        This is {{ ALPHA.name }}.
                anatomy-playbook:
                  use-features:
                    ALPHA: {}
                target:
                    alpha.txt: |
                      This is Alpha.
            """
        )


def test_undefined_variable(anatomy_checker):
    """
    Raise an error when the template uses a undefined variable.
    """
    with pytest.raises(RuntimeError):
        anatomy_checker.check(
            """
                anatomy-features:
                  - name: ALPHA
                    variables:
                        name: Alpha
                    create-file:
                      filename: alpha.txt
                      contents: |
                        This is {{ UNDEFINED }}.
                anatomy-playbook:
                  use-features:
                    ALPHA: {}
                target: {}
            """
        )


def test_duplicate_key(anatomy_checker):
    """
    Duplicate key.
    """
    with pytest.raises(DuplicateKeyError):
        anatomy_checker.check(
            """
                anatomy-features:
                  - name: ALPHA
                    variables:
                      name: Alpha
                    create-file:
                      filename: alpha.txt
                      contents: |
                        This is {{ ALPHA.name }}.
                    create-file:
                      filename: bravo.txt
                      contents: |
                        This is {{ ALPHA.name }}.
                anatomy-playbook:
                  use-features:
                    ALPHA: {}
                target:
                    alpha.txt: |
                      This is Alpha.
                    bravo.txt: |
                      This is Alpha.
            """
        )


def test_invalid_use_feature_key(anatomy_checker):
    """
    Invalid key when using a feature.
    """
    with pytest.raises(RuntimeError):
        anatomy_checker.check(
            """
                anatomy-features:
                  - name: ALPHA
                    variables:
                      name: Alpha
                    create-file:
                      filename: alpha.txt
                      contents: |
                        This is {{ ALPHA.name }}.
                anatomy-playbook:
                  use-features:
                    ALPHA:
                      invalid_key: 0
                target:
                    alpha.txt: |
                        This is Alpha.
            """
        )


def test_use_features(anatomy_checker):
    """
    Test Features using other features.
    """
    anatomy_checker.check(
        """
            anatomy-features:
              - name: ALPHA
                create-file:
                  filename: alpha.txt
                  contents: |
                    This is Alpha.
              - name: BRAVO
                create-file:
                  filename: bravo.txt
                  contents: |
                    This is Bravo.
              - name: ZULU
                use-features:
                  ALPHA: {}
                  BRAVO: {}
            anatomy-playbook:
              use-features:
                ZULU: {}
            target:
              alpha.txt: |
                This is Alpha.
              bravo.txt: |
                This is Bravo.
        """
    )


def test_use_features_override_variables(anatomy_checker):
    """
    Check how the order of use-features on ZULU changes the output. The last feature in the list will have its value
    overwriting all others.
    """
    anatomy_checker.check(
        """
            anatomy-features:
              - name: ALPHA
                variables:
                  name: Alpha
                create-file:
                  filename: alpha.txt
                  contents: |
                    This is {{ ALPHA.name }}.
              - name: BRAVO
                use-features:
                  ALPHA:
                    name: Bravo
              - name: CHARLIE
                use-features:
                  ALPHA:
                    name: Charlie
              - name: ZULU
                use-features:  # <-- Testing this
                  BRAVO: {}
                  CHARLIE: {}
            anatomy-playbook:
              use-features:
                ZULU: {}
            target:
              alpha.txt: |
                This is Charlie.
        """
    )
    anatomy_checker.check(
        """
            anatomy-features:
              - name: ALPHA
                variables:
                  name: Alpha
                create-file:
                  filename: alpha.txt
                  contents: |
                    This is {{ ALPHA.name }}.
              - name: BRAVO
                use-features:
                  ALPHA:
                    name: Bravo
              - name: CHARLIE
                use-features:
                  ALPHA:
                    name: Charlie
              - name: ZULU
                use-features:  # <-- Testing this
                  CHARLIE: {}
                  BRAVO: {}
            anatomy-playbook:
              use-features:
                ZULU: {}
            target:
              alpha.txt: |
                This is Bravo.
        """
    )


def test_use_features_variables(anatomy_checker):
    anatomy_checker.check(
        """
            anatomy-features:
              - name: ALPHA
                variables:
                  name: Alpha
                create-file:
                  filename: alpha.txt
                  contents: |
                    This is {{ ALPHA.name }}.
              - name: ZULU
                use-features:
                  ALPHA:
                    name: Zulu
            anatomy-playbook:
              use-features:
                ZULU: {}
            target:
              alpha.txt: |
                This is Zulu.
        """
    )

    anatomy_checker.check(
        """
            anatomy-features:
              - name: ALPHA
                variables:
                  name: Alpha
                create-file:
                  filename: alpha.txt
                  contents: |
                    This is {{ ALPHA.name }}.
              - name: ZULU
                use-features:
                  ALPHA:
                    name: Zulu
            anatomy-playbook:
              use-features:
                ALPHA:
                  name: Playbook
                ZULU: {}
            target:
              alpha.txt: |
                This is Playbook.
        """
    )


def test_use_features_duplicate(anatomy_checker):
    anatomy_checker.check(
        """
            anatomy-features:
              - name: ALPHA
                create-file:
                  filename: alpha.txt
                  contents: |
                    This is Alpha.
              - name: BRAVO
                use-features:
                  ALPHA: {}
                create-file:
                  filename: bravo.txt
                  contents: |
                    This is Bravo.
              - name: ZULU
                use-features:
                  ALPHA: {}
                  BRAVO: {}
            anatomy-playbook:
              use-features:
                ZULU: {}
            target:
              alpha.txt: |
                This is Alpha.
              bravo.txt: |
                This is Bravo.
        """
    )


def test_use_features_is_dict(anatomy_checker):
    """
    Raise an error if use-features is a list.
    """
    with pytest.raises(TypeError):
        anatomy_checker.check(
            """
                anatomy-features:
                  - name: ALPHA
                    variables:
                        name: Alpha
                anatomy-playbook:
                  use-features:
                    - ALPHA
                target: {}
            """
        )


@pytest.fixture
def anatomy_checker(datadir):

    class AnatomyChecker(object):

        def check(self, seed):
            if isinstance(seed, str):
                contents = _to_contents(seed)
            elif isinstance(seed, dict):
                contents = seed
            else:
                raise TypeError(seed.__class__)
            AnatomyFeatureRegistry.clear()
            AnatomyFeatureRegistry.register_from_contents(contents)
            playbook = AnatomyPlaybook.from_contents(contents)
            target_dir = datadir + '/target'
            playbook.apply(target_dir)

            for i_filename, i_expected in contents['target'].items():
                assert_file_contents(
                    target_dir.join(i_filename),
                    i_expected
                )

    return AnatomyChecker()


def _to_contents(seed):
    from zops.anatomy.yaml import yaml_load
    from zops.anatomy.text import dedent

    return yaml_load(dedent(seed))
