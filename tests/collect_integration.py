# Pylint doesn't play well with fixtures and dependency injection from pytest
# pylint: disable=redefined-outer-name

import os
import pytest

from buildstream.testing.runcli import cli_integration as cli  # pylint: disable=unused-import
from buildstream.testing.integration import integration_cache  # pylint: disable=unused-import
from buildstream.testing.integration import assert_contains
from buildstream.testing._utils.site import HAVE_SANDBOX

DATA_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "project"
)


@pytest.mark.datafiles(DATA_DIR)
@pytest.mark.skipif(not HAVE_SANDBOX, reason='Only available with a functioning sandbox')
@pytest.mark.xfail(HAVE_SANDBOX == 'buildbox', reason='Not working with BuildBox')
# Not stricked xfail as only fails in CI
def test_collect_integration(cli, datafiles):
    project = str(datafiles)
    checkout = os.path.join(project, 'checkout')
    element_name = 'collect_integration/collect.bst'

    result = cli.run(project=project, args=['build', element_name])
    result.assert_success()

    result = cli.run(project=project, args=['artifact', 'checkout', '--directory', checkout, element_name])
    result.assert_success()

    assert_contains(checkout, ['/script.sh'])

    with open(os.path.join(checkout, 'script.sh'), 'r') as f:
        artifact = f.readlines()
    expected = [
        "#!/bin/sh\n",
        "set -e\n",
        "\n",
        "# integration commands from collect_integration/dep1.bst\n",
        "foo\n",
        "\n",
        "bar\n",
        "\n",
        "# integration commands from collect_integration/dep2.bst\n",
        "baz\n",
        "\n",
        "quuz\n",
        "\n"
    ]
    assert artifact == expected
