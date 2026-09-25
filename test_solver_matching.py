import unittest
from ai_functions.solver_matching import validate_matches, match_problem_to_solvers
from unittest.mock import patch

class MatchingTests(unittest.TestCase):
 def setUp(self):
  self.solvers=[{"solver_id":"11"},{"solver_id":"4"}]
 def test_ranked_real_ids(self):
  result=validate_matches({"matches":[{"solver_id":4,"match_score":60,"reason":"Relevant skill"},{"solver_id":"11","match_score":90,"reason":"Relevant expertise"}]},self.solvers)
  self.assertEqual([m["solver_id"] for m in result],["11","4"])
 def test_rejects_invalid_ai(self):
  for item in [{"solver_id":99,"match_score":90,"reason":"x"},{"solver_id":11,"match_score":True,"reason":"x"},{"solver_id":11,"match_score":90.5,"reason":"x"},{"solver_id":11,"match_score":101,"reason":"x"},{"solver_id":11,"match_score":90,"reason":""}]:
   with self.subTest(item=item),self.assertRaises(ValueError):validate_matches({"matches":[item]},self.solvers)
 def test_duplicate_ids_rejected(self):
  item={"solver_id":11,"match_score":90,"reason":"x"}
  with self.assertRaises(ValueError):validate_matches({"matches":[item,item]},self.solvers)
 def test_outage_does_not_fabricate(self):
  with patch('urllib.request.urlopen',side_effect=OSError('offline')):
   result=match_problem_to_solvers({},self.solvers)
  self.assertEqual(result['matches'],[])
  self.assertIn('error',result)
 def test_no_candidates(self):self.assertEqual(match_problem_to_solvers({},[]),{'matches':[]})

if __name__=='__main__':unittest.main()
