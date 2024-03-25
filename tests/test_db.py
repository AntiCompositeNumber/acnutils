#!/usr/bin/env python3
# coding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2020 AntiCompositeNumber

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
