from flask import Flask, render_template, request, redirect, url_for, jsonify, session  # 导入Flask及其相关模块
from flask_sqlalchemy import SQLAlchemy  # 导入SQLAlchemy扩展
from sqlalchemy import Column, Integer, Text, String  # 导入SQLAlchemy的列类型
from sqlalchemy.dialects.postgresql import JSONB  # 导入PostgreSQL的JSONB类型
from datetime import datetime, timezone, timedelta  # 导入日期时间相关的模块
from sqlalchemy.sql import func, case  # 导入SQLAlchemy的函数和条件表达式

# app = Flask(__name__) 这行代码中，app 并不是自定义的名字，而是创建的 Flask 应用实例的一个常见命名习惯,可以自己命名其它名字
#__name__ 是 Python 中的一个特殊变量，表示当前模块的名称，通过它来确定根目录，正确加载文件
# Flask 是一个基于 WSGI（Web Server Gateway Interface）协议的 Web 框架，而 app 是 Flask 应用的核心入口点
# 没有flask实例，无法定义管理路由（如 @app.route()），无法app.config 设置应用的各种参数,无法接收 HTTP 请求
app = Flask(__name__)  # 创建Flask应用实例
#SQLALCHEMY_DATABASE_URI 用来指定数据库的连接信息,配置 SQLAlchemy 的数据库连接 URI（Uniform Resource Identifier），即告诉 Flask 应用如何连接到你的数据库。
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:!QAZ2wsx@localhost:5432/ceshi'  # 配置数据库URI
# 关闭 SQLAlchemy 的事件系统，以减少内存开销
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭跟踪修改
# Flask 应用设置一个密钥，用于保护会话（session）数据的安全性,会将用户的登录状态存储在会话中（通常是 Cookie 中）。如果没有 secret_key，这些数据可能会被恶意修改
app.secret_key = 'your_key_!@#123'  # 设置session密钥

#这行代码创建了一个 SQLAlchemy 类的实例 db，并将 Flask 应用实例 app 传递给它。这意味着 SQLAlchemy 现在知道如何与你的 Flask 应用进行交互，
# 包括如何读取配置（如数据库 URI）、如何处理应用上下文,db 对象提供了定义数据库模型的能力。你可以通过继承 db.Model 来创建与数据库表对应的 Python 类（即模型）
#db 对象还提供了对数据库执行各种操作的方法，比如添加、删除、修改数据以及查询数据
# db.session 是一个非常重要的属性，它代表当前数据库会话。通过这个会话，你可以将对象持久化到数据库中或者从数据库中检索对象
db = SQLAlchemy(app)  # 初始化SQLAlchemy



#############################################################################################
""" 模型的作用是将数据库中的表结构映射到 Python 类中，从而允许你以面向对象的方式操作数据库。这样做的主要目的是简化数据库操作
插入：new_user = UserRecord(username='john', email='john@example.com')   db.session.add(new_user) db.session.commit()
 更新：user = UserRecord.query.get(1)  user.email = 'new_email@example.com' db.session.commit()
 删除：user = UserRecord.query.get(1) db.session.delete(user) db.session.commit()

将name='张三', lx='现场'的第一条数据修改成王五，如果不是第一条，而是全部，就改成all.() 然后for users in user:  users.name = '王五'
try:
    user = UserRecord.query.filter_by(name='张三', lx='现场').first()
    if user:
        user.name = '王五'
        db.session.commit()
    else:
        print("未找到符合条件的用户")
except Exception as e:
    db.session.rollback()
    print(f"更新失败: {e}")
"""

class UserRecord(db.Model):  # 定义UserRecord模型
    __tablename__ = 'user_record'  # 表名

    id = db.Column(db.Integer, primary_key=True)  # 主键
    user_id = db.Column(db.String(50), nullable=False)  # 用户ID
    question_id = db.Column(db.Integer, nullable=False)  # 题目ID
    question_text = db.Column(db.String(500), nullable=False)  # 题目文本
    options = db.Column(db.JSON, nullable=False)  # 选项
    correct_answer = db.Column(db.String(10), nullable=False)  # 正确答案
    difficulty = db.Column(db.String(20))  # 难度
    category = db.Column(db.String(50))  # 类别
    beizhu = db.Column(db.String(200))  # 备注
    user_answers = db.Column(db.String(10), nullable=False)  # 用户答案
    submit_time = db.Column(db.DateTime, default=datetime.utcnow)  # 提交时间

