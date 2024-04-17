import json

import requests as requests
from flask import Flask, render_template, redirect
from flask_login import LoginManager, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired
from waitress import serve

from data import db_session
import auth


class AnswerArea(FlaskForm):
    area = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Ответить')


class QuestionArea(FlaskForm):
    title = StringField('Тема вопроса', validators=[DataRequired()])
    area = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Спросить')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def get_request(url):
    resp = requests.get(f'http://localhost:1000/api/' + url)
    if resp.status_code != 200:
        raise Exception('Response status code ' + str(resp.status_code))
    return json.loads(resp.content)


def post_request(url, data):
    resp = requests.post(f'http://localhost:1000/api/' + url, json=data)
    if resp.status_code // 100 == 4 or resp.status_code // 100 == 5:
        raise Exception('Response status code ' + str(resp.status_code))
    return json.loads(resp.content)


def get_answer_by_id(ans_id):
    r = get_request(f'a/{ans_id}')
    return r['answer']


@app.route('/', methods=['GET', 'POST'])
def main_page():
    questions = get_request('q')
    return render_template('index.html', title='Knowledge book', questions=questions['questions'])


@app.route('/ask', methods=['GET', 'POST'])
def ask_question():
    if not current_user.is_authenticated:
        return redirect('/login')
    form = QuestionArea()
    if form.validate_on_submit():
        title = form.title.data.strip()
        content = form.area.data.strip()
        if content and title:
            user = current_user.id
            print(user, type(user))
            qid = post_request('q', {'title': title, 'content': content,
                                     'author_id': current_user.id})['id']
            return redirect(f'q/{qid}')
        else:
            return redirect('')
    return render_template('ask_question.html', form=form)


@app.route('/q/<qid>', methods=['GET', 'POST'])
def question(qid):
    q = get_request('q/' + qid)['question']
    form = AnswerArea()
    if form.validate_on_submit():
        content = form.area.data.strip()
        if content:
            post_request('a', {'content': content, 'question_id': qid, 'author_id': q['author_id']})
        return redirect(qid)
    return render_template('question.html', question=q,
                           answers=list(map(get_answer_by_id, q['answers'])), form=form)


@app.route('/me')
def profile():
    return render_template('profile.html', username=current_user.username)


@app.route('/latest')
def latest_redirect():
    return redirect('/')


if __name__ == '__main__':
    db_session.global_init('db/users.sqlite')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        from website.data.users import User
        return db_sess.query(User).get(user_id)

    app.register_blueprint(auth.auth)
    # app.run(port=80)
    serve(app, port=80)
