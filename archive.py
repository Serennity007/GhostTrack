"""Authorized account archive: consented phone <-> public profile links.

Only two kinds of associations may be saved:
- 'self':   the user confirms the phone number and profile are their own;
- 'public': the profile owner published that phone number on the public page.

The archive never probes platforms for accounts by phone number; it only
stores associations the user explicitly saved, with source and save time.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import phonenumbers

from platforms import PLATFORMS, ProfileInputError, profile_url

LIMIT = 200
SOURCES = ('self', 'public')
SOURCE_LABELS = {'self': '本人授权提供', 'public': '主页公开信息'}


class ArchiveError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def normalize_phone(value, region='CN'):
    region = region if isinstance(region, str) and region in phonenumbers.SUPPORTED_REGIONS else 'CN'
    try:
        number = phonenumbers.parse(str(value).strip(), region)
    except phonenumbers.NumberParseException:
        raise ArchiveError('archive_phone') from None
    if not phonenumbers.is_valid_number(number):
        raise ArchiveError('archive_phone')
    return (phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164),
            phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL))


def flatten(records):
    """Flatten archive records into an ordered report-friendly mapping.

    Keys use the 'Archive NN / <field>' namespace so the existing ' / '
    localization path translates the field suffix automatically.
    """
    data = {}
    for index, item in enumerate(records, 1):
        prefix = f'Archive {index:02d} / '
        data[prefix + '平台'] = item['platform']
        data[prefix + '电话'] = item['phone_display']
        data[prefix + '主页'] = item['url']
        data[prefix + '来源'] = SOURCE_LABELS[item['source']]
        data[prefix + '保存时间 UTC'] = item['added']
        if item['note']:
            data[prefix + '备注'] = item['note']
    return data


class Archive:
    """Bounded local archive persisted next to the desktop state file."""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.path = self.directory / 'archive.json'
        self.records = []
        self.warning = False
        try:
            if self.path.exists():
                if self.path.stat().st_size > 1_000_000:
                    raise ValueError('Oversize archive')
                data = json.loads(self.path.read_text(encoding='utf-8'))
                self.records = [item for item in data.get('records', [])[:self.LIMIT] if self.valid(item)]
        except (OSError, ValueError, TypeError, AttributeError):
            self.warning = True

    LIMIT = LIMIT

    @staticmethod
    def valid(item):
        return (isinstance(item, dict)
                and all(isinstance(item.get(key), str) for key in
                        ('id', 'phone', 'phone_display', 'platform', 'url', 'source', 'note', 'added'))
                and item['platform'] in PLATFORMS
                and item['source'] in SOURCES
                and len(item['note']) <= 500)

    def save(self):
        temporary = self.directory / ('archive-' + uuid4().hex + '.tmp')
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            temporary.write_text(json.dumps({'schema': 1, 'records': self.records[:self.LIMIT]},
                                            ensure_ascii=False, indent=2), encoding='utf-8')
            # Windows scanners/readers can briefly deny an otherwise valid atomic replacement.
            for retry_delay in (.02, .04, .08, None):
                try:
                    temporary.replace(self.path)
                    return True
                except OSError as error:
                    if retry_delay is None or getattr(error, 'winerror', None) not in (5, 32, 33):
                        raise
                    time.sleep(retry_delay)
        except (OSError, TypeError, ValueError):
            return False
        finally:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass

    def add(self, phone, platform, url, region='CN', source='self', note=''):
        e164, display = normalize_phone(phone, region)
        if platform not in PLATFORMS:
            raise ArchiveError('archive_platform')
        if source not in SOURCES:
            raise ArchiveError('archive_source')
        try:
            canonical = profile_url(platform, url)
        except ProfileInputError:
            raise ArchiveError('archive_url') from None
        stamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
        for item in self.records:
            if item['phone'] == e164 and item['platform'] == platform and item['url'] == canonical:
                item.update(source=source, note=str(note)[:500], added=stamp)
                return item, False, self.save()
        item = {'id': uuid4().hex, 'phone': e164, 'phone_display': display,
                'platform': platform, 'url': canonical, 'source': source,
                'note': str(note)[:500], 'added': stamp}
        self.records.insert(0, item)
        del self.records[self.LIMIT:]
        return item, True, self.save()

    def remove(self, record_id):
        before = len(self.records)
        self.records = [item for item in self.records if item['id'] != record_id]
        if len(self.records) == before:
            return False
        return self.save()

    def search(self, text):
        text = str(text).strip()
        if not text:
            return list(self.records)
        digits = ''.join(c for c in text if c.isdigit())
        needle = text.casefold()
        matches = []
        for item in self.records:
            haystack = f"{item['platform']} {item['url']} {item['note']} {item['phone_display']}".casefold()
            if needle in haystack or (len(digits) >= 3 and digits in item['phone']):
                matches.append(item)
        return matches