class Question(db.Model):  # 定义Question模型
    __tablename__ = 'questions'  # 表名

    id = Column(Integer, primary_key=True)  # 主键
    question_text = Column(Text, nullable=False)  # 题目文本
    options = Column(JSONB, nullable=False)  # 选项
    correct_answer = Column(String(255), nullable=False)  # 正确答案
    difficulty = Column(String(50))  # 难度
    category = Column(String(255))  # 类别
    beizhu = Column(String(255))  # 备注

##################################################################################################
"""@app.route() 是一个装饰器，它被用来告诉 Flask 哪个 URL 应该触发下面的视图函数。
'/' 表示的是网站的根路径。当用户访问你的网站的基础 URL（例如 http://example.com/）时，Flask 就会调用紧跟在装饰器下面定义的函数
紧跟在 @app.route('/') 下面定义的 index 函数是一个视图函数。这个函数负责处理对应 URL 的请求，并返回响应给客户端（通常是网页内容、重定向等）
视图函数必须返回一个响应对象，它可以是一个字符串（直接作为 HTML 返回）、一个渲染后的模板或其他类型的响应
默认的 templates 文件夹中的文件，你需要告诉 Flask 在哪里找到这个 HTML 文件。Flask 默认会在 templates 文件夹中寻找模板文件，
因此如果你将文件放在其他目录（如 temp），需要手动指定路径
# 指定返回temp/index.html 的绝对路径
    file_path = '/path/to/your/project/temp/index.html'
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return Response(content, mimetype='text/html')
    
db.session.query	更通用，适合复杂的多表查询或跨模型查询	代码稍显冗长
Question.query	更简洁，直接与模型关联，适合单表查询	不适用于复杂的多表查询或跨模型查询    
    
"""
@app.route('/')  # 定义首页路由
def index():  # 首页视图函数
    categories = db.session.query(Question.category).distinct().all()  # 查询所有类别
    # 也可以换成categories = Question.query.with_entities(Question.category).distinct().all()   转成包含元组的列表，如[('数学',), ('语文',), ('英语',)]
    categories = [cat[0] for cat in categories]  # 提取类别名称 格式转换成 ['数学', '语文', '英语']

    colors = ["#ADD8E6","#9F5F9F","#87CEEB", "#42426F", "#000080", "#0047AB","#4169E1"]  # 定义颜色列表
    category_colors = {category: colors[i % len(colors)] for i, category in enumerate(categories)}  # 将类别与颜色一一对应，如果类别数量超过了颜色列表的长度，颜色会循环使用

    #render_template为flask函数，用于渲染模板，categories=categories 和 category_colors=category_colors）是传递给模板的数据。
    #这些数据可以在模板中通过变量名访问。
    return render_template('index.html', categories=categories, category_colors=category_colors)  # 渲染模板并传递数据

"""当用户访问指定的 URL（如 /add_question）时，Flask 会调用与该路径关联的视图函数
methods=['GET', 'POST']指定了该路由支持的 HTTP 请求方法。在这里，GET 和 POST 方法都被允许：GET：用于请求页面内容（如显示表单）。POST：用于提交数据（如通过表单提交题目信息）
GET 请求：
当用户访问 /add_question 页面时，浏览器会发送一个 GET 请求。
视图函数检测到请求方法是 GET，于是渲染并返回一个包含表单的 HTML 页面（如 add_question.html），供用户填写题目信息。
POST 请求：
当用户填写完表单并点击提交按钮时，浏览器会发送一个 POST 请求，将表单数据发送到服务器。
视图函数检测到请求方法是 POST，于是从请求中提取表单数据，并将其保存到数据库中
"""
@app.route('/add_question', methods=['GET', 'POST'])  # 定义添加题目路由
def add_question():  # 添加题目视图函数
    if request.method == 'POST':  # 如果请求方法为POST
        question_text = request.form.get('question_text')  # 获取题目文本

        #request.form.get('options') 从表单数据中获取名为 options 的字段值
        options_str = request.form.get('options')  # 获取选项字符串
        correct_answer = request.form.get('correct_answer')  # 获取正确答案
        difficulty = request.form.get('difficulty')  # 获取难度
        category = request.form.get('category')  # 获取类别
        beizhu = request.form.get('beizhu')  # 获取备注

        parsed_options = parse_options(options_str)  #使用下面的parse_options函数 解析选项字符串

        #将字段的值为这个，写入到数据库表中
        new_question = Question(
            question_text=question_text,
            options=parsed_options,
            correct_answer=correct_answer,
            difficulty=difficulty,
            category=category,
            beizhu=beizhu
        )
        db.session.add(new_question)  # 添加新题目到会话
        db.session.commit()  # 提交会话

        #jsonify() 是 Flask 提供的一个函数，用于将 Python 数据结构（如字典、列表等）转换为 JSON 格式的 HTTP 响应。
        return jsonify({'message': '题目已成功提交！'})  # 返回JSON响应
    else:  # 如果请求方法为GET
        categories = db.session.query(Question.category).distinct().all()  # 查询所有类别
        categories = [cat[0] for cat in categories]  # 提取类别名称

        colors = ["#ADD8E6", "#9F5F9F", "#87CEEB", "#42426F", "#000080", "#0047AB", "#4169E1"]  # 定义颜色列表
        category_colors = {category: colors[i % len(colors)] for i, category in enumerate(categories)}  # 将类别与颜色对应

    return render_template('index.html', categories=categories, category_colors=category_colors)  # 渲染模板并传递数据

