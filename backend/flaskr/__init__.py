#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random , sys

from models import setup_db, Question, Category

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    [DONE]'''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    [DONE]'''
    @app.after_request
    def after_request(response):
      response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Headers','GET,POST.PATCH.DELETE,OPTIONS')
      response.headers.add('Access-Control-Allow-Origin', '*')
      return response


#----------------------------------------------------------------------------#
# Helper Methods.
#----------------------------------------------------------------------------#

    # pagination for each page 10 questions
    QUESTIONS_PER_PAGE = 10
    def paginate_questions(request , selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1 ) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    def get_category_list():
        categories = {}
        for category in Category.query.all():
            categories[category.id] = category.type
        return categories


#----------------------------------------------------------------------------#
# Endpoints.
#----------------------------------------------------------------------------#

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    [DONE]'''
    @app.route('/categories',methods=['GET'])
    def get_categories():
        try:
            current_categories = get_category_list()

            if current_categories is None:
                abort(404)
                print(sys.exc_info())
            else:
                return jsonify({
                            'success': True,
                            'categories': current_categories
                        })
        except:
            abort(404)
            print(sys.exc_info())


    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    [DONE]'''
    @app.route('/questions',methods=['GET'])
    def get_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request,selection)
            current_categories = get_category_list()

            if len(current_questions) == 0:
                abort(404)
                print(sys.exc_info())
            else:
                return jsonify({
                        'success': True,
                        'questions': current_questions,
                        'total_questions': len(Question.query.all()),
                        'categories': current_categories,
                        'current_category': len(current_categories)
                })
        except:
            abort(404)
            print(sys.exc_info())


    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    [DONE]'''
    @app.route('/questions/<int:question_id>',methods=["DELETE"])
    def delete_question(question_id):

        try:
            target = Question.query.filter(Question.id == question_id).one_or_none()
            if target is None:
                abort(404)
            target.delete()
            return jsonify({
                    'success': True,
                    'deleted' : question_id
                }),200
        except:
            # target.rollback()
            abort(422)
            print(sys.exc_info())





    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    [DONE]'''
    @app.route('/questions',methods=["POST"])
    def create_question():
        try:
            body = request.get_json()
            new_question = Question(
                    question = body.get('question'),
                    answer = body.get('answer'),
                    category = body.get('category'),
                    difficulty = body.get('difficulty')
            )
            new_question.insert()
            selection = Question.query.all()
            current_questions = paginate_questions(request,selection)
        except:
            # db.session.rollback()
            abort(422)
            print(sys.exc_info())


        return jsonify({
                'success': True,
                'created':new_question.id,
                'questions': current_questions,
                'total_questions': len(current_questions)+1
        })


    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    [DONE]'''
    @app.route('/search',methods=["POST","GET"])
    def search_question():
        try:
            body = request.get_json()
            search_term = '%{}%'.format(body.get('searchTerm'))
            print(search_term)
            findings = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            results = paginate_questions(request,findings)

            return jsonify({
                    'success': True,
                    'questions':results,
                    'total_questions': len(results)
            })
        except:
            abort(404)
            print(sys.exc_info())


    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    [DONE]'''
    @app.route('/categories/<int:category_id>/questions',methods=["GET"])
    def get_questions_basedOn_category(category_id):
        try:
            target_categ = Category.query.get(category_id).type
            # target_ques = Question.query.filter_by(category == target_categ).all()
            target_ques = Question.query.filter(Question.category == str(category_id)).all()
            questions = [question.format() for question in target_ques]
            if target_ques is None:
                abort(404)
                print(sys.exc_info())
            else:
                return jsonify({
                        'success':True,
                        'questions':questions,
                        'total_questions': len(questions),
                        'current_category':category_id
                        # 'categories':get_category_list()
                })
        except:
            abort(404)
            print(sys.exc_info())


    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    [DONE]'''

    @app.route('/quizzes',methods=["POST"])
    def play_quiz():
        try:
            body = request.get_json()

            quiz_category = body.get('quiz_category')
            previousQuestion = body.get('previous_questions')

            if (quiz_category['type'] == 'click'):
                questions = Question.query.filter(Question.id.notin_(previousQuestion)).all()

            else:
                questions = Question.query.filter_by(category=quiz_category['id']).all()

            available_questions = []
            format_questions = [question.format() for question in questions]
            for qn in format_questions:
                if qn['id'] not in previousQuestion:
                    available_questions.append(qn)
            if len(available_questions) > 0:
                selected_question = random.choice(available_questions)
                return jsonify({
                    'success' : True,
                    'question' : selected_question
                    })
            else:
                return jsonify({'success':False,'question':None})
        except:
            abort(422)



#----------------------------------------------------------------------------#
# Erorr Handling.
#----------------------------------------------------------------------------#

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''

    @app.errorhandler(404)
    def error_404(error):
        return jsonify({
                'success': False,
                'error_code': 404,
                'message' : 'Not Found'
        }),404
    @app.errorhandler(422)
    def error_422(error):
        return jsonify({
            'success': False,
            'error_code': 422,
            'message': 'Unprocessable'
            }),422




    return app
