#!/usr/bin/env python3
# coding: utf-8
# SPDX-License-Identifier: Apache-2.0


# Copyright 2020 AntiCompositeNumber

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pywikibot
import unittest.mock as mock
from io import StringIO
import json
import pytest
import acnutils


@pytest.mark.parametrize("toolforge", [True, False])
@pytest.mark.parametrize("home", ["", "/lorem/ipsum"])
def test_get_log_location_pass(toolforge, home):
    mock_os = mock.Mock()
    mock_os.environ = {"HOME": home}
    mock_os.path.join = os.path.join
    mock_toolforge = mock.Mock(return_value=toolforge)

    with mock.patch("acnutils.os", mock_os):
        with mock.patch("acnutils.on_toolforge", mock_toolforge):
            actual = acnutils.get_log_location("/foo/bar/baz.log")

    assert actual == "/foo/bar/baz.log"
    mock_os.getcwd.assert_not_called()
    mock_os.mkdir.assert_not_called()


@pytest.mark.parametrize("home", ["/foo/bar", "/foo/bar/"])
@pytest.mark.parametrize("exists", [True, False])
def test_get_log_location_toolforge(home, exists):
    mock_os = mock.Mock()
    mock_os.environ = {"HOME": home}
    mock_os.path.join = os.path.join
    if exists:
        mock_os.mkdir.side_effect = FileExistsError
    mock_toolforge = mock.Mock(return_value=True)

    with mock.patch("acnutils.os", mock_os):
        with mock.patch("acnutils.on_toolforge", mock_toolforge):
            actual = acnutils.get_log_location("baz.log")

    assert actual == "/foo/bar/logs/baz.log"
    mock_os.getcwd.assert_not_called()
    mock_os.mkdir.assert_called_once()


@pytest.mark.parametrize("toolforge, home", [(True, ""), (False, "/lorem/ipsum/")])
@pytest.mark.parametrize("cwd", ["/foo/bar", "/foo/bar/"])
def test_get_log_location_cwd(toolforge, home, cwd):
    mock_os = mock.Mock()
    mock_os.environ = {"HOME": home}
    mock_os.path.join = os.path.join
    mock_os.getcwd.return_value = cwd
    mock_toolforge = mock.Mock(return_value=toolforge)
    with mock.patch("acnutils.os", mock_os):
        with mock.patch("acnutils.on_toolforge", mock_toolforge):
            actual = acnutils.get_log_location("baz.log")

    assert actual == "/foo/bar/baz.log"
    mock_os.getcwd.assert_called_once()
    mock_os.mkdir.assert_not_called()


@pytest.mark.parametrize("expected", [True, False])
def test_on_toolforge(expected):
    mock_open = mock.mock_open()
    if not expected:
        mock_open.side_effect = FileNotFoundError
    with mock.patch("acnutils.open", mock_open):
        result = acnutils.on_toolforge()

    mock_open.assert_called_once_with("/etc/wmcs-project")
    assert result is expected


@pytest.mark.parametrize(
    "task,title,expected",
    [
        ("", "", "User:LoremIpsum/Run"),
        ("Foo", "", "User:LoremIpsum/Foo/Run"),
        ("", "User:FooBar/Baz/Bang", "User:FooBar/Baz/Bang"),
    ],
)
def test_check_runpage_title(task, title, expected):
    site = mock.Mock(spec=pywikibot.site.BaseSite)
    site.username.return_value = "LoremIpsum"
    page = mock.Mock(spec=pywikibot.page.BasePage)
    page.return_value.text = "True"

    with mock.patch("pywikibot.Page", page):
        acnutils.check_runpage(site, task=task, title=title)
    page.assert_called_once_with(site, expected)


def test_check_runpage_tasktitle():
    site = mock.Mock(spec=pywikibot.Site)
    page = mock.Mock(spec=pywikibot.Page)

    with mock.patch("pywikibot.Page", page):
        with pytest.raises(ValueError):
            acnutils.check_runpage(site, task="Foo", title="Bar")


@pytest.mark.parametrize(
    "text",
    [
        "True",
        "<!--Set to False to stop the bot-->\nTrue",
    ],
)
def test_chec_runpage_true(text):
    site = mock.Mock(spec=pywikibot.site.BaseSite)
    page = mock.Mock(spec=pywikibot.page.BasePage)
    page.return_value.title.return_value = ""
    page.return_value.text = text

    with mock.patch("pywikibot.Page", page):
        acnutils.check_runpage(site, title="Foobar", override=False)