"""匹配一个字母范围在 A-D 之间的字符（如 A、B、C、D）。
使用圆括号 () 表示捕获组，表示这部分内容会被提取出来作为匹配结果的一部分
\.  匹配一个点号 .  因为点号在正则表达式中有特殊含义，所以需要使用反斜杠 \ 转义  ([^A-D]+)匹配除 A-D 之外的一个或多个字符

"""
def parse_options(options_str):  # 解析选项字符串函数
    try:
        import re  # 导入正则表达式模块
        pattern = r'([A-D])\.([^A-D]+)'  # 定义正则表达式模式
        #该正则表达式会匹配形如 A. 答案内容 的字符串  re.findall() 方法查找所有符合正则表达式模式的子字符串
        #match 之后的值[('A', ' 选项一 '), ('B', ' 选项二 '), ('C', ' 选项三 '), ('D', ' 选项四 ')]
        matches = re.findall(pattern, options_str)  # 查找匹配项
        parsed_options = {}  # 初始化解析后的选项字典

        #遍历匹配项并处理，key.strip()，去掉选项标识符（如 A、B 等）前后的空白字符
        #value.strip() 去掉选项描述前后的空白字符， value.replace(':', '')： 去掉选项描述中的冒号（如果存在）
        for key, value in matches:  # 遍历匹配项
            value = value.strip().replace(':', '')  # 处理选项值
            #parsed_options[key.strip()] = value  将处理后的选项标识符和描述存入字典 将选项标识符作为键，选项描述作为值，存储到字典中
            parsed_options[key.strip()] = value  # 存储选项

        return parsed_options  # 返回解析后的选项
    except Exception as e:
        raise ValueError(f'选项格式错误，请按照 \'A.北京 B.天津 C.长沙 D.广州\' 的格式输入！ 错误信息: {str(e)}')  # 抛出异常

#上面统一返回index.html
########################################################
@app.route('/quiz')  # 定义测验路由
@app.route('/quiz/<category>/<difficulty>')  # 定义带参数的测验路由 <category> 和 <difficulty> 是路径参数，它们会被传递给视图函数
#用户访问 /quiz或者用户可以通过指定的分类和难度等级访问特定的测验内容 都可以进入下面的测验试图函数
def quiz(category=None, difficulty=None):  # 测验视图函数
    #使用 request.args.get() 方法从 URL 查询参数中获取名为 page 的参数值，用户没有提供 page 参数，则默认值为 1
    page = request.args.get('page', 1, type=int)  # 获取当前页码，默认为第一页，type=int 表示将获取的值转换为整数类型
    per_page = 5  # 每页显示的题目数量

    if category and difficulty:  # 如果提供了类别和难度
        if difficulty == "all":  # 如果难度为'all'
            query = Question.query.filter_by(category=category)  # 只按类别过滤
            #从题目列表中过滤出对应的数据出来
        else:  # 否则按类别和难度过滤
            query = Question.query.filter_by(category=category, difficulty=difficulty)
    else:  # 如果没有提供类别和难度
        query = Question.query  # 不做任何过滤

    # 分页查询
    #paginate() 是 SQLAlchemy 提供的一个分页方法，用于对查询结果进行分页。
    # paginate(当前页码，每页记录数量，请求超出范围空列表)改成true会报404错误
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    questions = pagination.items   #items 分页对象中的一个属性，表示当前页的所有记录（即当前页的数据）

    questions_data = [
        {
            "id": q.id,
            "question_text": q.question_text,
            "options": q.options,
            "correct_answer": q.correct_answer
        }
        for q in questions
    ]

    return render_template('quiz.html',
                           questions=questions_data,
                           category=category,
                           difficulty=difficulty,
                           pagination=pagination)


