"""Ownership retirement precedes stock model-manager shutdown, including errors."""
import gc
import sys
import unittest
import weakref
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src/res/scripts/client'))
from gui.mods.offline_lan_0922 import native_shutdown, engine_audio


class ShutdownOrderTests(unittest.TestCase):
    def setUp(self):
        self.previous = native_shutdown._HOOK
        native_shutdown._HOOK = None
        self.addCleanup(setattr,native_shutdown,'_HOOK',self.previous)

    def test_offline_cleanup_and_cycle_collection_precede_stock_fini_once(self):
        events = []
        game = SimpleNamespace(fini=lambda *a,**k:events.append(('stock',a,k)))
        cleanup = lambda:events.append(('offline',))
        self.assertTrue(native_shutdown.install(game,cleanup))
        self.assertFalse(native_shutdown.install(game,cleanup))
        with mock.patch.object(native_shutdown.gc,'collect',side_effect=lambda:events.append(('gc',))):
            game.fini(3,reason='exit')
            game.fini()
        self.assertEqual([('offline',),('gc',),('stock',(3,),{'reason':'exit'})],events)

    def test_cleanup_failure_is_reported_and_stock_fini_still_runs(self):
        game = SimpleNamespace(fini=mock.Mock())
        error = RuntimeError('retirement refused')
        native_shutdown.install(game,lambda:error)
        with mock.patch.object(native_shutdown.gc,'collect') as collect, \
                mock.patch.object(native_shutdown.sys,'stdout') as output:
            game.fini()
        collect.assert_called_once_with()
        native_shutdown._HOOK[1].assert_called_once_with()
        self.assertIn('retirement refused',str(output.write.call_args))

    def test_stock_appearance_destroy_releases_muted_model_before_native_retirement(self):
        events = []
        class Model:
            pass
        class Appearance:
            def destroy(self):
                events.append((self._offlineLANMutedEngine,self._offlineEngineMotion))
                return 'native-destroyed'
        a = Appearance()
        model = Model()
        witness = weakref.ref(model)
        a._offlineLANMutedEngine = (object(),model)
        a._offlineEngineMotion = object()
        a._offlineEngineRelay = None
        del model
        self.assertIsNotNone(witness())
        self.assertTrue(engine_audio.install_appearance_cleanup(Appearance))
        self.assertFalse(engine_audio.install_appearance_cleanup(Appearance))
        try:
            self.assertEqual('native-destroyed',a.destroy())
            self.assertIsNone(witness())
            self.assertEqual([(None,None)],events)
            a.destroy()
        finally:
            original,installed = engine_audio._APPEARANCE_HOOKS.pop(Appearance)
            Appearance.destroy = original

    def test_failed_audio_observer_cannot_skip_stock_destroy_or_keep_custom_model(self):
        class Appearance:
            def destroy(self):
                self.destroyed = True
        a = Appearance()
        a._offlineLANMutedEngine = (object(),object())
        a._offlineEngineRelay = SimpleNamespace(close=mock.Mock(side_effect=RuntimeError('callback failed')))
        engine_audio.install_appearance_cleanup(Appearance)
        try:
            with self.assertRaisesRegex(RuntimeError,'callback failed'):
                a.destroy()
            self.assertTrue(a.destroyed)
            self.assertIsNone(a._offlineLANMutedEngine)
            self.assertIsNone(a._offlineEngineRelay)
        finally:
            original,installed = engine_audio._APPEARANCE_HOOKS.pop(Appearance)
            Appearance.destroy = original


if __name__ == '__main__':
    unittest.main()
