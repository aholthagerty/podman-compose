# SPDX-License-Identifier: GPL-2.0

import json
import os
import unittest

from tests.integration.test_utils import RunSubprocessMixin
from tests.integration.test_utils import podman_compose_path
from tests.integration.test_utils import test_path


def compose_yaml_path():
    return os.path.join(
        test_path(),
        "merge/reset_and_override_tags/override_tag_service/docker-compose.yaml",
    )


class TestComposeOverrideTagService(unittest.TestCase, RunSubprocessMixin):
    # test if whole service from docker-compose.yaml file is overridden in another file
    def test_override_tag_service(self):
        override_file = os.path.join(
            test_path(),
            "merge/reset_and_override_tags/override_tag_service/docker-compose.override_service.yaml",
        )
        try:
            self.run_subprocess_assert_returncode([
                podman_compose_path(),
                "-f",
                compose_yaml_path(),
                "-f",
                override_file,
                "up",
            ])

            # Whole app service was overridden in the docker-compose.override_tag_service.yaml file.
            # Command and port is overridden accordingly.
            output, _ = self.run_subprocess_assert_returncode([
                podman_compose_path(),
                "-f",
                compose_yaml_path(),
                "-f",
                override_file,
                "logs",
            ])
            self.assertEqual(output, b"One\n")

            output, _ = self.run_subprocess_assert_returncode([
                "podman",
                "inspect",
                "override_tag_service_app_1",
            ])
            container_info = json.loads(output.decode('utf-8'))[0]
            self.assertEqual(
                container_info['NetworkSettings']["Ports"],
                {"81/tcp": [{"HostIp": "", "HostPort": "8111"}]},
            )
        finally:
            self.run_subprocess_assert_returncode([
                podman_compose_path(),
                "-f",
                compose_yaml_path(),
                "down",
            ])
