# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""A handler and functions to check whether bisect is supported."""

import re

from dashboard import request_handler
from dashboard import namespaced_stored_object

# A set of suites for which we can't do performance bisects.
# This list currently also exists in the front-end code.
_UNBISECTABLE_SUITES = [
    'arc-perf-test',
    'browser_tests',
    'content_browsertests',
    'resource_sizes',
    'sizes',
    'v8',
]

# The bisect bot map stored in datastore is expected to be
# a dict mapping master names to [perf bot, bisect bot] pairs.
# If a master name is not in the dict, bisect isn't supported.
BISECT_BOT_MAP_KEY = 'bisect_bot_map'


class CanBisectHandler(request_handler.RequestHandler):

  def post(self):
    """Checks whether bisect is supported for a test.

    Request parameters:
      test_path: A full test path (Master/bot/benchmark/...)
      start_revision: The start of the bisect revision range.
      end_revision: The end of the bisect revision range.

    Outputs: The string "true" or the string "false".
    """
    can_bisect = (
        IsValidTestForBisect(self.request.get('test_path')) and
        IsValidRevisionForBisect(self.request.get('start_revision')) and
        IsValidRevisionForBisect(self.request.get('end_revision')))
    self.response.write('true' if can_bisect else 'false')


def IsValidTestForBisect(test_path):
  """Checks whether a test is valid for bisect."""
  if not test_path:
    return False
  path_parts = test_path.split('/')
  if len(path_parts) < 3:
    return False
  if not _MasterNameIsWhitelisted(path_parts[0]):
    return False
  if path_parts[2] in _UNBISECTABLE_SUITES:
    return False
  if test_path.endswith('/ref') or test_path.endswith('_ref'):
    return False
  return True


def _MasterNameIsWhitelisted(master_name):
  """Checks whether a master name is acceptable by checking a whitelist."""
  bisect_bot_map = namespaced_stored_object.Get(BISECT_BOT_MAP_KEY)
  if not bisect_bot_map:
    return True  # If there's no list available, all names are OK.
  whitelisted_masters = list(bisect_bot_map)
  return master_name in whitelisted_masters


def IsValidRevisionForBisect(revision):
  """Checks whether a revision looks like a valid revision for bisect."""
  return _IsGitHash(revision) or re.match(r'^[0-9]{5,7}$', str(revision))


def _IsGitHash(revision):
  """Checks whether the input looks like a SHA1 hash."""
  return re.match(r'[a-fA-F0-9]{40}$', str(revision))
