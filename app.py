from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Questions(db.Model):
    __tablename__ = "questions"  # таблица будет создана здесь же искусственно

    tag = db.Column(db.Text, primary_key=True)
    question = db.Column(db.Text)


class Usermeta(db.Model):
    __tablename__ = "meta"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rus = db.Column(db.Text)
    age = db.Column(db.Integer)
    accept = db.Column(db.Text)


class Answers(db.Model):
    __tablename__ = "answers"

    user_id = db.Column(db.Integer, primary_key=True)
    gram = db.Column(db.Text)
    mean = db.Column(db.Text)
    differ = db.Column(db.Text)


db.create_all()


try:  # таблица может быть заполнена только один раз, если это первый, то она заполнится, если нет - pass
    tag1 = 'gram'
    tag2 = 'mean'
    tag3 = 'differ'

    question1 = 'Считаете ли вы словосочетание "заклятые друзья" приемлемым с точки зрения русского языка?'
    question2 = 'Как вам кажется, что оно может значить?'
    question3 = 'Есть ли для вас разница между употреблением этого словосочетания в кавычках и без?'

    q1 = Questions(tag=tag1, question=question1)
    db.session.add(q1)

    q2 = Questions(tag=tag2, question=question2)
    db.session.add(q2)

    q3 = Questions(tag=tag3, question=question3)
    db.session.add(q3)

    db.session.commit()

except:
    pass


@app.route('/')  # главная страница
def index():
    return render_template("index.html")


@app.route('/form')  # форма
def form():
    return render_template("form.html")


@app.route('/thankyou')  # слайд с благодарностью
def thankyou():
    return render_template("thankyou.html")


@app.route('/process', methods=['get'])  # процесс обработки результата
def answer_process():
    if not request.args:
        return redirect(url_for('form'))

    rus = request.args.get('rus')
    age = request.args.get('age')
    accept = request.args.get('accept')

    meta = Usermeta(age=age, rus=rus, accept=accept)
    db.session.add(meta)
    db.session.commit()
    db.session.refresh(meta)

    gram = request.args.get('gram')
    mean = request.args.get('mean')
    differ = request.args.get('differ')

    answers = Answers(user_id=meta.user_id, gram=gram, mean=mean, differ=differ)
    db.session.add(answers)
    db.session.commit()

    return redirect(url_for('thankyou'))  # направляем на страницу благодарности


@app.route('/statistics')  # статистика
def statistics():
    all_info = {}

    all_info['age_mean'] = db.session.query(func.avg(Usermeta.age)).one()[0]
    all_info['total_count'] = Usermeta.query.count()
    all_info['gram_number'] = Answers.query.filter_by(gram='yes').count()
    all_info['gram_percentage'] = str(all_info['gram_number']/all_info['total_count']*100) + '%'

    return render_template('statistics.html', all_info=all_info)


if __name__ == '__main__':
    app.run()