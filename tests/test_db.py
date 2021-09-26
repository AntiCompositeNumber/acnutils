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

from unittest import mock
from decimal import Decimal
import datetime
import importlib.util
import pytest

import acnutils

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("toolforge") is None, reason="installed without db extra"
)


def test_get_replag():
    mock_connect = mock.MagicMock()
    mock_cur = mock_connect.return_value.cursor.return_value.__enter__.return_value
    mock_execute = mock.MagicMock(return_value=1)
    mock_cur.execute = mock_execute
    mock_cur.fetchall.return_value = ((Decimal("10.0000"),),)

    with mock.patch("toolforge.connect", mock_connect):
        result = acnutils.get_replag(mock.sentinel.db, cluster=mock.sentinel.cluster)
    assert result == datetime.timedelta(seconds=10)


def test_get_replag_raise():
    mock_connect = mock.MagicMock()
    mock_cur = mock_connect.return_value.cursor.return_value.__enter__.return_value
    mock_execute = mock.MagicMock(return_value=0)
    mock_cur.execute = mock_execute

    with mock.patch("toolforge.connect", mock_connect):
        with pytest.raises(ValueError):
            acnutils.get_replag(mock.sentinel.db, cluster=mock.sentinel.cluster)