@pytest.mark.parametrize(
    "text", ["False", "", "Lorem ipsum", "True\nplease stop this bot"]
)
def test_check_runpage_false(text):
    site = mock.Mock(spec=pywikibot.site.BaseSite)
    page = mock.Mock(spec=pywikibot.page.BasePage)
    page.return_value.title.return_value = ""
    page.return_value.text = text

    with mock.patch("pywikibot.Page", page):
        with pytest.raises(acnutils.RunpageError):
            acnutils.check_runpage(site, title="Foobar", override=False)


def test_check_runpage_override():
    site = mock.Mock(spec=pywikibot.site.BaseSite)
    page = mock.Mock(spec=pywikibot.page.BasePage)
    page.return_value.title.return_value = ""
    page.return_value.text = "False"

    with mock.patch("pywikibot.Page", page):
        acnutils.check_runpage(site, title="Foobar", override=True)


@pytest.mark.parametrize(
    "mode,text,old_text,new_text",
    [
        ("replace", "[new_text]", "[old_text]", "[new_text]"),
        ("append", "[new_text]", "[old_text]", "[old_text][new_text]"),
        ("prepend", "[new_text]", "[old_text]", "[new_text][old_text]"),
        ("append", "[old_text]", "[old_text]", "[old_text][old_text]"),
        ("prepend", "[old_text]", "[old_text]", "[old_text][old_text]"),
        ("replace", "[new_text]", "", "[new_text]"),
        ("append", "[new_text]", "", "[new_text]"),
        ("prepend", "[new_text]", "", "[new_text]"),
    ],
)
def test_save_page(mode, text, old_text, new_text):
    mock_page = mock.Mock(spec=pywikibot.page.Page, text="[old_text]")
    if old_text:
        mock_page.get.return_value = mock_page.text
    else:
        mock_page.get.side_effect = pywikibot.exceptions.NoPageError(mock_page)
    mock_save = mock.Mock()
    mock_page.save = mock_save
    acnutils.save_page(
        text=text,
        page=mock_page,
        summary=mock.sentinel.summary,
        minor=mock.sentinel.minor,
        bot=mock.sentinel.bot,
        mode=mode,
        new_ok=True,
    )
    mock_save.assert_called_once_with(
        summary=mock.sentinel.summary,
        minor=mock.sentinel.minor,
        botflag=mock.sentinel.bot,
        quiet=True,
        force=False,
    )
    assert mock_page.text == new_text


@pytest.mark.parametrize(
    "mode,text,old_text,exception",
    [
        ("replace", "", "[old_text]", acnutils.PageNotSaved),
        ("append", "", "[old_text]", acnutils.PageNotSaved),
        ("prepend", "", "[old_text]", acnutils.PageNotSaved),
        ("delete", "foo", "[old_text]", ValueError),
        ("replace", "[old_text]", "[old_text]", acnutils.PageNotSaved),
        ("append", "foo", "", pywikibot.exceptions.NoPageError),
        ("prepend", "foo", "", pywikibot.exceptions.NoPageError),
    ],
)
def test_save_page_except(mode, text, old_text, exception):
    mock_page = mock.Mock(spec=pywikibot.page.Page, text=old_text)
    if old_text:
        mock_page.get.return_value = mock_page.text
    else:
        mock_page.get.side_effect = pywikibot.exceptions.NoPageError(mock_page)
    mock_save = mock.Mock()
    mock_page.save = mock_save
    with pytest.raises(exception):
        acnutils.save_page(
            text=text,
            page=mock_page,
            summary=mock.sentinel.summary,
            minor=mock.sentinel.minor,
            bot=mock.sentinel.bot,
            mode=mode,
        )


@pytest.mark.parametrize(
    "mode,text",
    [
        ("replace", "[old_text]"),
        ("append", ""),
        ("prepend", ""),
    ],
)
def test_save_page_no_change_ok(mode, text):
    mock_page = mock.Mock(spec=pywikibot.page.Page, text="[old_text]")
    mock_page.get.return_value = mock_page.text
    mock_save = mock.Mock()
    mock_page.save = mock_save
    acnutils.save_page(
        text=text,
        page=mock_page,
        mode=mode,
        summary=mock.sentinel.summary,
        minor=mock.sentinel.minor,
        bot=mock.sentinel.bot,
        no_change_ok=True,
    )
    mock_save.assert_not_called()


