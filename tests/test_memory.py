from rocketclaw.memory.memory_store import MemoryStore


def test_memory_write_read(tmp_path):
    store = MemoryStore(base=tmp_path)
    store.write("episodic", "session.txt", "hello")
    assert store.read("episodic", "session.txt") == "hello"


def test_memory_append(tmp_path):
    store = MemoryStore(base=tmp_path)
    store.append("episodic", "session.txt", "line1")
    store.append("episodic", "session.txt", "line2")
    data = store.read("episodic", "session.txt")
    assert "line1" in data
    assert "line2" in data
