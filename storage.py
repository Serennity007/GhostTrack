"""Small bounded local state store. Query history is persisted only on opt-in."""
import json
import os
from pathlib import Path
from uuid import uuid4


class Store:
    def __init__(self, directory=None):
        self.directory = Path(directory or os.environ.get('GHOSTTRACK_DATA_DIR') or
                              Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'GhostTrackDesk')
        self.path = self.directory / 'state.json'
        self.settings = {'language': 'zh', 'region': 'CN', 'remember': False}
        self.history = []
        self.warning = False
        try:
            if self.path.exists():
                if self.path.stat().st_size > 2_000_000:
                    raise ValueError('Oversize state')
                state = json.loads(self.path.read_text(encoding='utf-8'))
                settings = state.get('settings', {})
                if settings.get('language') in ('zh', 'en', 'ja', 'es'):
                    self.settings['language'] = settings['language']
                region = settings.get('region')
                if isinstance(region, str) and len(region) == 2 and region.isupper():
                    self.settings['region'] = region
                self.settings['remember'] = settings.get('remember') is True
                if self.settings['remember']:
                    self.history = [item for item in state.get('history', [])[:50] if self.valid_record(item)]
        except (OSError, ValueError, TypeError, AttributeError):
            self.warning = True

    @staticmethod
    def valid_record(item):
        return (isinstance(item, dict) and isinstance(item.get('result'), dict)
                and len(item['result']) <= 100
                and all(isinstance(k, str) and isinstance(v, (str, int, float, bool, type(None)))
                        for k, v in item['result'].items())
                and all(isinstance(item.get(key), str) for key in ('id', 'time', 'kind', 'input', 'region', 'platform')))

    def save(self):
        temporary = self.directory / ('state-' + uuid4().hex + '.tmp')
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            history = self.history[:50] if self.settings['remember'] else []
            while True:
                state = {'schema': 1, 'settings': self.settings, 'history': history}
                encoded = json.dumps(state, ensure_ascii=False, indent=2)
                if len(encoded.encode('utf-8')) <= 1_900_000 or not history:
                    break
                history = history[:-1]
            temporary.write_text(encoded, encoding='utf-8')
            temporary.replace(self.path)
            return True
        except (OSError, TypeError, ValueError):
            return False
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass

    def record(self, kind, value, region, platform, result):
        self.history.insert(0, {'id': uuid4().hex, 'time': result.get('查询时间 UTC', ''),
                                'kind': kind, 'input': value[:5000], 'region': region,
                                'platform': platform, 'result': dict(result)})
        del self.history[50:]
        return self.save()

    def clear_history(self):
        self.history.clear()
        return self.save()