def test_retry():
    side_effect = [KeyError, ValueError, IndexError, OSError, None]
    func = mock.Mock()
    func.side_effect = side_effect
    retries = len(side_effect)

    acnutils.retry(func, retries, mock.sentinel.arg, foo=mock.sentinel.kwarg)
    assert func.call_count == retries
    func.assert_has_calls(
        [mock.call(mock.sentinel.arg, foo=mock.sentinel.kwarg) for i in range(retries)]
    )


def test_retry_raise():
    side_effect = [KeyError, ValueError, IndexError, OSError, ZeroDivisionError]
    func = mock.Mock()
    func.side_effect = side_effect
    retries = len(side_effect)

    with pytest.raises(ZeroDivisionError):
        acnutils.retry(func, retries, mock.sentinel.arg, foo=mock.sentinel.kwarg)
    assert func.call_count == retries
    func.assert_has_calls(
        [mock.call(mock.sentinel.arg, foo=mock.sentinel.kwarg) for i in range(retries)]
    )


@pytest.mark.parametrize("retries", [-1, 0])
def test_retry_retries(retries):
    func = mock.Mock()
    with pytest.raises(ValueError):
        acnutils.retry(func, retries)


def test_throttle():
    now = [
        1000.0,
        1000.0,
        1015.0,
        1015.0,
        1020.0,
        1025.0,
        1035.0,
        1035.0,
        1040.4999,
        1045.0,
    ]
    expected_list = [0, 0, 5.0, 0, 4.50]
    assert len(now) / 2 == len(expected_list)

    mock_mono = mock.Mock(side_effect=now)
    mock_sleep = mock.Mock()
    delay = 10

    throttle = acnutils.Throttle(delay)
    assert throttle.delay == delay
    with mock.patch("time.monotonic", mock_mono):
        with mock.patch("time.sleep", mock_sleep):
            for expected in expected_list:
                throttle.throttle()
                if expected:
                    mock_sleep.assert_called_once_with(expected)
                else:
                    mock_sleep.assert_not_called()
                mock_sleep.reset_mock()


def test_load_config():
    # The idea here is that the output will contain a key set only by each of
    # default_config[*], default_config[test], local_config[*], and local_config[test].
    # All but default_config[*] will also overwrite a key set by any combination of the
    # previous dicts.
    default_config = {
        "*": {  # dc*
            "1": 1,  # Set new
            "2": 1,
            "3": 1,
            "4": 1,
            "5": 1,
            "6": 1,
            "7": 1,
            "8": 1,
        },
        "test": {  # dct
            "2": 2,  # Overwrite dc*
            "3": 2,
            "4": 2,
            "5": 2,
            "9": 9,  # Set new
            "10": 9,
            "11": 9,
            "12": 9,
        },
        "exclude": {"foo": "bar"},
    }
    local_config = {
        "*": {  # lc*
            "3": 3,  # Overwrite dc*, dct
            "4": 3,
            "6": 6,  # Overwrite dc*
            "7": 6,
            "10": 10,  # Overwrite dct
            "11": 10,
            "13": 13,  # Set new
            "14": 13,
        },
        "test": {  # lct
            "4": 4,  # Overwrite dc*, dct, lc*
            "5": 5,  # Overwrite dc*, dct
            "7": 7,  # Overwrite dc*, lc*
            "8": 8,  # Overwrite dc*
            "11": 11,  # Overwrite dct, lc*
            "12": 12,  # Overwrite dct
            "14": 14,  # Overwrite lc*
            "15": 15,
        },
        "exclude": {"baz": "bang"},
    }
    mock_open = mock.MagicMock()
    mock_open.return_value.__enter__.side_effect = [
        StringIO(json.dumps(default_config)),
        StringIO(json.dumps(local_config)),
    ]
    mock_dirname = mock.Mock(return_value="/foo/bar/baz.py")
    with mock.patch("acnutils.open", mock_open):
        with mock.patch("os.path.dirname", mock_dirname):
            conf = acnutils.load_config("test", __file__)

    for i in range(1, 16):
        assert i == conf.pop(str(i))

    assert len(conf) == 0


def test_load_config_nolocal():
    default_config = {"*": {"foo": "bar"}}

    mock_open = mock.MagicMock()
    mock_open.return_value.__enter__.side_effect = [
        StringIO(json.dumps(default_config)),
        FileNotFoundError,
    ]
    mock_dirname = mock.Mock(return_value="/foo/bar/baz.py")
    with mock.patch("acnutils.open", mock_open):
        with mock.patch("os.path.dirname", mock_dirname):
            conf = acnutils.load_config("test", __file__)

    assert conf["foo"] == "bar"
