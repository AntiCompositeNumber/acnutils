#!/usr/bin/env python3
# coding: utf-8
# SPDX-License-Identifier: Apache-2.0


# Copyright 2021 AntiCompositeNumber

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
