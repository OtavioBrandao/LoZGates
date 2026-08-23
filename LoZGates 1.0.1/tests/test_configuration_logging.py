import json
import logging
import tempfile
import unittest
from pathlib import Path

from BackEnd.logging_config import configure_logging
from config import ASSETS_DIR, CIRCUIT_IMAGE_PATH, DATA_DIR, INPUT_CACHE_PATH, ROOT_PATH


class ConfigurationTests(unittest.TestCase):
    def test_runtime_outputs_are_outside_versioned_assets(self):
        self.assertEqual(ASSETS_DIR, ROOT_PATH / "assets")
        self.assertEqual(CIRCUIT_IMAGE_PATH.parent, DATA_DIR)
        self.assertEqual(INPUT_CACHE_PATH.parent, DATA_DIR)
        self.assertNotEqual(CIRCUIT_IMAGE_PATH.parent, ASSETS_DIR)


class LoggingTests(unittest.TestCase):
    def tearDown(self):
        root_logger = logging.getLogger()
        for handler in list(root_logger.handlers):
            if getattr(handler, "_lozgates_handler", False):
                root_logger.removeHandler(handler)
                handler.close()

    def test_structured_rotating_files_separate_errors(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            log_dir = configure_logging(
                Path(temporary_directory), level="DEBUG", force=True
            )
            test_logger = logging.getLogger("tests.logging")
            test_logger.info("mensagem informativa")
            try:
                raise RuntimeError("falha controlada")
            except RuntimeError:
                test_logger.exception("mensagem de erro")

            for handler in logging.getLogger().handlers:
                handler.flush()

            general_lines = (log_dir / "lozgates.log").read_text(
                encoding="utf-8"
            ).splitlines()
            error_lines = (log_dir / "errors.log").read_text(
                encoding="utf-8"
            ).splitlines()

            general_records = [json.loads(line) for line in general_lines]
            error_records = [json.loads(line) for line in error_lines]
            self.assertTrue(
                any(record["message"] == "mensagem informativa" for record in general_records)
            )
            self.assertEqual(error_records[-1]["level"], "ERROR")
            self.assertIn("RuntimeError", error_records[-1]["exception"])
            self.tearDown()


if __name__ == "__main__":
    unittest.main()
