import unittest
from utilities import *
from pygments.token import *
from subprocess import call

class lexerTest(unittest.TestCase):

    def setUp(self):
        self.tokens1 = [(Token.Name, u'System'), (Token.Operator, u'.'), (Token.Name.Attribute, u'out'), (Token.Operator, u'.'), (Token.Name.Attribute, u'println'), (Token.Operator, u'('), (Token.Literal.String, u'"I\'m a test!"'), (Token.Operator, u')'), (Token.Operator, u';'), (Token.Text, u'\n')]
        call(["python", "simplePyLex.py", "tests/", "*.java", "tests/", "3", "api"])
        

    def test_Strings(self):
        output1 = modifyStrings(self.tokens1, underscoreString)
        print(self.tokens1)
        print(output1)
        self.assertTrue(len(output1) == len(self.tokens1))
        self.assertTrue(output1[0] == self.tokens1[0])
        self.assertTrue(output1[1] == self.tokens1[1])
        self.assertTrue(output1[2] == self.tokens1[2])
        self.assertTrue(output1[3] == self.tokens1[3])
        self.assertTrue(output1[4] == self.tokens1[4])
        self.assertTrue(output1[5] == self.tokens1[5])

        self.assertFalse(output1[6] == self.tokens1[6])
        self.assertTrue(output1[6][1] == u'"I\'m_a_test!"')

        self.assertTrue(output1[7] == self.tokens1[7])
        self.assertTrue(output1[8] == self.tokens1[8])
        self.assertTrue(output1[9] == self.tokens1[9])

        output2 = modifyStrings(self.tokens1, singleStringToken)
        self.assertTrue(len(output2) == len(self.tokens1))
        self.assertTrue(output2[0] == self.tokens1[0])
        self.assertTrue(output2[1] == self.tokens1[1])
        self.assertTrue(output2[2] == self.tokens1[2])
        self.assertTrue(output2[3] == self.tokens1[3])
        self.assertTrue(output2[4] == self.tokens1[4])
        self.assertTrue(output2[5] == self.tokens1[5])

        self.assertFalse(output2[6] == self.tokens1[6])
        self.assertTrue(output2[6][1] == "<str>")

        self.assertTrue(output2[7] == self.tokens1[7])
        self.assertTrue(output2[8] == self.tokens1[8])
        self.assertTrue(output2[9] == self.tokens1[9])

        output3 = modifyStrings(self.tokens1, spaceString)
        print(output3)        

        self.assertTrue(len(output3) == len(self.tokens1))
        self.assertTrue(output3[0] == self.tokens1[0])
        self.assertTrue(output3[1] == self.tokens1[1])
        self.assertTrue(output3[2] == self.tokens1[2])
        self.assertTrue(output3[3] == self.tokens1[3])
        self.assertTrue(output3[4] == self.tokens1[4])
        self.assertTrue(output3[5] == self.tokens1[5])

        self.assertFalse(output3[6] == self.tokens1[6])
        self.assertTrue(output3[6][1] == u'" I\'m a test! "')

        self.assertTrue(output3[7] == self.tokens1[7])
        self.assertTrue(output3[8] == self.tokens1[8])
        self.assertTrue(output3[9] == self.tokens1[9])

    def test_Apis(self):
        tokens = []
        with open("tests/0.java.tokens", 'r') as f:
            for line in f:
                tokens += line.split(" ")

        self.assertTrue("Android.Namespace" not in tokens[15], "Actual:" + tokens[15])
        self.assertTrue("Android.Namespace" in tokens[16], "Actual:" + tokens[16])
        self.assertTrue("Android.Name" in tokens[194], "Actual:" + tokens[194])
        self.assertTrue("Android.Name" not in tokens[196], "Actual:" + tokens[196])
        self.assertTrue("Token.Name" in tokens[196], "Actual:" + tokens[196])
        self.assertTrue("Token.Name" in tokens[307], "Actual:" + tokens[307])
        self.assertTrue("Android.Function" in tokens[309], "Actual:" + tokens[309])
        

if __name__ == "__main__":
    unittest.main()