##########################################
@app.route('/get_challenge_records')  # 定义获取挑战记录路由 这个就是为了做一个表格
def get_challenge_records():  # 获取挑战记录视图函数
    try:
        records = (
            db.session.query(
                UserRecord.user_id,
                UserRecord.category,
                UserRecord.difficulty,
                ((func.sum(case((UserRecord.correct_answer == UserRecord.user_answers, 1), else_=0)) * 100).cast(db.Numeric) / func.count(1)).label('score'),
                UserRecord.submit_time
            )
            .group_by(UserRecord.user_id, UserRecord.category, UserRecord.difficulty, UserRecord.submit_time)
            .order_by(UserRecord.submit_time.asc())
            .all()
        )

 #目的是为了查出每次提交的时候的分数
#前面就是为了实现一个sql,select user_id,category,difficulty,submit_time,(case when correct_answer = user_answers then 1 else 0 end)::numeric/count(1)
#from user_record group by user_id,category,difficulty,submit_time order by submit_time
#        format_records 是一个函数，用于对从数据库或其他数据源获取的原始记录（records）进行格式化，records 是一个包含多条记录的列表或查询结果，
 #       format_records 函数可能将其转换为更适合前端使用的格式（例如将日期格式化为字符串、提取特定字段等）"""
        result = format_records(records)  # 格式化记录

        #jsonify 是 Flask 提供的一个函数，用于将 Python 数据结构（如字典、列表等）转换为 JSON 格式的 HTTP 响应
        #在这里，{'records': result} 是一个字典，其中 records 是键，result 是值（即格式化后的记录）
        #返回值如下{ "records": [  {"id": 1, "name": "Alice", "created_at": "2023-01-01"}, {"id": 2, "name": "Bob", "created_at": "2023-01-02"} ]}
        return jsonify({'records': result})  # 返回JSON响应
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # 返回错误信息

def format_records(records):  # 格式化记录函数
    result = []  # 初始化结果列表
    for record in records:  # 遍历记录
        score = float(record.score) if record and record.score is not None else 0.0  # 转换分数为浮点数
        result.append({
            'user_id': record.user_id,
            'category': record.category,
            'difficulty': record.difficulty,
            'score': score,
            'submit_time': record.submit_time.isoformat()
        })  # 构建结果字典
    return result  # 返回结果列表

@app.route('/get_wrong_records')  # 定义获取错误记录路由
def get_wrong_records():  # 获取错误记录视图函数
    records = (
        db.session.query(
            UserRecord.user_id,
            UserRecord.question_id,
            UserRecord.category,
            UserRecord.difficulty,
            UserRecord.user_answers,
            UserRecord.correct_answer,
            UserRecord.beizhu,
            UserRecord.submit_time
        )
        .filter(UserRecord.correct_answer != UserRecord.user_answers)
        .order_by(UserRecord.submit_time.asc())
        .all()
    )
#将查询出来的数据都返回，然后一条一套列出来
    result = [{
        'user_id': record.user_id,
        'question_id': record.question_id,
        'category': record.category,
        'difficulty': record.difficulty,
        'user_answers': record.user_answers,
        'correct_answer': record.correct_answer,
        'beizhu': record.beizhu,
        'submit_time': record.submit_time.isoformat()
    } for record in records]

    return jsonify({'records': result})  # 返回JSON响应
#和前面的区别是一个用了函数一个没用函数封装
#######################################################################

#当用户访问 /question/<question_id> 时，Flask 会调用这个函数
@app.route('/question/<int:question_id>')  # 定义单个题目路由
def question(question_id):  # 单个题目视图函数
    question = Question.query.get_or_404(question_id)  # 获取题目或返回404,query.get_or_404(question_id) 是 SQLAlchemy 提供的一个便捷方法
    #找到了对应的记录，则返回该记录否则返回404错误
    #渲染一个 HTML 模板并将其返回给客户端（浏览器），'single_question.html' 是模板文件的名称，通常位于 templates 文件夹中
    #question=question 将查询到的题目对象传递给模板，模板可以使用该对象的数据来动态生成 HTML 内容。
    return render_template('single_question.html', question=question)  # 渲染模板并传递数据

