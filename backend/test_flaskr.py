import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_paginate_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])


    def test_404_sent_requesting_beyond_valid(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error_code'],404)
        self.assertEqual(data['message'],'Not Found')


    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(data['success'],True)


    def test_delete_question(self):
        res = self.client().delete('/questions/2/delete')
        data = json.loads(res.data)
        self.assertEqual(data['success'],True)# PROBLEM
        self.assertEqual(data['deleted'],2)


    def test_404_delete_question(self):
        res = self.client().delete('/questions/2/delete')
        data = json.loads(res.data)
        self.assertEqual(data['success'],False) # PROBLEM
        self.assertEqual(data['error_code'],404)
        self.assertEqual(data['message'],'Not Found')


    def test_search_question(self):
        serach_term = {'searchTerm': 'Test'}
        res = self.client().get('/search',json=serach_term)
        data = json.loads(res.data)
        self.assertEqual(data['success'],True)
        # self.assertTrue(data['total_questions'])


    def test_404_search_question(self):
        res = self.client().get('/search')
        data = json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error_code'],404)
        self.assertEqual(data['message'],'Not Found')


    def test_category_question(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        self.assertEqual(data['success'],True)
        # self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'],2)


    def test_404_category_question(self):
        res = self.client().get('/categories/12/questions')
        data = json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error_code'],404)
        self.assertEqual(data['message'],'Not Found')


    def test_play_quiz(self):
        data = {
                'previous_questions':[],
                'quiz_category':{
                    'type': 'Art',
                    'id': 2
                }
        }
        res = self.client().post('/quizzes',json=data)
        data = json.loads(res.data)
        self.assertEqual(data['success'],True)# PROBLEM


    def test_404_play_quiz(self):
        data = {
                'previous_questions':[],
                'quiz_category':{
                    'type': 'CS',
                    'id': 12
                }
        }
        res = self.client().post('/quizzes',json=data)
        data = json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error_code'],404)
        self.assertEqual(data['message'],'Not Found')




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
