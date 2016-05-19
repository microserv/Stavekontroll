#from twisted.trial import unittestf
#from unittest import unittest
import unittest
import os
import requests
import json

import main
import spelling
import CONFIG

class SPELLCHECK(unittest.TestCase):
    def test_01_load_frequencies(self):
        frkfile = 'test_frk.frk'
        inpath = os.path.join('corpus', frkfile)

        outfile = 'test_buffered.json'
        outpath = os.path.join('corpus', outfile)
        #remove existing buffered file to make sure load_frequencies loads newly created .frk
        if os.path.exists(outpath):
            os.remove(outpath)
        del outpath
        
        #write testing frequency file to be loaded
        s = '''100 katt\n90 applaus\n89 apple\n88 applaudere\n70 kattesand\n71 kattepus\n60 sau\n500 og\n'''
        d = {'katt':100, 'applaus':90, 'apple':89, 'applaudere':88, 'kattesand':70, 'kattepus':71, 'sau':60, 'og':500}
        with open(inpath, 'w') as f:
            f.write(s)
        del inpath
        
        freqs = main.load_frequencies(frk_linelist=frkfile, frk_buffered_outfile=outfile)

        SPELLCHECK.frkfile = frkfile
        SPELLCHECK.outfile = outfile

        SPELLCHECK.d = d

        self.assertEqual(freqs, d)
        

    def test_02_load_frequencies_buffered(self):
        freqs = main.load_frequencies(frk_linelist=SPELLCHECK.frkfile , frk_buffered_outfile=SPELLCHECK.outfile)
        self.assertEqual(freqs, self.d)
        del SPELLCHECK.frkfile, SPELLCHECK.outfile

    def test_03_load_keytree(self):
        d = SPELLCHECK.d
        KT =    {'a': [0,
                       {'p': [0,
                              {'p': [0,
                                     {'l': [0,
                                            {'a': [0,
                                                   {'u': [0,
                                                          {'d': [0,
                                                                 {'e': [0,
                                                                        {'r': [0,
                                                                               {'e': [1,
                                                                                      {}]}]}]}],
                                                           's': [1, {}]}]}],
                                             'e': [1, {}]}]}]}]}],
                 'k': [0,
                       {'a': [0,
                              {'t': [0,
                                     {'t': [1,
                                            {'e': [0,
                                                   {'p': [0, {'u': [0, {'s': [1, {}]}]}],
                                                    's': [0,
                                                          {'a': [0,
                                                                 {'n': [0,
                                                                        {'d': [1,
                                                                               {}]}]}]}]}]}]}]}]}],
                 'o': [0, {'g': [1, {}]}],
                 's': [0, {'a': [0, {'u': [1, {}]}]}]}
        SPELLCHECK.KT = KT

        keytree_out = 'keytree_test.json'
        kpath = os.path.join('corpus', keytree_out)
        if os.path.exists(kpath):
            os.remove(kpath)
        del kpath
        
        ktd = main.load_keytree(d, keytree_out)
        
        self.assertEqual(ktd, KT)        
  
    def test_04_check_prefix(self):
        KT = SPELLCHECK.KT
        PFL = [('kat', ['katt', 'kattepus', 'kattesand']), 
               ('appl', ['applaus', 'applaudere', 'apple']), 
               ('sau', ['sau']),
               ('kfzzztksss', []),
               ]
        for prefix, expected in PFL:
            result = spelling.check_prefix(prefix, KT)
            self.assertEqual(set(expected), set(result))


    def ntest_99_EXTENSIVE(self):
        return True
        """Test most/all of asynchronous network pipeline. Difficult to test in isolation"""
        freqs = main.load_frequencies(frk_linelist='test_frk.frk', frk_buffered_outfile='test_buffered.json')
        keytree = main.load_keytree(SPELLCHECK.d, 'keytree_test.json')
        
        site=main.server.Site(main.SpellServer(freqs,keytree)) 
        main.reactor.listenTCP(CONFIG.SPELL_SERVER_PORT,site)

        PFL = [('kat', ['katt', 'kattepus', 'kattesand']), 
               ('appl', ['applaus', 'applaudere', 'apple']), 
               ('sau', ['sau']),
               ('kfzzztksss', []),
               ]
        
        REQL = [({'Type':'completion', 'Search':False, 'Query':'kat'}, ['katt', 'kattepus', 'kattesand']),
                ({'Type':'completion', 'Search':False, 'Query':'appl'}, ['applaus', 'applaudere', 'apple']),
                ({'Type':'completion', 'Search':False, 'Query':'sau'}, ['sau']),
                ({'Type':'completion', 'Search':False, 'Query':'kfzzztksss'}, []),
                ({'Type':'correction', 'Search':False, 'Query':'kkztt'}, ['katt']),
                ({'Type':'correction', 'Search':False, 'Query':'appleu'}, ['apple', 'applaus'])
               ]
        url = 'http://127.0.0.1:{}/'.format(CONFIG.SPELL_SERVER_PORT)
        def f():
            for req,expected in REQL:
                print(url)
                print(req)
                r = json.loads(requests.post(url, data=json.dumps(req)))
                if req['Type'] == 'completion':
                    results = r['results']
                spell = r['spell']
                self.assertEqual(set(spell), set(expected))
    
        delay = 5
        print('Starting reactor, calling test in {} seconds'.format(delay))
        main.reactor.callLater(delay+5, main.reactor.stop)
        main.reactor.callLater(delay, f)
        print('s')
        main.reactor.run()
            
if __name__ == '__main__':
    print('make sure backend-comm is running, and that the ip of index is registered')
    unittest.main()
    
