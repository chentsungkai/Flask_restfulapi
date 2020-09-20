from flask import Flask  , jsonify , request , render_template , flash , redirect , url_for
from flask_restful import Api,Resource , reqparse , abort , marshal_with , fields
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField , TextField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Email,Length,EqualTo,ValidationError
from flask_bootstrap import Bootstrap





app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '966a98e7b6fd851217f6f90db9f0e1da'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

class UserInfo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user = db.Column(db.String,unique=True,nullable=False)
    email = db.Column(db.String,unique=True,nullable=False)
    password = db.Column(db.String,nullable=False)

db.create_all()

class VideoModel(db.Model):
    id  = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable = False )
    view = db.Column(db.Integer,nullable = False)
    likes = db.Column(db.Integer,nullable = False)


    def __repr__(self):
        return "video (name={name},view={view},likes={likes})"


#####  註冊表單  #####
class RegisterForm(FlaskForm):
    user = StringField('name',validators=[DataRequired(),Length(min=2,max=15)])
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired(),])
    confirm_password = PasswordField('confirm_password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self,email):
        check_mail = UserInfo.query.filter_by(email=email.data).first()
        if check_mail:
            raise ValidationError('Email already taken')
    def validate_user(self,user):
        check_user = UserInfo.query.filter_by(user=user.data).first()
        if check_user:
            raise ValidationError('user name is taken')


#####  登入表單  #####
class LoginForm(FlaskForm):
    email = StringField('email',validators=[DataRequired(),Email()])
    password = PasswordField('password',validators=[DataRequired()])
    submit = SubmitField('Login')



resource_filed = {
    'id':fields.Integer,
    'name':fields.String,
    'view':fields.Integer,
    'likes':fields.Integer
}



video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name",type=str,help="Name of video not found",required=True)
video_put_args.add_argument("view",type=int,help="View of video not found",required=True)
video_put_args.add_argument("likes",type=int,help="Likes of video not found",required=True)

video_update_args = reqparse.RequestParser()
video_update_args.add_argument("name",type=str,help="Name of video not found")
video_update_args.add_argument("view",type=int,help="View of video not found")
video_update_args.add_argument("likes",type=int,help="Likes of video not found")


##### 網址 #####

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html' , page_title='Home sweet home')

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        password_hash = Bcrypt.generate_password_hash('form.password.data').decode('uft-8')
        user_data = UserInfo(user=form.user.data,email=form.email.data,password=form.password_hash)
        db.session.add(user_data)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html',page_title="Register page",form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = UserInfo.query.filter_by(email=form.email.data).first()
        validate_pass = Bcrypt.check_password_hash(user.password,form.password.data) ##question

        if user and validate_pass :
            flash(f'Login Successful')
            return redirect(url_for('home'))
        else:
            flash(f'Email or password invaild')
            return redirect(url_for('home'))
    return render_template('Login.html',page_title="Login",form=form)


@marshal_with(resource_filed)
def video_not_exist(video_id):
    global result
    args = video_update_args.parse_args()
    result = VideoModel.query.filter_by(id=video_id).first()
    if not result:
        abort(409,message="video not found , can't delete ")

class video(Resource):
    @marshal_with(resource_filed)
    def get(self,video_id):
        result = VideoModel.query.filter_by(id=video_id).first()
        return result

    @marshal_with(resource_filed)
    def put(self,video_id):
        args = video_put_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if result:
            abort(409,message="video id taken")

        video = VideoModel(id=video_id,name=args['name'],view=args['view'],likes=args['likes'])
        db.session.add(video)
        db.session.commit()
        return video,201

    @marshal_with(resource_filed)
    def patch(self,video_id):
        args = video_update_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(409,message="video not exist,can't update")

        if args['name']:
            result.name = args['name']
        if args['view']:
            result.view = args['view']
        if args['likes']:
            result.likes= args['likes']

        db.session.commit()

        return result

    def delete(self,video_id):
        video_not_exist(video_id)
        db.session.delete(result)
        db.session.commit()
        return '',204

api.add_resource(video, "/video/<int:video_id>")


if __name__ == "__main__":
    app.run(debug=True)