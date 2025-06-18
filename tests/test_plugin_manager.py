from plugin_manager import PluginManager


def test_plugin_load(tmp_path):
    plugins = tmp_path / "plugins"
    plugins.mkdir()
    (plugins / "plugins.json").write_text('{"plugins": ["demo"]}')
    (plugins / "demo.py").write_text("VALUE = 123")

    pm = PluginManager(str(plugins))
    assert pm.discover() == ["demo"]
    mod = pm.load("demo")
    assert mod.VALUE == 123
