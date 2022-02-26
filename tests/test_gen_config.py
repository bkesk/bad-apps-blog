import pytest

def test_init_config_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_config():
        Recorder.called = True

    result = runner.invoke(args=['init-config'])
    assert 'Nothing to initialize' in result.output

    monkeypatch.setattr('bad_apps_blog.gen_config.init_config', fake_init_config)
    result = runner.invoke(args=['init-config'])
    assert Recorder.called

