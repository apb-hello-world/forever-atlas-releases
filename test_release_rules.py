import unittest
from release_rules import check_promotion,version_key

class ReleaseRulesTests(unittest.TestCase):
    def test_equivalent_spellings(self):
        self.assertEqual(version_key('0.5.0b1'),version_key('0.5.0-beta.1'))
    def test_upgrade_keeps_addon(self):
        check_promotion('v0.5.0-beta.1','0.5.0b1','0.4.6','preview',{'channel':'preview','companion':{'version':'0.4.0b17'},'addon':{'version':'0.4.6'}})
    def test_reject_downgrade(self):
        with self.assertRaises(ValueError):check_promotion('v0.5.0-beta.1','0.5.0b1','0.4.6','preview',{'channel':'preview','companion':{'version':'0.5.0b2'},'addon':{'version':'0.4.6'}})
    def test_reject_prerelease_stable(self):
        with self.assertRaises(ValueError):check_promotion('v0.5.0-beta.1','0.5.0b1','0.4.6','stable')
    def test_reject_mismatched_tag(self):
        with self.assertRaises(ValueError):check_promotion('v0.5.0-beta.2','0.5.0b1','0.4.6','preview')

if __name__=='__main__':unittest.main()
