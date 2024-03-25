#!/usr/bin/env python3
# coding: utf-8
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021 AntiCompositeNumber

import toolforge
import datetime


def get_replag(db: str, cluster: str = "web") -> datetime.timedelta:
    """Retrieve the current replecation lag for a Toolforge database.

    :param db: Name of the database, ``_p`` suffix not required.
    :param cluster: Database cluster to query.
    """
    conn = toolforge.connect(db, cluster=cluster)
    with conn.cursor() as cur:
        count = cur.execute("SELECT lag FROM heartbeat_p.heartbeat LIMIT 1")
        if count:
            return datetime.timedelta(seconds=float(cur.fetchall()[0][0]))
        else:
            raise ValueError
