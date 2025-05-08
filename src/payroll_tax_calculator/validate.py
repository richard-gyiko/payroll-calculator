"""
Validate DSL JSONC files against the schema.

Usage:
    validate-dsl [--schema SCHEMA] PATH...

Arguments:
    PATH        One or more DSL JSONC files to validate

Options:
    --schema SCHEMA   Path to the schema file [default: dsl/schema.json]
    -h, --help        Show this help message
"""

import argparse
import json
import sys
from pathlib import Path

import jsonschema
from .loader import _strip_json_comments


def validate_dsl_file(file_path: Path, schema_path: Path) -> bool:
    """
    Validate a DSL JSONC file against the schema.

    Args:
        file_path: Path to the DSL JSONC file
        schema_path: Path to the schema file

    Returns:
        True if validation succeeds, False otherwise
    """
    try:
        # Load and parse the schema
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Load and parse the DSL file (stripping comments)
        with open(file_path, "r", encoding="utf-8") as f:
            dsl_content = f.read()

        # Strip comments from JSONC
        json_content = _strip_json_comments(dsl_content)

        # Parse the JSON
        dsl_data = json.loads(json_content)

        # Validate against schema
        jsonschema.validate(instance=dsl_data, schema=schema)

        print(f"✅ {file_path} - Valid")
        return True

    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e}", file=sys.stderr)
        return False
    except json.JSONDecodeError as e:
        print(f"❌ {file_path} - Invalid JSON: {e}", file=sys.stderr)
        return False
    except jsonschema.exceptions.ValidationError as e:
        print(f"❌ {file_path} - Schema validation failed:", file=sys.stderr)
        print(f"   {e.message}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ {file_path} - Unexpected error: {e}", file=sys.stderr)
        return False


def main() -> int:
    """Run the validation script."""
    parser = argparse.ArgumentParser(
        description="Validate DSL JSONC files against the schema"
    )
    parser.add_argument(
        "--schema", default="dsl/schema.json", help="Path to the schema file"
    )
    parser.add_argument(
        "paths", nargs="+", help="One or more DSL JSONC files to validate"
    )

    args = parser.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"❌ Error: Schema file not found: {schema_path}", file=sys.stderr)
        return 1

    success = True
    for path_str in args.paths:
        path = Path(path_str)
        if path.is_dir():
            # If directory, find all .jsonc files
            for jsonc_file in path.glob("**/*.jsonc"):
                if not validate_dsl_file(jsonc_file, schema_path):
                    success = False
        elif path.exists():
            if not validate_dsl_file(path, schema_path):
                success = False
        else:
            print(f"❌ Error: File not found: {path}", file=sys.stderr)
            success = False

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