@app.route('/submit_single', methods=['POST'])  # 定义提交单题答案路由
def submit_single():  # 提交单题答案视图函数
    user_answers = request.form.to_dict()  # 获取用户答案
   #可以一个字段一个字段获取，也可以获取全部  options_str = request.form.get('options')
    #当网页上的表单通过 POST 方法提交时，这些数据可以通过 request.form 访问，to_dict() 方法将 request.form 转换为一个标准的 Python 字典。这意味着你可以方便地对提交的数据进行操作，比如遍历、修改
    #pop('question_id') 方法从 user_answers 字典中移除键 'question_id' 并返回其对应的值。这里假设用户提交的答案中包含了一个名为 'question_id' 的字段，用于标识特定的问题
    question_id = int(user_answers.pop('question_id'))  # 获取题目ID
    question = Question.query.get_or_404(question_id)  # 获取题目或返回404

    #str(question_id): 将 question_id 转换为字符串类型。这是因为 user_answers 的键是字符串形式的问题ID，而 question_id 可能是以整数形式存储的。通过将其转换为字符串，确保可以正确匹配字典中的键
    #.get(str(question_id), ''): 使用字典的 get 方法来查找与 str(question_id) 对应的值（即用户对该问题的回答）。如果找不到对应的问题ID（也就是说，字典中没有这个键），则返回第二个参数 '' 作为默认值，这里是一个空字符串
    user_answer = user_answers.get(str(question_id), '')  # 获取用户对当前题目的答案，用question_id匹配一个键，按钮点击
    correct_answer = question.correct_answer  # 获取题目正确答案

    user_id = session.get('user_id', 'guest')  # 获取当前用户ID，默认为'guest'
    if user_answer == correct_answer:  # 如果用户答案正确
        result_message = "回答正确！"  # 设置结果消息
    else:  # 如果用户答案错误
        result_message = f"回答错误！正确答案是 {correct_answer} - {question.options[correct_answer]}"  # 设置结果消息

    return render_template('result_single.html', message=result_message, beizhu=question.beizhu)  # 渲染模板并传递数据


@app.route('/submit', methods=['POST'])  # 定义提交答案路由
def submit():  # 提交答案视图函数
    user_answers = request.form.to_dict()  # 获取用户答案
    category = request.form.get('category')  # 获取类别
    difficulty = request.form.get('difficulty')  # 获取难度

    total = 0  # 初始化总题目数
    correct = 0  # 初始化正确题目数
    wrong_questions = []  # 初始化错误题目列表

    #因为只有难度有所有的选项，通过用户选的难度和题目分类选择对应的题目
    if difficulty == "all":  # 如果难度为'all'
        all_questions = Question.query.filter_by(category=category).all()  # 按类别过滤所有题目
    else:  # 否则按类别和难度过滤所有题目
        all_questions = Question.query.filter_by(category=category, difficulty=difficulty).all()

    user_id = session.get('user_id', 'guest')  # 获取当前用户ID，默认为'guest'

    for question in all_questions:  # 遍历所有题目
        total += 1  # 增加总题目数
        q_id = str(question.id)  # 获取题目ID
        user_answer = user_answers.get(q_id, '')  # 获取用户对当前题目的答案

        #这里相当于指定了表
        record = UserRecord(
            user_id=user_id,
            question_id=question.id,
            question_text=question.question_text,
            options=question.options,
            correct_answer=question.correct_answer,
            difficulty=question.difficulty,
            category=question.category,
            beizhu=question.beizhu,
            user_answers=user_answer,
            submit_time=datetime.now(timezone(timedelta(hours=8)))
        )
        db.session.add(record)  # 添加记录到会话 调用 .add() 方法时，SQLAlchemy 将该对象标记为“待插入”，意味着在下一次提交会话时，它会被插入到相应的数据库表中

        if user_answer == question.correct_answer:  # 如果用户答案正确
            correct += 1  # 增加正确题目数
        else:  # 如果用户答案错误
            wrong_questions.append({
                'question_text': question.question_text,
                'user_answer': user_answer,
                'correct_answer': question.correct_answer,
                'beizhu': question.beizhu,
                'options': question.options
            })  # 记录错误题目信息
    db.session.commit()  # 提交会话

    score = (correct / total) * 100 if total != 0 else 0  # 计算分数
    return render_template('result.html',
                           score=score,
                           wrong_questions=wrong_questions)  # 渲染模板并传递数据





if __name__ == '__main__':  # 如果直接运行此脚本
    with app.app_context():  # 使用应用上下文
        db.create_all()  # 创建所有表
    # app.run() 就是调用 Flask 实例的方法来启动服务器。没有实例，就无法启动服务器
    app.run(debug=True)  # 运行应用，开启调试模式



