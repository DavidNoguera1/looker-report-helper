import importlib.util
import json
from pathlib import Path
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('render_config', ROOT / 'scripts/render_config.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ConfigurationTests(unittest.TestCase):
    def test_client_launch_contracts(self):
        for client in ['codex', 'claude', 'opencode', 'plugin']:
            for platform in ['windows', 'posix']:
                with self.subTest(client=client, platform=platform):
                    text = module.render(client, platform)
                    if client == 'codex':
                        server = tomllib.loads(text)['mcp_servers']['looker-browser']
                        argv = [server['command'], *server['args']]
                    elif client == 'opencode':
                        server = json.loads(text)['mcp']['looker-browser']
                        self.assertEqual(server['type'], 'local')
                        self.assertTrue(server['enabled'])
                        argv = server['command']
                    else:
                        server = json.loads(text)['mcpServers']['looker-browser']
                        argv = [server['command'], *server['args']]
                    self.assertIn('@playwright/mcp@0.0.82', argv)
                    self.assertIn('--extension', argv)
                    self.assertNotIn('--headless', argv)
                    self.assertNotIn('--isolated', argv)
                    self.assertNotIn('--port', argv)
                    self.assertNotIn('env', server)
                    if platform == 'windows':
                        self.assertEqual(argv[:1] if client == 'codex' else argv[:3],
                                         ['npx.cmd'] if client == 'codex' else ['cmd', '/c', 'npx'])
                    else:
                        self.assertEqual(argv[0], 'npx')

    def test_public_plugin_uses_canonical_server(self):
        actual = json.loads((ROOT / '.mcp.json').read_text(encoding='utf-8'))
        self.assertEqual(actual, json.loads(module.render('plugin', 'posix')))

    def test_action_configuration_uses_one_server_and_absolute_script(self):
        for client in ['codex', 'claude', 'opencode', 'plugin']:
            for platform in ['windows', 'posix']:
                text = module.render(client, platform, with_actions=True)
                if client == 'codex':
                    servers = tomllib.loads(text)['mcp_servers']
                    config = servers['looker-browser']
                    argv = [config['command'], *config['args']]
                elif client == 'opencode':
                    servers = json.loads(text)['mcp']
                    argv = servers['looker-browser']['command']
                else:
                    servers = json.loads(text)['mcpServers']
                    config = servers['looker-browser']
                    argv = [config['command'], *config['args']]
                self.assertEqual(list(servers), ['looker-browser'])
                self.assertEqual(Path(argv[-1]), ROOT / 'automation/server.py')
                self.assertTrue(Path(argv[-1]).is_absolute())
                if platform == 'windows':
                    self.assertEqual(argv[:3], ['cmd', '/c', 'python'])


if __name__ == '__main__':
    unittest.main()
