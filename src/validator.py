import subprocess
import tempfile
import os
from typing import Dict, Any

def run_tests(source_code: str, test_code: str = "", timeout: int = 5) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        target_file = os.path.join(tmpdir, "target.py")
        with open(target_file, "w") as f:
            f.write(source_code)

        test_file = os.path.join(tmpdir, "test_target.py")
        if test_code:
            with open(test_file, "w") as f:
                f.write(test_code)
        else:
            # Generate a minimal placeholder test if no explicit tests provided
            # so pytest has something to run against the module syntax.
            with open(test_file, "w") as f:
                f.write("import target\n\ndef test_import():\n    pass\n")

        try:
            # Run pytest in the temporary directory
            res = subprocess.run(
                ["pytest", test_file, "-v", "--tb=short"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "success": res.returncode == 0,
                "output": res.stdout,
                "error": res.stderr,
                "returncode": res.returncode
            }

        except subprocess.TimeoutExpired as e:
            return {
                "success": False,
                "output": getattr(e, 'stdout', b'').decode('utf-8') if getattr(e, 'stdout', b'') else "",
                "error": f"Test execution timed out after {timeout} seconds.",
                "returncode": -1
            }
        except Exception as e:
             return {
                "success": False,
                "output": "",
                "error": f"Unexpected error during test execution: {str(e)}",
                "returncode": -1
            }
