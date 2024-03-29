# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import unittest

from perf_insights import function_handle
from perf_insights.mre import failure as failure_module
from perf_insights.mre import job as job_module


def _SingleFileFunctionHandle(filename, function_name, guid):
  return function_handle.FunctionHandle(
      modules_to_load=[function_handle.ModuleToLoad(filename=filename)],
      function_name=function_name, guid=guid)


class FailureTests(unittest.TestCase):

  def testAsDict(self):
    map_function_handle = _SingleFileFunctionHandle('foo.html', 'Foo', '2')
    reduce_function_handle = _SingleFileFunctionHandle('bar.html', 'Bar', '3')
    job = job_module.Job(map_function_handle, reduce_function_handle, '1')
    failure = failure_module.Failure(job, 'foo.html:Foo',
                                     'file://foo.html',
                                     'err', 'desc', 'stack')

    self.assertEquals(failure.AsDict(), {
      'job_guid': '1',
      'function_handle_string': 'foo.html:Foo',
      'trace_canonical_url': 'file://foo.html',
      'type': 'err',
      'description': 'desc',
      'stack': 'stack'
    })

  def testFromDict(self):
    map_function_handle = _SingleFileFunctionHandle('foo.html', 'Foo', '2')
    reduce_function_handle = _SingleFileFunctionHandle('bar.html', 'Bar', '3')
    job = job_module.Job(map_function_handle, reduce_function_handle, '1')

    failure_dict = {
        'job_guid': '1',
        'function_handle_string': 'foo.html:Foo',
        'trace_canonical_url': 'file://foo.html',
        'type': 'err',
        'description': 'desc',
        'stack': 'stack'
    }

    failure = failure_module.Failure.FromDict(failure_dict, job)

    self.assertEquals(failure.job.guid, '1')
    self.assertEquals(failure.function_handle_string, 'foo.html:Foo')
    self.assertEquals(failure.trace_canonical_url, 'file://foo.html')
    self.assertEquals(failure.failure_type_name, 'err')
    self.assertEquals(failure.description, 'desc')
    self.assertEquals(failure.stack, 'stack')
