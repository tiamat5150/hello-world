import unittest

from requests import codes
from requests_mock import Mocker

from onedrived import OS_USER_ID, OS_USER_GID, datetime_to_timestamp
from onedrived.api.items import OneDriveItem
from onedrived.common.tasks.down_task import get_tmp_filename, DownloadFileTask
from tests import get_data
from tests import mock
from tests.common.test_tasks import setup_os_mock
from tests.factory.tasks_factory import get_sample_task_base


class TestDownloadFileTask(unittest.TestCase):
    def setUp(self):
        self.data = get_data('image_item.json')
        self.data['name'] = 'test'
        self.data['size'] = 1
        self.parent_task = get_sample_task_base()
        self.item = OneDriveItem(drive=self.parent_task.drive, data=self.data)
        # The '/' in relative path is generated by MergeDirTask at root. Merging root itself has rel parent path ''.
        self.task = DownloadFileTask(self.parent_task, rel_parent_path='/', item=self.item)
        self.calls_hist = setup_os_mock()

    @Mocker()
    def test_handle(self, mock_request):
        tmp_path = self.parent_task.drive.config.local_root + '/' + get_tmp_filename('test')
        dest_path = self.parent_task.drive.config.local_root + '/test'
        tmp_path2 = self.task.local_parent_path + get_tmp_filename('test')
        ts = datetime_to_timestamp(self.item.modified_time)
        mock_request.get(self.task.drive.drive_uri + self.task.drive.drive_path + '/items/' + self.item.id + '/content',
                         content=b'1', status_code=codes.ok)
        m = mock.mock_open()
        with mock.patch('builtins.open', m, create=True):
            self.task.handle()
        self.assertEqual([(tmp_path, dest_path)], self.calls_hist['os.rename'])
        self.assertEqual([(dest_path, OS_USER_ID, OS_USER_GID)], self.calls_hist['os.chown'])
        self.assertEqual([(dest_path, (ts, ts))], self.calls_hist['os.utime'])
        self.assertEqual(tmp_path, tmp_path2)
        m.assert_called_once_with(tmp_path2, 'wb')
        handle = m()
        handle.write.assert_called_once_with(b'1')


if __name__ == '__main__':
    unittest.main()