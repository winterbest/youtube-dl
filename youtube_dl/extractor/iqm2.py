# coding: utf-8
from __future__ import unicode_literals
from ..utils import smuggle_url

import re

from .common import InfoExtractor
from ..compat import compat_urlparse
from .generic import GenericIE

# IQM2 aka Accela is a municipal meeting management platform that
# (among other things) stores livestreamed video from municipal
# meetings.  In some cases (e.g. cambridgema.iqm2.com), after a hefty
# (several-hour) processing time, that video is available in easily
# downloadable form from their web portal, but prior to that, the
# video can only be watched in realtime through JWPlayer. Other
# (somervillecityma.iqm2.com) instances don't seem to ever offer a
# downloadable form. This extractor is designed to download the
# realtime video without the download links being available. For more
# info on Accela, see:
#   http://www.iqm2.com/About/Accela.aspx
#   http://www.accela.com/
#   https://github.com/Accela-Inc/leg-man-api-docs

# This processing makes hard to test since there's only a narrow
# window when it matters. After that the extractor finds links to
# the processed video intead.

# No metadata is retrieved, as that would require finding a metadata
# URL and retreiving a 3rd HTTP resource.

# Contributed by John Hawkinson <jhawk@mit.edu>, 6 Oct 2016.

class IQM2IE(InfoExtractor):

    # We commonly see both iqm2.com and IQM2.com.
    _VALID_URL = r'(?i)https?://(?:\w+\.)?iqm2\.com/Citizens/\w+.aspx\?.*MeetingID=(?P<id>[0-9]+)'
    _TESTS = [ {
            'url': 'http://somervillecityma.iqm2.com/Citizens/SplitView.aspx?Mode=Video&MeetingID=2308',
         'md5': '9ef458ff6c93f8b9323cf79db4ede9cf',
         'info_dict': {
             'id': '70472_480',
             'ext': 'mp4',
             'title': 'City of Somerville, Massachusetts',
             'uploader': 'somervillecityma.iqm2.com',
         }}, {
        'url': 'http://cambridgema.iqm2.com/Citizens/SplitView.aspx?Mode=Video&MeetingID=1679#',
        'md5': '478ea30eee1966f7be0d8dd623122148',
        'info_dict': {
            'id': '1563_720',
            'ext': 'mp4',
            'title': 'Cambridge, MA (2)',
            'uploader': 'cambridgema.iqm2.com',
        }}, {
            'url': 'https://CambridgeMA.IQM2.com/Citizens/VideoMain.aspx?MeetingID=1679',
            'only_matching': True,
        }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        webpage = self._download_webpage(url, video_id)

        # print "Original URL is", url

        # Simple extractor: take, e.g.
        #   http://cambridgema.iqm2.com/Citizens/SplitView.aspx?Mode=Video&MeetingID=1679
        # and look for
        #   <div id="VideoPanel" class="LeftTopContent">
        #     <div id="VideoPanelInner" ... src="/Citizens/VideoScreen.aspx?MediaID=1563&Frame=SplitView">
        # and feed the canonicalized src element to the generic extractor
        inner_url_rel = self._html_search_regex(
            r'<div id="VideoPanelInner".*src="([^"]+)"',
            webpage, 'url');
        # print "inner_URL is", inner_url_rel

        inner_url = compat_urlparse.urljoin(url, inner_url_rel)

        if self._downloader.params.get('verbose'):
            self.to_screen('Invoking downloader on %s' % inner_url)

        # Generic extractor matches this under the "Broaden the
        # findall a little bit: JWPlayer JS loader" (line 2372 as of 6
        # Oct 2016, dcdb292fddc82ae11f4c0b647815a45c88a6b6d5).
        return self.url_result(smuggle_url(inner_url, {'to_generic': True}),
                               'Generic')
