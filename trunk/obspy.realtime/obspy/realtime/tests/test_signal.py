# -*- coding: utf-8 -*-
"""
The obspy.realtime.signal test suite.
"""
from obspy.core import read
from obspy.core.stream import Stream
from obspy.signal.filter import lowpass
from obspy.realtime import RtTrace, splitTrace, signal
import numpy as np
import os
import unittest


# some debug flags
PLOT_TRACES = False


class RealTimeSignalTestCase(unittest.TestCase):
    """
    The obspy.realtime.signal test suite.
    """
    NUM_PAKETS = 3

    def setUp(self):
        # original trace
        self.orig_trace = read(os.path.join(os.path.dirname(__file__), 'data',
                              'II.TLY.BHZ.SAC'))[0]
        # create set of contiguous packet data in an array of Trace objects
        self.orig_trace_chunks = splitTrace(self.orig_trace, self.NUM_PAKETS)
        # clear results
        self.filt_trace_data = None
        self.rt_trace = None
        self.rt_appended_traces = []

    def tearDown(self):
        # use results for debug plots if enabled
        if PLOT_TRACES and self.filt_trace_data is not None and \
           self.rt_trace is not None and self.rt_appended_traces:
            self._plotResults()

    def test_lowpass(self):
        """
        Testing obspy.signal.filters.lowpass function.
        """
        trace = self.orig_trace.copy()
        options = {'freq': 1.0, 'df': trace.stats.sampling_rate}
        # filtering manual
        self.filt_trace_data = lowpass(trace, **options)
        # filtering real time
        process_list = [(lowpass, options)]
        self._runRtProcess(process_list)
        # check results
        np.testing.assert_array_equal(self.filt_trace_data, self.rt_trace.data)

    def test_square(self):
        """
        Testing np.square function.
        """
        trace = self.orig_trace.copy()
        options = {}
        # filtering manual
        self.filt_trace_data = np.square(trace, **options)
        # filtering real time
        process_list = [(np.square, options)]
        self._runRtProcess(process_list)
        # check results
        np.testing.assert_array_equal(self.filt_trace_data, self.rt_trace.data)

    def test_integrate(self):
        """
        Testing integrate function.
        """
        trace = self.orig_trace.copy()
        options = {}
        # filtering manual
        self.filt_trace_data = signal.integrate(trace, **options)
        # filtering real time
        process_list = [('integrate', options)]
        self._runRtProcess(process_list)
        # check results
        np.testing.assert_array_equal(self.filt_trace_data, self.rt_trace.data)

    def test_differentiate(self):
        """
        Testing differentiate function.
        """
        trace = self.orig_trace.copy()
        options = {}
        # filtering manual
        self.filt_trace_data = signal.differentiate(trace, **options)
        # filtering real time
        process_list = [('differentiate', options)]
        self._runRtProcess(process_list)
        # check results
        np.testing.assert_array_equal(self.filt_trace_data, self.rt_trace.data)

    def test_boxcar(self):
        """
        Testing boxcar function.
        """
        trace = self.orig_trace.copy()
        options = {'width': 500}
        # filtering manual
        self.filt_trace_data = signal.boxcar(trace, **options)
        # filtering real time
        process_list = [('boxcar', options)]
        self._runRtProcess(process_list)
        # check results
        peak = np.amax(np.abs(self.rt_trace.data))
        self.assertAlmostEqual(peak, 566974.187, 3)
        np.testing.assert_array_equal(self.filt_trace_data, self.rt_trace.data)

    def test_scale(self):
        """
        Testing scale function.
        """
        trace = self.orig_trace.copy()
        options = {'factor': 1000}
        # filtering manual
        self.filt_trace_data = signal.scale(trace, **options)
        # filtering real time
        process_list = [('scale', options)]
        self._runRtProcess(process_list)
        # check results
        peak = np.amax(np.abs(self.rt_trace.data))
        self.assertEqual(peak, 1045236992)
        np.testing.assert_array_equal(self.filt_trace_data, self.rt_trace.data)

    def test_abs(self):
        """
        Testing np.abs function.
        """
        trace = self.orig_trace.copy()
        options = {}
        # filtering manual
        self.filt_trace_data = np.abs(trace, **options)
        # filtering real time
        process_list = [(np.abs, options)]
        self._runRtProcess(process_list)
        # check results
        peak = np.amax(np.abs(self.rt_trace.data))
        self.assertEqual(peak, 1045237)
        np.testing.assert_array_equal(self.filt_trace_data, self.rt_trace.data)

    def test_tauc(self):
        """
        Testing tauc function.
        """
        trace = self.orig_trace.copy()
        options = {'width': 60}
        # filtering manual
        self.filt_trace_data = signal.tauc(trace, **options)
        # filtering real time
        process_list = [('tauc', options)]
        self._runRtProcess(process_list)
        # check results
        peak = np.amax(np.abs(self.rt_trace.data))
        self.assertAlmostEqual(peak, 114.296, 3)
        np.testing.assert_array_equal(self.filt_trace_data, self.rt_trace.data)

    def test_mwpIntegral(self):
        """
        Testing mwpIntegral functions.
        """
        trace = self.orig_trace.copy()
        options = {'mem_time': 240,
                   'ref_time': trace.stats.starttime + 301.506,
                   'max_time': 120,
                   'gain': 1.610210e+09}
        # filtering manual
        self.filt_trace_data = signal.mwpIntegral(self.orig_trace.copy(),
                                                  **options)
        # filtering real time
        process_list = [('mwpIntegral', options)]
        self._runRtProcess(process_list)
        # check results
        np.testing.assert_array_equal(self.filt_trace_data, self.rt_trace.data)

    def test_mwp(self):
        """
        Testing Mwp calculation using two processing functions.
        """
        trace = self.orig_trace.copy()
        epicentral_distance = 30.0855
        options = {'mem_time': 240,
                   'ref_time': trace.stats.starttime + 301.506,
                   'max_time': 120,
                   'gain': 1.610210e+09}
        # filtering manual
        trace.data = signal.integrate(trace)
        self.filt_trace_data = signal.mwpIntegral(trace, **options)
        # filtering real time
        process_list = [('integrate', {}), ('mwpIntegral', options)]
        self._runRtProcess(process_list)
        # check results
        peak = np.amax(np.abs(self.rt_trace.data))
        mwp = signal.calculateMwpMag(peak, epicentral_distance)
        self.assertAlmostEqual(mwp, 8.78902911791, 5)
        np.testing.assert_array_equal(self.filt_trace_data, self.rt_trace.data)

    def test_combined(self):
        """
        Testing combining integrate and differentiate functions.
        """
        trace = self.orig_trace.copy()
        options = {}
        # filtering manual
        trace.data = signal.integrate(trace, **options)
        self.filt_trace_data = signal.differentiate(trace, **options)
        # filtering real time
        process_list = [('int', options), ('diff', options)]
        self._runRtProcess(process_list)
        # check results
        trace = self.orig_trace.copy()
        np.testing.assert_array_equal(trace.data, self.rt_trace.data)
        np.testing.assert_array_equal(trace.data, self.filt_trace_data)

    def _runRtProcess(self, process_list, max_length=None):
        """
        Helper function to create a RtTrace, register all given process
        functions and run the real time processing.
        """
        # assemble real time trace
        self.rt_trace = RtTrace(max_length=max_length)

        for (process, options) in process_list:
            self.rt_trace.registerRtProcess(process, **options)

        # append packet data to RtTrace
        self.rt_appended_traces = []
        for trace in self.orig_trace_chunks:
            # process single trace
            result = self.rt_trace.append(trace, gap_overlap_check=True)
            # add to list of appended traces
            self.rt_appended_traces.append(result)

    def _plotResults(self):
        """
        Plots original, filtered original and real time processed traces into
        a single plot.
        """
        # plot only if test is started manually
        if __name__ != '__main__':
            return
        # create empty stream
        st = Stream()
        st.label = self._testMethodName
        # original trace
        self.orig_trace.label = "Original Trace"
        st += self.orig_trace
        # use header information of original trace with filtered trace data
        tr = self.orig_trace.copy()
        tr.data = self.filt_trace_data
        tr.label = "Filtered original Trace"
        st += tr
        # real processed chunks
        for i, tr in enumerate(self.rt_appended_traces):
            tr.label = "RT Chunk %02d" % (i + 1)
            st += tr
        # real time processed trace
        self.rt_trace.label = "RT Trace"
        st += self.rt_trace
        st.plot(automerge=False, color='blue', equal_scale=False)


def suite():
    # skip test suite if obspy.sac is not installed
    try:
        import obspy.sac  # @UnusedImport
    except ImportError:
        pass
    else:
        return unittest.makeSuite(RealTimeSignalTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')