#Unit tests for double checking the accuracy of function definition capturing
#and relabelling.

import unittest
import os
from subprocess import call

class apiLabelTest(unittest.TestCase):
    #String -> String
    def convertToPair(self, token):
        #print(token)
        token = token[1:-1]
        try:
            split = token.index("|Token.")
            return (token[:split], token[split+1:])
        except:
            return ("", "") #EOF padding?

    #String -> list of token,type pairs
    def readTokenFile(self, filename):
        tokenList = []
        with open(filename, 'r') as f:
            unsplit = f.readlines()[0].split(' ') #Just one line
            tokenList = [self.convertToPair(x) for x in unsplit]
            tokenList = [x for x in tokenList if not x == ("", "")]
        return tokenList
   
    def setUp(self):
        #Create the tokens files if they don't exist yet.
        if(not os.path.isfile("0.java.tokens")):
            call(["python", "simplePyLex.py", "./tests/apiTests/", "*.java", "./tests/apiTests/", "3", "api"])

        #Read in files
        self.file0 = self.readTokenFile("./tests/apiTests/0.java.tokens")
        self.file1 = self.readTokenFile("./tests/apiTests/1.java.tokens")
       
        
    

    
    #def testDefinitionSequences(self):

    #def testCallSequences(self):

    def testFile0(self):
        self.assertEqual(self.file0[79], ("IOException", "Token.Function.External.Call"), msg = "Actually: " +  str(self.file0[79]))
        self.assertEqual(self.file0[195], ("Decoder", "Token.Function.Definition"), msg = "Actually: " +  str(self.file0[195]))
        self.assertEqual(self.file0[237], ("reset", "Token.Function.Definition"), msg = "Actually: " +  str(self.file0[237]))
        self.assertEqual(self.file0[431], ("readName", "Token.Function.Internal.Call"), msg = "Actually: " +  str(self.file0[431]))

    def testFile1(self):
        #print(self.file0)
        self.assertEqual(self.file1[131], ("UnderDevelopmentGradleDistribution", "Token.Function.Internal.Call"), msg = "Actually: " +  str(self.file0[131]))
        self.assertEqual(self.file1[151], ("M2Installation", "Token.Name"), msg = "Actually: " +  str(self.file0[151]))
        self.assertEqual(self.file1[161], ("getTestDirectory","Token.Function.Internal.Call"), msg = "Actually: " +  str(self.file0[161]))
        self.assertEqual(self.file1[176], ("getDistribution","Token.Function.Definition"), msg = "Actually: " +  str(self.file0[176]))
        


if __name__=="__main__":
    unittest.main()
