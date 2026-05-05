import tempfile
from ...Zenobie.standalone.rob_copy import hash_calculator, get_relative_paths, verify_hashs_and_paths

def test_hash_calculator_same_content():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"hello")
        f.flush()

        hash1 = hash_calculator(f.name)
        hash2 = hash_calculator(f.name)

        assert hash1 == hash2


def test_hash_calculator_different_content():
    with tempfile.NamedTemporaryFile(delete=False) as f1, \
         tempfile.NamedTemporaryFile(delete=False) as f2:

        f1.write(b"hello")
        f2.write(b"world")
        f1.flush()
        f2.flush()

        assert hash_calculator(f1.name) != hash_calculator(f2.name)

def test_get_relative_paths(tmp_path):
    # créer structure
    source = tmp_path / "repo"
    source.mkdir()

    file1 = source / "a.txt"
    file2 = source / "b.txt"

    file1.write_text("hello")
    file2.write_text("world")

    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    result = get_relative_paths(str(source), str(log_dir), "user", "role")

    assert len(result) == 2

    # vérifier les clés (relpath)
    keys = list(result.keys())
    assert any("a.txt" in k for k in keys)
    assert any("b.txt" in k for k in keys)

def test_verify_hash_mismatch(tmp_path):
    paths_source = {
        "repo/a.txt": ("hash1", "/src/a.txt"),
    }

    paths_destination = {
        "repo/a.txt": ("hash2", "/dst/a.txt"),
    }

    result = verify_hashs_and_paths(
        paths_source, paths_destination,
        str(tmp_path), "user", "role"
    )

    assert len(result) == 1

def test_verify_hash_mismatch(tmp_path):
    paths_source = {
        "repo/a.txt": ("hash1", "/src/a.txt"),
    }

    paths_destination = {
        "repo/a.txt": ("hash2", "/dst/a.txt"),
    }

    result = verify_hashs_and_paths(
        paths_source, paths_destination,
        str(tmp_path), "user", "role"
    )

    assert len(result) == 1

def test_verify_missing_file(tmp_path):
    paths_source = {}

    paths_destination = {
        "repo/a.txt": ("hash1", "/dst/a.txt"),
    }

    result = verify_hashs_and_paths(
        paths_source, paths_destination,
        str(tmp_path), "user", "role"
    )

    assert len(result) == 1