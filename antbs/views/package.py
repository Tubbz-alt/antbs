#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#
#  package.py
#
#  Copyright © 2016-2017 Antergos
#
#  This file is part of The Antergos Build Server, (AntBS).
#
#  AntBS is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  AntBS is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  The following additional terms are in effect as per Section 7 of the license:
#
#  The preservation of all legal notices and author attributions in
#  the material or in the Appropriate Legal Notices displayed
#  by works containing it is required.
#
#  You should have received a copy of the GNU General Public License
#  along with AntBS; If not, see <http://www.gnu.org/licenses/>.

from . import *


class PackageView(FlaskView):
    route_base = '/package'

    def _get_build_events_timeline(self, pkg_obj, tlpage=1):
        timeline = []
        start_at = len(pkg_obj.tl_events) - 300
        start_at = max(0, start_at)

        for event_id in pkg_obj.tl_events[start_at:-1]:
            event = get_timeline_object(event_id=event_id)
            timeline.append(event)

        this_page, all_pages = get_paginated(timeline, 6, tlpage)

        return this_page, all_pages

    def _get_build_counts(self, pkg_obj):
        completed = [b for b in pkg_obj.builds if b and not build_failed(b)]
        failed = [b for b in pkg_obj.builds if b and build_failed(b)]

        completed = len(completed)
        failed = len(failed)

        counts = [
            ('Total Builds', completed + failed, ''),
            ('Completed', completed, 'success'),
            ('Failed', failed, 'danger')
        ]

        return counts

    @route('/<pkgname>', methods=['GET'], endpoint='get_and_show_pkg_profile')
    @route('/<pkgname>/<int:tlpage>', methods=['GET'], endpoint='get_and_show_pkg_profile')
    def get_and_show_pkg_profile(self, pkgname=None, tlpage=1):
        if pkgname is None or not status.all_packages.ismember(pkgname):
            abort(404)

        pkg_obj = get_pkg_object(name=pkgname)

        if '' == pkg_obj.description:
            desc = pkg_obj.get_from_pkgbuild('pkgdesc')
            pkg_obj.description = desc
            pkg_obj.pkgdesc = desc

        tl_events, all_pages = self._get_build_events_timeline(pkg_obj, tlpage=tlpage)
        build_counts = self._get_build_counts(pkg_obj)
        columns_info_obj = ColumnsInfo(current_user, request)
        service_icons_info = columns_info_obj.get_repo_monitor_services_icons_info()

        return try_render_template(
            'package.html',
            pkg=pkg_obj,
            tl_events=tl_events,
            page=tlpage,
            all_pages=all_pages,
            build_counts=build_counts,
            service_icons_info=service_icons_info
        )
